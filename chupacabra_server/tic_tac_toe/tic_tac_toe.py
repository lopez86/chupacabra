import json
from typing import Dict, Optional, Tuple

from chupacabra_client.protos.game_structs_pb2 import PlayerInfo, Move
import numpy as np


PLAY_MODE = 'play'
FINISHED_MODE = 'over'
GAME_MODES = frozenset({
    PLAY_MODE,
    FINISHED_MODE
})

TURN_OPTIONS = frozenset({0, 1})

ID_KEY = 'id'
PLAYER_KEY = 'players'
BOARD_KEY = 'board'
MODE_KEY = 'mode'
TURN_KEY = 'turn'
WINNER_KEY = 'winner'


class TicTacToeInternalState:
    def __init__(
        self,
        game_id: str,
        players: PlayerInfo,
        board: np.ndarray = None,
        mode: str = None,
        turn: int = None,
        winner: str = None
    ):
        if not game_id:
            raise AssertionError('Please supply a game ID.')

        if len(players) != 2:
            raise AssertionError(
                'TicTacToe must have 2 players. Have {}'.format(len(players)))

        self.id = game_id
        self.players = players
        if board is None:
            self.board = np.array([3, 3], np.int8)
        else:
            if not isinstance(board, np.ndarray):
                raise AssertionError('Board must be a numpy array. Got {}'.format(type(board)))
            if not isinstance(board.dtype, np.int8):
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
    players_list = [
        {
            'id': player.id,
            'name': player.name,
            'level': player.level,
            'team': player.team
        }
        for player in state.players
    ]
    game_dict = {
        ID_KEY: state.id,
        PLAYER_KEY: players_list,
        BOARD_KEY: state.board.tolist(),
        MODE_KEY: state.mode,
        TURN_KEY: state.turn,
        WINNER_KEY: state.winner
    }
    serialized_game = json.dumps(game_dict)
    return serialized_game


def deserialize_state(serialized_game: str) -> 'TicTacToeInternalState':
    game_data = json.loads(serialized_game, encoding='utf-8')
    game_id = game_data[ID_KEY]
    players_list = game_data[PLAYER_KEY]
    board = game_data[BOARD_KEY]
    mode = game_data[MODE_KEY]
    turn = game_data[TURN_KEY]
    winner = game_data[WINNER_KEY]
    players = [
        PlayerInfo(
            id=player['id'],
            name=player['name'],
            level=player['level'],
            team=player['team']
        )
        for player in players_list
    ]
    return TicTacToeInternalState(
        game_id,
        players,
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


def _validate_game_state(
    internal_state: TicTacToeInternalState,
    move: Move
) -> Tuple[bool, str]:
    # Game is not in play mode
    if internal_state.mode != PLAY_MODE:
        return False, 'Game is not in play mode'
    current_player = internal_state.players[internal_state.turn].id
    # Wrong player's turn
    if move.player_id != current_player:
        return False, 'You may not make a move at this time.'

    return True, ''


def _validate_and_extract_coordinates(
    move: Move
) -> Tuple[Dict[str, int], str]:
    # Regular move errors
    if len(move.piece_moves) != 1:
        return {}, 'Illegal move.'

    piece_move = move.piece_moves[0]
    if len(piece_move.locations) != 1:
        return {}, 'Illegal move.'

    location = piece_move.locations[0]
    coordinates = {
        coordinate.name: coordinate.value
        for coordinate in location.coordinates
    }

    if len(set(coordinates.keys()) & COORDINATE_NAMES) != len(COORDINATE_NAMES):
        return {}, 'Illegal move.'

    for value in coordinates.values():
        if value < 0 or value > 3:
            return {}, 'Illegal move.'

    return coordinates, ''


def _check_for_game_over(board: np.ndarray) -> Tuple[bool, int]:
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
    """Make a move"""
    # First validate the move
    is_validated, message = _validate_game_state(internal_state, move)
    if not is_validated:
        return message, None

    score = TURN_SCORES[internal_state.turn]

    coordinates, message = _validate_and_extract_coordinates(move)
    if not coordinates:
        return message, None

    move_x = coordinates[X_COORD]
    move_y = coordinates[Y_COORD]
    position_value = internal_state.board[move_x, move_y]
    if position_value != 0:
        return 'Position already filled.', None
    internal_state.board[move_x, move_y] = score
    internal_state.turn = (internal_state.turn + 1) % 2

    is_game_over, game_winner = _check_for_game_over(internal_state.board)
    if is_game_over:
        internal_state.mode = FINISHED_MODE
        internal_state.winner = game_winner

    message = 'Success.'

    return message, internal_state
