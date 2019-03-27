from typing import Any, Dict

from chupacabra_client.protos.chupacabra_pb2_grpc import ChupacabraServerServicer
from chupacabra_client.protos import chupacabra_pb2
from chupacabra_client.protos import game_structs_pb2

from chupacabra_server import chupacabra_implementation
from chupacabra_server.config import get_session_handler, get_user_authentication_handler
from protos.game_server_pb2_grpc import GameServerStub


class ChupacabraServicer(ChupacabraServerServicer):
    def __init__(
        self,
        game_map: Dict[Any, GameServerStub]
    ) -> None:
        """Initialize the servicer."""
        self._game_map = game_map

    def RegisterUser(
        self,
        request: chupacabra_pb2.UserRequest,
        context: Any
    ) -> chupacabra_pb2.UserResponse:
        """Try to register a new user."""
        auth_handler = get_user_authentication_handler()
        return chupacabra_implementation.register_user(
            request, auth_handler)

    def BeginSession(
        self,
        request: chupacabra_pb2.SessionRequest,
        context: Any
    ) -> chupacabra_pb2.SessionResponse:
        """Begin a new user session (i.e. log in)"""
        session_handler = get_session_handler()
        auth_server_handler = get_user_authentication_handler()
        return chupacabra_implementation.begin_session(
            request, auth_server_handler, session_handler
        )

    def ListAvailableGames(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> chupacabra_pb2.AvailableGamesResponse:
        """List the available games on this server."""
        session_handler = get_session_handler()
        games = list(self._game_map.keys())
        return chupacabra_implementation.list_available_games(
            request, games, session_handler
        )

    def RequestGame(
        self,
        request: chupacabra_pb2.GameRequest,
        context: Any
    ) -> game_structs_pb2.GameRequestResponse:
        """Request a new game."""
        session_handler = get_session_handler()
        return chupacabra_implementation.request_game(
            request, self._game_map, session_handler
        )

    def CheckGameRequest(
        self,
        request: chupacabra_pb2.GameRequestStatus,
        context: Any
    ) -> game_structs_pb2.GameRequestStatusResponse:
        """Check if a game request is finished."""
        session_handler = get_session_handler()
        return chupacabra_implementation.check_game_request(
            request, self._game_map, session_handler
        )

    def GetGameState(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> game_structs_pb2.GameStatusResponse:
        """Get the state of the current game."""
        session_handler = get_session_handler()
        return chupacabra_implementation.check_game_state(
            request, self._game_map, session_handler
        )

    def CheckLegalMoves(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> game_structs_pb2.LegalMovesResponse:
        """Check what moves the user can make at this point in the game."""
        session_handler = get_session_handler()
        return chupacabra_implementation.check_legal_moves(
            request, self._game_map, session_handler
        )

    def MakeMove(
        self,
        request: chupacabra_pb2.MoveRequest,
        context: Any
    ) -> game_structs_pb2.GameStatusResponse:
        """Make a move."""
        session_handler = get_session_handler()
        return chupacabra_implementation.make_move(
            request, self._game_map, session_handler
        )

    def ForfeitGame(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> game_structs_pb2.GameStatusResponse:
        """Forfeit the current game."""
        session_handler = get_session_handler()
        return chupacabra_implementation.forfeit_game(
            request, self._game_map, session_handler
        )
