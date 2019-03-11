import json
from typing import Optional, Tuple

from chupacabra_client.protos import game_structs_pb2

from . import tic_tac_toe
from .config import get_redis_handler
from ..dbs.redis_cache import RedisCacheHandler
from ..protos import game_server_pb2

TTT_MOVE_BLOCK_TIME = 1  # in seconds


def _make_validation_key(game_id: str) -> str:
    """Make the redis key for game validation."""
    return 'ttt:{}:valid'.format(game_id)


def _make_state_key(game_id: str) -> str:
    """Make the redis key for the game state."""
    return 'ttt:{}.state'.format(game_id)


def _make_state_lock_key(game_id: str) -> str:
    """Make the redis key for locking the game state."""
    return 'ttt:{}.state_lock'.format(game_id)


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


def request_game(
    request: game_server_pb2.GameRequest
) -> game_server_pb2.GameResponse:
    """Request a game."""
    pass


def describe_game() -> game_structs_pb2.GameDescription:
    """Describe this game."""
    pass


def describe_moves() -> game_structs_pb2.GameMovesResponse:
    """Describe the game moves"""
    pass


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
        moves=['place_mark']
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
