from typing import Callable, NamedTuple

from protos.game_server_pb2_grpc import GameServerServicer


class GameImplementation(NamedTuple):
    """Class to hold the different game functions."""

    request_game_function: Callable
    check_game_request_function: Callable
    describe_game_function: Callable
    describe_moves_function: Callable
    make_move_function: Callable
    get_game_status_function: Callable
    get_legal_moves_function: Callable
    forfeit_game_function: Callable


class BasicGameServicer(GameServerServicer):
    def __init__(self, implementation: GameImplementation) -> None:
        """Basic game server to run on a fairly common game interface."""
        self._implementation: GameImplementation = implementation

    def RequestGame(self, request, context):
        """Request a game."""
        return self._implementation.request_game_function(request)

    def CheckGameRequest(self, request, context):
        """Check if the request has been accepted."""
        return self._implementation.check_game_request_function(request)

    def DescribeGame(self, request, context):
        """Describe the game"""
        return self._implementation.describe_game_function()

    def DescribeMoves(self, request, context):
        """Describe the game moves."""
        return self._implementation.describe_moves_function()

    def MakeMove(self, request, context):
        """Make a move"""
        return self._implementation.make_move_function(request)

    def GetGameStatus(self, request, context):
        """Get the game status"""
        return self._implementation.get_game_status_function(request)

    def GetLegalMoves(self, request, context):
        """Get the legal moves at the current time."""
        return self._implementation.get_legal_moves_function(request)

    def ForfeitGame(self, request, context):
        return self._implementation.forfeit_game_function(request)
