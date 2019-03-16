import json
from typing import List, Optional, Tuple

import arrow
from chupacabra_client.protos import game_structs_pb2
import numpy as np

from dbs.redis_cache import RedisCacheHandler
from game_server.game_servicer import GameImplementation
from protos import game_server_pb2
from tic_tac_toe import tic_tac_toe
from tic_tac_toe.config import get_redis_handler
from tic_tac_toe import description


TTT_MOVE_BLOCK_TIME = 1  # in seconds
TTT_REQUEST_BLOCK_TIME = 1  # in seconds
GAME_PERSISTENCE_TIME = 15 * 60  # 15 minutes - redis time
REQUEST_LIFETIME = 60  # 1 minutes
QUEUE_LIFETIME = 90  # 1.5 minutes
GAME_PADDED_LIFETIME = GAME_PERSISTENCE_TIME + tic_tac_toe.GAME_LIFETIME

MAX_REQUEST_VALUE = 2000000000
MAX_REQUEST_ID_ATTEMPTS = 10


def _make_validation_key(game_id: str) -> str:
    """Make the redis key for game validation."""
    return 'ttt:{}:valid'.format(game_id)


def _make_state_key(game_id: str) -> str:
    """Make the redis key for the game state."""
    return 'ttt:{}.state'.format(game_id)


def _make_state_lock_key(game_id: str) -> str:
    """Make the redis key for locking the game state."""
    return 'ttt:{}.state_lock'.format(game_id)


def _make_request_key(request_id: str, player_id: str) -> str:
    """Make the redis key for a game request lock."""
    return 'ttt:{}:{}.request'.format(request_id, player_id)


def _make_request_lock_key(request_id: str, player_id: str) -> str:
    """Make the redis key for locking a game request lock."""
    return 'ttt:{}:{}.request_lock'.format(request_id, player_id)


REQUEST_QUEUE_KEY = 'ttt:requests'
REQUEST_QUEUE_LOCK_KEY = 'ttt:requests_lock'


def _validate_game(
    game_id: str, player_id: str, redis_handler: RedisCacheHandler
) -> bool:
    """Validate that the player has access to this game"""
    key = _make_validation_key(game_id)
    data = redis_handler.get(key)
    if data is None:
        return False

    deserialized_data = json.loads(data)
    if not isinstance(deserialized_data, list):
        raise AssertionError('Malformed tictactoe game metadata.')
    if player_id in deserialized_data:
        return True
    return False


def _get_game_state(
    game_id: str, player_id: str, redis_handler: RedisCacheHandler
) -> Tuple[str, Optional[tic_tac_toe.TicTacToeInternalState], bool]:
    """Get the game state without locking anything."""
    validated = _validate_game(game_id, player_id, redis_handler)
    if validated is False:
        message = 'Cannot find game of the given id for the given user'
        return message, None, False

    state_key = _make_state_key(game_id)
    state = redis_handler.get(state_key)
    if state is None:
        message = 'Game data not found.'
        return message, None, False

    internal_state = tic_tac_toe.deserialize_state(state)
    time_now = arrow.utcnow().float_timestamp
    if (
        time_now > internal_state.turn_expiration_time and
        internal_state.turn_expiration_time <= internal_state.game_expiration_time
    ):
        internal_state.mode = tic_tac_toe.FINISHED_MODE
        internal_state.winner = (internal_state.turn + 1) % 2
        save_new_state = True
    elif time_now > internal_state.game_expiration_time:
        internal_state.mode = tic_tac_toe.FINISHED_MODE
        internal_state.winner = -1
        save_new_state = True
    else:
        save_new_state = False
    message = 'Success'
    return message, internal_state, save_new_state


def _make_game_piece(
    piece_id: str,
    name: str,
    player: str,
    x_coord: int,
    y_coord: int
) -> game_structs_pb2.GamePiece:
    piece = game_structs_pb2.GamePiece(
        id=piece_id,
        name=name,
        player=player,
        location=game_structs_pb2.Coordinates(
            name='location',
            values=[
                game_structs_pb2.Coordinate(
                    name='x',
                    value=x_coord
                ),
                game_structs_pb2.Coordinate(
                    name='y',
                    value=y_coord
                ),
            ]
        )
    )
    return piece


def _make_game_board(
    board: np.ndarray,
    players: List[game_structs_pb2.PlayerInfo]
) -> game_structs_pb2.GameBoard:
    """Create the game board."""
    pieces = []
    for idx in range(3):
        for jdx in range(3):
            state = board[idx, jdx]
            if state == tic_tac_toe.TURN_SCORES[0]:
                piece = _make_game_piece('x', 'X', players[0].name, idx, jdx)
            elif state == tic_tac_toe.TURN_SCORES[1]:
                piece = _make_game_piece('o', 'O', players[1].name, idx, jdx)
            else:
                continue
            pieces.append(piece)

    board = game_structs_pb2.GameBoard(
        id='0',
        name='Game Board',
        type='2d-board',
        pieces=pieces
    )
    return board


SCORE_COMMENTS = {
    'lose': 'You lose! Too bad. Keep trying',
    'win': 'You win! Great job!',
    'tie': 'Tie!'
}

SCORES = {
    'lose': -1,
    'win': 1,
    'tie': 0
}


def _get_game_status(
    mode: str,
    winner: int,
    players: List[game_structs_pb2.PlayerInfo]
) -> List[game_structs_pb2.GameScore]:
    if mode == tic_tac_toe.PLAY_MODE:
        scores = [
            game_structs_pb2.GameScore(
                player_name=player.username,
                comment='Game not yet finished.'
            )
            for player in players
        ]
        status = 'not finished'
        comment = 'Keep playing'
    elif mode == tic_tac_toe.FINISHED_MODE:
        if winner == -1:
            statuses = {
                player.username: 'tie'
                for player in players
            }
        else:
            statuses = {
                player.username: 'win' if winner == idx else 'lose'
                for idx, player in enumerate(players)
            }
        scores = [
            game_structs_pb2.GameScore(
                player_name=username,
                score_type='int',
                int_score=SCORES[status],
                comment=SCORE_COMMENTS[status]
            )
            for username, status in statuses.items()
        ]
        status = 'finished'
        comment = 'Game Over'
    else:
        raise AssertionError('Illegal game mode "{}".'.format(mode))

    game_status = game_structs_pb2.GameStatus(
        status=status,
        comment=comment,
        scores=scores
    )
    return game_status


def _convert_to_status_response(
    player_id: str,
    success_message: str,
    internal_state: tic_tac_toe.TicTacToeInternalState
) -> game_structs_pb2.GameStatusResponse:
    board = _make_game_board(internal_state.board, internal_state.players)
    current_player = internal_state.players[internal_state.turn].id
    if (
        internal_state.mode == tic_tac_toe.PLAY_MODE and
        current_player == player_id
    ):
        legal_moves = [description.PLACE_MARK_DESCRIPTION.name]
    else:
        legal_moves = []

    status = _get_game_status(
        internal_state.mode, internal_state.winner, internal_state.players)

    state = game_structs_pb2.GameState(
        status=status,
        boards=[board],
        mode=internal_state.mode,
    )

    status_info = game_structs_pb2.GameStatusInfo(
        id=internal_state.id,
        players=internal_state.players,
        state=state,
        legal_moves=legal_moves
    )

    response = game_structs_pb2.GameStatusResponse(
        success=True,
        message=success_message,
        status_info=status_info
    )
    return response


def _generate_request_id(
    handler: RedisCacheHandler,
    player_id: str,
    random_state: np.random.RandomState
) -> Optional[str]:
    """Generate a request id"""
    request_id = None
    for _ in range(MAX_REQUEST_ID_ATTEMPTS):
        proposed_request_id = str(random_state.randint(1, MAX_REQUEST_VALUE))
        request_key = _make_request_key(proposed_request_id, player_id)
        existing_data = handler.get(request_key)
        if existing_data is None:
            request_id = proposed_request_id

    return request_id


def _generate_game_id(
    handler: RedisCacheHandler,
    random_state: np.random.RandomState
) -> Optional[str]:
    """Generate a game id"""
    game_id = None
    for _ in range(MAX_REQUEST_ID_ATTEMPTS):
        proposed_game_id = str(random_state.randint(1, MAX_REQUEST_VALUE))
        game_key = _make_state_key(proposed_game_id)
        existing_data = handler.get(game_key)
        if existing_data is None:
            game_id = proposed_game_id

    return game_id


def request_game(
    request: game_server_pb2.GameRequest
) -> game_structs_pb2.GameRequestResponse:
    """Request a game."""
    handler = get_redis_handler()

    # Set a random number seed based on the fractional second part
    # of the timestamp. This makes it more reliable on higher loads compared
    # to the integer utc timestamp.
    time_now = arrow.utcnow().float_timestamp
    seed = int(time_now * 1e9) % 1000000000
    random_state = np.random.RandomState(seed)

    # Lock the requests
    with handler.lock(REQUEST_QUEUE_LOCK_KEY, TTT_REQUEST_BLOCK_TIME):
        # Generate a request id
        request_id = _generate_request_id(handler, request.player_id, random_state)
        if request_id is None:
            return game_structs_pb2.GameRequestResponse(
                success=False,
                message='Unable to request a game.'
            )
        request_key = _make_request_key(request_id, request.player_id)

        # Get the request queue
        queue_data = handler.get(REQUEST_QUEUE_KEY)
        if queue_data is not None and len(queue_data) > 0:
            request_queue = json.loads(queue_data)
            # Check expiration times
            valid_requests = [
                game_request
                for game_request in request_queue
                if game_request['expiration'] < time_now
            ]
            # Check if the current user is in the queue (slow -- need better method to do this)
            for game_request in valid_requests:
                if game_request['player_id'] == request.player_id:
                    return game_structs_pb2.GameRequestResponse(
                        success=False,
                        message='You already have a request in the queue.',
                        request_id=game_request['request_id']
                    )

            # Generate game id
            game_id = _generate_game_id(handler, random_state)

            if game_id is None:
                return game_structs_pb2.GameRequestResponse(
                    success=False,
                    message='Unable to request a game.'
                )

            # Grab the first element
            matched_player_request = valid_requests[0]
            remaining_requests = valid_requests[1:]
            matched_player_info = game_structs_pb2.PlayerInfo(
                username=matched_player_request['username'],
                nickname=matched_player_request['nickname'],
                team=matched_player_request['team'],
                level=matched_player_request['level']
            )
            matched_player_id = matched_player_request['player_id']
            matched_request_id = matched_player_request['id']

            # Randomized starting player
            if random_state.randint(2) == 0:
                player_ids = [request.player_id, matched_player_id]
                player_info = [request.player_info, matched_player_info]
            else:
                player_ids = [matched_player_id, request.player_id]
                player_info = [matched_player_info, request.player_info]

            # initialize the state
            game_state = tic_tac_toe.TicTacToeInternalState(
                game_id,
                player_ids,
                player_info,
                tic_tac_toe.TURN_EXPIRATION_TIME,
                tic_tac_toe.GAME_LIFETIME
            )
            serialized_state = tic_tac_toe.serialize_state(game_state)

            # Now we want to set:
            # 1) the queue
            # 2) the game
            # 3) the request
            # The idea for this order is to prevent a request from
            # generating multiple games (easier to have it just fail)
            # and also to prevent a request from getting assigned
            # a bad game.
            # Unfortunately, redis does not allow for a multiset
            # with different expirations

            # Save the queue:
            serialized_queue = json.dumps(remaining_requests)
            handler.set(
                REQUEST_QUEUE_KEY,
                serialized_queue,
                lifetime=QUEUE_LIFETIME
            )

            # Save the game:
            game_key = _make_state_key(game_id)
            handler.set(game_key, serialized_state, lifetime=GAME_PERSISTENCE_TIME)

            # Save the request
            serialized_request = json.dumps({
                'player': request.player_id,
                'game': game_id
            })
            handler.set(request_key, serialized_request, lifetime=REQUEST_LIFETIME)
            matched_request_key = _make_request_key(
                matched_request_id, matched_player_id)
            serialized_matched_request = json.dumps({
                'player': matched_player_id,
                'game': game_id
            })
            handler.set(
                matched_request_key,
                serialized_matched_request,
                lifetime=REQUEST_LIFETIME
            )

            response = game_structs_pb2.GameRequestResponse(
                success=True,
                message='Found game',
                request_id=request_id,
                game_id=game_id
            )

        else:  # The queue is empty
            queue_request = {
                'id': request_id,
                'player_id': request.player_id,
                'username': request.player_info.username,
                'nickname': request.player_info.nickname,
                'level': request.player_info.level,
                'team': request.player_info.team
            }
            serialized_request = json.dumps(queue_request)
            serialized_queue = json.dumps([queue_request])
            # Save the request first then the queue
            handler.set(
                request_key,
                serialized_request,
                lifetime=REQUEST_LIFETIME
            )

            handler.set(
                REQUEST_QUEUE_KEY,
                serialized_queue,
                lifetime=QUEUE_LIFETIME
            )

            response = game_structs_pb2.GameRequestResponse(
                success=True,
                message='Added request to queue',
                request_id=request_id
            )

    return response


def check_game_request(
    request: game_server_pb2.GameRequestStatusRequest
) -> game_structs_pb2.GameRequestStatusResponse:
    """Check if the request has been completed."""
    # Check if the request --> game mapping has been found
    redis_handler = get_redis_handler()
    key = _make_request_key(request.request_id, request.player_id)
    data_string = redis_handler.get(key)
    if data_string is None:
        message = 'Game request not found.'
        success = False
        game_id = None
    else:
        data = json.loads(data_string)
        # Verify the ID
        if data['player'] != request.player_id:
            message = 'Game request not found.'
            success = False
            game_id = None

        else:
            game_id = data.get('game')
            success = True
            if game_id is None:
                message = 'Game found.'
            else:
                message = 'Game not initialized yet.'

    if game_id is None:
        response = game_structs_pb2.GameRequestStatusResponse(
            success=success,
            message=message,
            game_found=False
        )
    else:
        response = game_structs_pb2.GameRequestStatusResponse(
            success=success,
            message=message,
            game_found=True,
            game_id=game_id
        )

    return response


def describe_game() -> game_structs_pb2.GameDescription:
    """Describe this game."""
    game_description = game_structs_pb2.GameDescription(
        name=description.TIC_TAC_TOE_NAME,
        description=description.TIC_TAC_TOE_DESCRIPTION
    )
    return game_description


def describe_moves() -> game_structs_pb2.GameMovesResponse:
    """Describe the game moves"""
    game_moves = game_structs_pb2.GameMovesResponse(
        moves=description.TIC_TAC_TOE_MOVES
    )
    return game_moves


def make_move(
    request: game_server_pb2.MoveRequest
) -> game_structs_pb2.GameStatusResponse:
    """Make a move."""
    handler = get_redis_handler()
    validated = _validate_game(
        request.game_id,
        request.player_id,
        handler
    )

    if validated is False:
        response = game_structs_pb2.GameStatusResponse(
            success=False,
            message='Cannot find game of this id for this user.'
        )
        return response

    # Lock the state so that we can make a move
    lock_key = _make_state_lock_key(request.game_id)
    with handler.lock(lock_key, blocking_timeout=TTT_MOVE_BLOCK_TIME):
        # Now grab the state from redis
        state_key = _make_state_key(request.game_id)
        state = handler.get(state_key)
        if state is None:
            not_found_response = game_structs_pb2.GameStatusResponse(
                success=False,
                message='Game data not found.'
            )
            return not_found_response

        internal_state = tic_tac_toe.deserialize_state(state)

        # Make the move
        message, new_state = tic_tac_toe.make_move(
            internal_state, request.move
        )

        # If the move was successful, write back into redis and release lock
        if new_state is not None:
            serialized_state = tic_tac_toe.serialize_state(new_state)
            handler.set(state_key, serialized_state)
        else:
            new_state = internal_state

    # craft and return the correct response
    response = _convert_to_status_response(request.player_id, message, new_state)
    return response


def get_game_status(
    request: game_server_pb2.UserGameInfo
) -> game_structs_pb2.GameStatusResponse:
    """Get the current status of the game."""
    handler = get_redis_handler()
    lock_key = _make_state_lock_key(request.game_id)
    with handler.lock(lock_key, TTT_MOVE_BLOCK_TIME):
        message, internal_state, save_new_state = _get_game_state(
            request.game_id,
            request.player_id,
            handler
        )
        if save_new_state:
            serialized_state = tic_tac_toe.serialize_state(internal_state)
            state_key = _make_state_key(request.game_id)
            timestamp = arrow.utcnow().timestamp
            state_lifetime = (
                internal_state.game_expiration_time - timestamp + GAME_PADDED_LIFETIME)
            handler.set(state_key, serialized_state, lifetime=state_lifetime)

    if internal_state is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=message
        )

    success_message = 'Success'
    response = _convert_to_status_response(
        request.player_id,
        success_message,
        internal_state
    )
    return response


def get_legal_moves(
    request: game_server_pb2.UserGameInfo
) -> game_structs_pb2.LegalMovesResponse:
    """Get all the possible moves the player can make at the current time."""
    handler = get_redis_handler()
    lock_key = _make_state_lock_key(request.game_id)
    with handler.lock(lock_key, TTT_MOVE_BLOCK_TIME):
        message, internal_state, save_new_state = _get_game_state(
            request.game_id,
            request.player_id,
            handler
        )
        if save_new_state:
            serialized_state = tic_tac_toe.serialize_state(internal_state)
            state_key = _make_state_key(request.game_id)
            timestamp = arrow.utcnow().timestamp
            state_lifetime = (
                internal_state.game_expiration_time - timestamp + GAME_PADDED_LIFETIME)
            handler.set(state_key, serialized_state, lifetime=state_lifetime)

    if internal_state is None:
        return game_structs_pb2.LegalMovesResponse(
            success=False,
            message=message
        )

    # Check if the game is finished
    if internal_state.mode == tic_tac_toe.FINISHED_MODE:
        return game_structs_pb2.LegalMovesResponse(
            success=True,
            message='Game is over. No moves available.'
        )

    # Check if it's the player's turn
    current_player_id = internal_state.players[internal_state.turn].id
    if request.player_id != current_player_id:
        return game_structs_pb2.LegalMovesResponse(
            success=True,
            message='It is not your turn to move.'
        )

    # The requesting player can now move
    return game_structs_pb2.LegalMovesResponse(
        success=True,
        message='It is your turn to move.',
        moves=[description.PLACE_MARK_DESCRIPTION.name]
    )


def forfeit_game(
    request: game_server_pb2.UserGameInfo
) -> game_structs_pb2.GameStatusResponse:
    """Forfeit the game."""
    handler = get_redis_handler()
    validated = _validate_game(
        request.game_id,
        request.player_id,
        handler
    )

    if validated is False:
        response = game_structs_pb2.GameStatusResponse(
            success=False,
            message='Cannot find game of this id for this user.'
        )
        return response

    # Lock the state so that we can make a move
    lock_key = _make_state_lock_key(request.game_id)
    with handler.lock(lock_key, blocking_timeout=TTT_MOVE_BLOCK_TIME):
        # Now grab the state from redis
        state_key = _make_state_key(request.game_id)
        state = handler.get(state_key)
        if state is None:
            not_found_response = game_structs_pb2.GameStatusResponse(
                success=False,
                message='Game data not found.'
            )
            return not_found_response

        internal_state = tic_tac_toe.deserialize_state(state)
        internal_state.mode = tic_tac_toe.FINISHED_MODE
        winner_idx = None
        for idx, player_id in enumerate(internal_state.player_ids):
            if player_id != request.player_id:
                winner_idx = idx
                break

        if winner_idx is None:
            raise AssertionError('Could not find the winning player.')

        internal_state.winner = winner_idx
        success_message = 'Success. You have forfeited the game.'
        response = _convert_to_status_response(
            request.player_id,
            success_message,
            internal_state
        )
        return response


def make_tic_tac_toe_implementation() -> GameImplementation:
    """Get the game implementation for tic tac toe"""
    implementation = GameImplementation(
        request_game_function=request_game,
        check_game_request_function=check_game_request,
        describe_game_function=describe_game,
        describe_moves_function=describe_moves,
        make_move_function=make_move,
        get_game_status_function=get_game_status,
        get_legal_moves_function=get_legal_moves,
        forfeit_game_function=forfeit_game
    )
    return implementation
