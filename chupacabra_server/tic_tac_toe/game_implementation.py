import json
from typing import List, Optional, Tuple

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
GAME_EXPIRATION_TIME = 30 * 60  # 30 minutes
MOVE_EXPIRATION_TIME = 2 * 60  # 2 minutes


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
) -> Tuple[str, Optional[tic_tac_toe.TicTacToeInternalState]]:
    """Get the game state without locking anything."""
    validated = _validate_game(game_id, player_id, redis_handler)
    if validated is False:
        message = 'Cannot find game of the given id for the given user'
        return message, None

    state_key = _make_state_key(game_id)
    state = redis_handler.get(state_key)
    if state is None:
        message = 'Game data not found.'
        return message, None

    internal_state = tic_tac_toe.deserialize_state(state)
    message = 'Success'
    return message, internal_state


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
                player_name=player.name,
                comment='Game not yet finished.'
            )
            for player in players
        ]
        status = 'not finished'
        comment = 'Keep playing'
    elif mode == tic_tac_toe.FINISHED_MODE:
        if winner == -1:
            statuses = {
                player.name: 'tie'
                for player in players
            }
        else:
            statuses = {
                player.name: 'win' if winner == idx else 'lose'
                for idx, player in enumerate(players)
            }
        scores = [
            game_structs_pb2.GameScore(
                player_name=name,
                score_type='int',
                int_score=SCORES[status],
                comment=SCORE_COMMENTS[status]
            )
            for name, status in statuses.items()
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

    players = [
        game_structs_pb2.PlayerInfo(
            name=player.name,
            level=player.level,
            team=player.team,
        )
        for player in internal_state.players
    ]

    status = _get_game_status(
        internal_state.mode, internal_state.winner, internal_state.players)

    state = game_structs_pb2.GameState(
        status=status,
        boards=[board],
        mode=internal_state.mode,
    )

    status_info = game_structs_pb2.GameStatusInfo(
        id=internal_state.id,
        players=players,
        state=state,
        legal_moves=legal_moves
    )

    response = game_structs_pb2.GameStatusResponse(
        success=True,
        message=success_message,
        status_info=status_info
    )
    return response


def request_game(
    request: game_server_pb2.GameRequest
) -> game_server_pb2.GameResponse:
    """Request a game."""
    # Lock the requests
    # TODO: implement
    # Idea:
    # 1) Check if the queue is populated with active requests
    # 2) check if the user has a request in the queue
    # 2a) if yes, fail
    # 2b) if no, continue
    # 3) if queue has requests: make a game and set request --> game mappings
    # 4) if not, add user to the queue along with an expiration time
    raise NotImplementedError()


def check_game_request(
    request: game_server_pb2.GameRequestStatusRequest
) -> game_server_pb2.GameResponse:
    """Check if the request has been completed."""
    # Check if the request --> game mapping has been found
    raise NotImplementedError()


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
    message, internal_state = _get_game_state(
        request.game_id,
        request.player_id,
        handler
    )

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
    message, internal_state = _get_game_state(
        request.game_id,
        request.player_id,
        handler
    )

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
        for idx, player in enumerate(internal_state.players):
            if player.id != request.player_id:
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
