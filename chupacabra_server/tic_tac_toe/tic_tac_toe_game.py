import copy
import json
import logging
from typing import Dict, List, Optional, Tuple

import arrow
from chupacabra_client.protos.game_structs_pb2 import PlayerInfo, Move
import numpy as np


logger = logging.getLogger(__name__)


PLAY_MODE = 'play'
FINISHED_MODE = 'over'
GAME_MODES = frozenset({
    PLAY_MODE,
    FINISHED_MODE
})

TURN_OPTIONS = frozenset({0, 1})

ID_KEY = 'id'
PLAYER_IDS_KEY = 'player_ids'
PLAYER_KEY = 'players'
BOARD_KEY = 'board'
MODE_KEY = 'mode'
TURN_KEY = 'turn'
WINNER_KEY = 'winner'
TURN_EX_TIME_KEY = 'turn_ex'
GAME_EX_TIME_KEY = 'game_ex'

GAME_LIFETIME = 11 * 60  # 11 minutes
TURN_EXPIRATION_TIME = 60  # 1 minute, expiration for a single turn


class TicTacToeInternalState:
    def __init__(
        self,
        game_id: str,
        player_ids: List[str],
        players: List[PlayerInfo],
        turn_expiration_time: int,
        game_expiration_time: int,
        board: np.ndarray = None,
        mode: str = None,
        turn: int = None,
        winner: int = None,
    ):
        """Represents an internal state of a tic tac toe game

        Args:
            game_id: str, the unique ID for this game
            player_ids: list of str, the players
            players: list of PlayerInfo, the players
            turn_expiration_time: int, the time at which the current turn expires
            game_expiration_time: int, the time at which the game expires
            board: Maybe(numpy.ndarray), the 3x3 game board
            mode: Maybe(str), the current game mode
            turn: Maybe(int), the index of the player whose turn it is (if applicable)
            winner: Maybe(int), the index of the winning player if applicable
        """
        if not game_id:
            raise AssertionError('Please supply a game ID.')

        if len(players) != 2 or len(player_ids) != 2:
            raise AssertionError(
                'TicTacToe must have 2 players. Have {}'.format(len(players)))

        self.id = game_id
        self.player_ids = player_ids
        self.players = players
        self.game_expiration_time = game_expiration_time
        self.turn_expiration_time = turn_expiration_time

        if board is None:
            self.board = np.zeros([3, 3], np.int8)
        else:
            if not isinstance(board, np.ndarray):
                raise AssertionError('Board must be a numpy array. Got {}'.format(type(board)))
            if board.dtype != np.int8:
                raise AssertionError('Board must have type numpy.int8. Got {}'.format(board.dtype))
            if board.shape != (3, 3):
                raise AssertionError('Board shape must be (3, 3). Got {}'.format(board.shape))
            self.board = board

        if mode is None:
            self.mode = 'play'
        else:
            if mode not in GAME_MODES:
                raise AssertionError('Illegal game mode {}.'.format(mode))
            self.mode = mode

        if turn is None:
            self.turn = 0
        else:
            if turn not in TURN_OPTIONS:
                raise AssertionError('Illegal turn {}.'.format(turn))
            self.turn = turn
        if winner is None:
            self.winner = -1
        else:
            self.winner = winner


def serialize_state(state: TicTacToeInternalState) -> str:
    """Serialize an internal state into a string."""
    players_list = [
        {
            'username': player.username,
            'nickname': player.nickname,
            'level': player.level,
            'team': player.team
        }
        for player in state.players
    ]
    game_dict = {
        ID_KEY: state.id,
        PLAYER_IDS_KEY: state.player_ids,
        PLAYER_KEY: players_list,
        BOARD_KEY: state.board.tolist(),
        MODE_KEY: state.mode,
        TURN_KEY: state.turn,
        WINNER_KEY: state.winner,
        TURN_EX_TIME_KEY: state.turn_expiration_time,
        GAME_EX_TIME_KEY: state.game_expiration_time
    }
    serialized_game = json.dumps(game_dict)
    return serialized_game


def deserialize_state(serialized_game: str) -> 'TicTacToeInternalState':
    """Deserialized a stringified internal state."""
    game_data = json.loads(serialized_game, encoding='utf-8')
    game_id = game_data[ID_KEY]
    player_ids = game_data[PLAYER_IDS_KEY]
    players_list = game_data[PLAYER_KEY]
    board = np.array(game_data[BOARD_KEY], dtype=np.int8)
    mode = game_data[MODE_KEY]
    turn = game_data[TURN_KEY]
    winner = game_data[WINNER_KEY]
    game_ex_time = game_data[GAME_EX_TIME_KEY]
    turn_ex_time = game_data[TURN_EX_TIME_KEY]
    players = [
        PlayerInfo(
            username=player['username'],
            nickname=player['nickname'],
            level=player['level'],
            team=player['team']
        )
        for player in players_list
    ]
    return TicTacToeInternalState(
        game_id,
        player_ids,
        players,
        turn_ex_time,
        game_ex_time,
        board=board,
        mode=mode,
        turn=turn,
        winner=winner
    )


X_COORD = 'x'
Y_COORD = 'y'
COORDINATE_NAMES = frozenset({X_COORD, Y_COORD})
TURN_SCORES = {
    0: 1,
    1: -1
}


NOT_IN_PLAY_MODE_MESSAGE = 'Game is not in play mode.'
CANNOT_MOVE_MESSAGE = 'You may not make a move at this time.'


def _validate_game_state(
    internal_state: TicTacToeInternalState,
    move: Move
) -> Tuple[bool, str]:
    """Validate if the state is consistent with attempting the move.

    Args:
        internal_state: the internal state
        move: the move being attempted

    Returns:
        tuple of bool (True=pass, False=fail), and string (message)
    """
    # Game is not in play mode
    if internal_state.mode != PLAY_MODE:
        return False, NOT_IN_PLAY_MODE_MESSAGE
    current_player = internal_state.player_ids[internal_state.turn]
    # Wrong player's turn
    if move.player_id != current_player:
        return False, CANNOT_MOVE_MESSAGE

    return True, ''


ILLEGAL_MOVE_MESSAGE = 'Illegal move.'


def _validate_and_extract_coordinates(
    move: Move
) -> Tuple[Dict[str, int], str]:
    """Validate that the move is legal and return the coordinates to fill.

    Args:
        move: the move to be validated

    Returns:
        tuple of:
            dict, keys are coordinate names 'x' and 'y', values are the positions
            str, return message if validation fails
    """
    # Regular move errors
    if len(move.piece_moves) != 1:
        return {}, ILLEGAL_MOVE_MESSAGE

    piece_move = move.piece_moves[0]
    if len(piece_move.locations) != 1:
        return {}, ILLEGAL_MOVE_MESSAGE

    location = piece_move.locations[0]
    coordinates = {
        coordinate.name: coordinate.value
        for coordinate in location.values
    }

    if (
        (len(set(coordinates.keys()) | COORDINATE_NAMES) != len(COORDINATE_NAMES)) or
        (len(set(coordinates.keys()) & COORDINATE_NAMES) != len(COORDINATE_NAMES))
    ):
        return {}, ILLEGAL_MOVE_MESSAGE

    for value in coordinates.values():
        if value < 0 or value > 3:
            return {}, ILLEGAL_MOVE_MESSAGE

    return coordinates, ''


def _check_for_game_over(board: np.ndarray) -> Tuple[bool, int]:
    """Check if the game is over given the current state of the board

    Args:
        board: numpy.ndarray, the game board

    Returns:
        tuple of bool (True=game over), and int (index of winner or -1 for no winner)
    """
    sums1 = np.sum(board, axis=0)
    sums2 = np.sum(board, axis=1)
    trace1 = np.trace(board)
    trace2 = np.trace(np.flip(board, axis=0))
    sums = np.hstack([sums1, sums2, trace1, trace2])
    top_score = np.argmax(np.abs(sums))
    best_sum = sums[top_score]
    if best_sum == 3:
        winner = 0
        game_over = True
    elif best_sum == -3:
        winner = 1
        game_over = True
    else:
        winner = -1
        if np.sum(board != 0) == 9:
            game_over = True
        else:
            game_over = False
    return game_over, winner


def make_move(
    internal_state: TicTacToeInternalState,
    move: Move
) -> Tuple[str, Optional[TicTacToeInternalState]]:
    """Attempt to make a move.

    Args:
        internal_state: the current internal state
        move: the move to attempt

    Returns:
        Tuple of:
            str, a return message
            maybe(internal state), the new internal state if the move was a success
    """
    # First validate the move
    is_validated, message = _validate_game_state(internal_state, move)
    if not is_validated:
        return message, None

    # Now test if the turn or game has expired
    current_time = arrow.utcnow().float_timestamp
    if current_time > internal_state.turn_expiration_time:
        # Turn has expired
        new_internal_state = copy.deepcopy(internal_state)
        new_internal_state.mode = FINISHED_MODE
        new_internal_state.winner = (new_internal_state.turn + 1) % 2
    elif current_time > internal_state.game_expiration_time:
        # Game has expired
        logger.info('Game {} has expired'.format(internal_state.id))
        new_internal_state = copy.deepcopy(internal_state)
        new_internal_state.mode = FINISHED_MODE
        new_internal_state.winner = -1
    else:
        score = TURN_SCORES[internal_state.turn]

        coordinates, message = _validate_and_extract_coordinates(move)
        if not coordinates:
            return message, None

        move_x = coordinates[X_COORD]
        move_y = coordinates[Y_COORD]
        position_value = internal_state.board[move_x, move_y]
        if position_value != 0:
            return 'Position already filled.', None

        # Make the move
        # We first want to copy the state so as not to modify the original state
        new_internal_state = copy.deepcopy(internal_state)
        new_internal_state.board[move_x, move_y] = score
        new_internal_state.turn = (new_internal_state.turn + 1) % 2
        new_internal_state.turn_expiration_time = int(current_time + TURN_EXPIRATION_TIME)

        is_game_over, game_winner = _check_for_game_over(new_internal_state.board)
        if is_game_over:
            new_internal_state.mode = FINISHED_MODE
            new_internal_state.winner = game_winner

        message = 'Success.'

    return message, new_internal_state
