import logging
from typing import Any, Dict

from chupacabra_client.protos.chupacabra_pb2_grpc import ChupacabraServerServicer
from chupacabra_client.protos import chupacabra_pb2
from chupacabra_client.protos import game_structs_pb2

from chupacabra_server import chupacabra_implementation
from chupacabra_server.config import get_session_handler, get_user_authentication_handler
from protos.game_server_pb2_grpc import GameServerStub


logger = logging.getLogger(__name__)


ERROR_MESSAGE = 'Error during handling of your request'


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
        try:
            auth_handler = get_user_authentication_handler()
            return chupacabra_implementation.register_user(
                request, auth_handler)
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def BeginSession(
        self,
        request: chupacabra_pb2.SessionRequest,
        context: Any
    ) -> chupacabra_pb2.SessionResponse:
        """Begin a new user session (i.e. log in)"""
        try:
            session_handler = get_session_handler()
            auth_server_handler = get_user_authentication_handler()
            return chupacabra_implementation.begin_session(
                request, auth_server_handler, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def ListAvailableGames(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> chupacabra_pb2.AvailableGamesResponse:
        """List the available games on this server."""
        try:
            session_handler = get_session_handler()
            games = list(self._game_map.keys())
            return chupacabra_implementation.list_available_games(
                request, games, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def RequestGame(
        self,
        request: chupacabra_pb2.GameRequest,
        context: Any
    ) -> game_structs_pb2.GameRequestResponse:
        """Request a new game."""
        try:
            session_handler = get_session_handler()
            return chupacabra_implementation.request_game(
                request, self._game_map, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def CheckGameRequest(
        self,
        request: chupacabra_pb2.GameRequestStatus,
        context: Any
    ) -> game_structs_pb2.GameRequestStatusResponse:
        """Check if a game request is finished."""
        try:
            session_handler = get_session_handler()
            return chupacabra_implementation.check_game_request(
                request, self._game_map, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def GetGameState(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> game_structs_pb2.GameStatusResponse:
        """Get the state of the current game."""
        try:
            session_handler = get_session_handler()
            return chupacabra_implementation.check_game_state(
                request, self._game_map, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def CheckLegalMoves(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> game_structs_pb2.LegalMovesResponse:
        """Check what moves the user can make at this point in the game."""
        try:
            session_handler = get_session_handler()
            return chupacabra_implementation.check_legal_moves(
                request, self._game_map, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def MakeMove(
        self,
        request: chupacabra_pb2.MoveRequest,
        context: Any
    ) -> game_structs_pb2.GameStatusResponse:
        """Make a move."""
        try:
            session_handler = get_session_handler()
            return chupacabra_implementation.make_move(
                request, self._game_map, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)

    def ForfeitGame(
        self,
        request: chupacabra_pb2.PlayerGameInfo,
        context: Any
    ) -> game_structs_pb2.GameStatusResponse:
        """Forfeit the current game."""
        try:
            session_handler = get_session_handler()
            return chupacabra_implementation.forfeit_game(
                request, self._game_map, session_handler
            )
        except Exception as exception:
            logger.error(exception)
            raise AssertionError(ERROR_MESSAGE)
