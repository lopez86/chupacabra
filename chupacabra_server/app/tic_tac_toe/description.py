from chupacabra_client.protos.game_structs_pb2 import MoveDescription

from tic_tac_toe.tic_tac_toe_game import PLAY_MODE


# Game name
TIC_TAC_TOE_NAME = 'Tic Tac Toe'

# Game description
TIC_TAC_TOE_DESCRIPTION = (
    'Tic Tac Toe is a simple game in which players take turns placing Xs and Os '
    'on a 3 by 3 game board. The winner is the first to fill a full row of 3 of their'
    'symbol. These rows can be horizontal, vertical, or diagonal.'
)

# There is only one move
PLACE_MARK_DESCRIPTION = MoveDescription(
        name='place_mark',
        description=(
            'Place your symbol (X or O) on an unfilled position on the board.'
        ),
        modes=[PLAY_MODE]
    )

# The moves
TIC_TAC_TOE_MOVES = [PLACE_MARK_DESCRIPTION]
