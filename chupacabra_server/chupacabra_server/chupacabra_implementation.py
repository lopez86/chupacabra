from chupacabra_client.protos import chupacabra_pb2, game_structs_pb2


def register_user(
    request: chupacabra_pb2.UserRequest
) -> chupacabra_pb2.UserResponse:
    """Register a new user."""
    raise NotImplementedError()


def begin_session(
    request: chupacabra_pb2.SessionRequest
) -> chupacabra_pb2.SessionResponse:
    """Try to begin a new session."""
    raise NotImplementedError()


def list_available_games(
    request: chupacabra_pb2.PlayerGameInfo
) -> chupacabra_pb2.AvailableGamesResponse:
    """List the games available on the server."""
    raise NotImplementedError()


def request_game(
    request: chupacabra_pb2.GameRequest
) -> game_structs_pb2.GameRequestResponse:
    """Request a new game."""
    raise NotImplementedError()


def check_game_request(
    request: chupacabra_pb2.GameRequestStatus
) -> game_structs_pb2.GameRequestStatusResponse:
    """Check if the game request has been fulfilled"""
    raise NotImplementedError()


def check_game_state(
    request: chupacabra_pb2.PlayerGameInfo
) -> game_structs_pb2.GameStatusResponse:
    """Check the state of an existing game."""
    raise NotImplementedError()


def check_legal_moves(
    request: chupacabra_pb2.PlayerGameInfo
) -> game_structs_pb2.LegalMovesResponse:
    """Check what types of moves are available for the player at this point in the game."""
    raise NotImplementedError()


def make_move(
    request: chupacabra_pb2.MoveRequest
) -> game_structs_pb2.GameStatusResponse:
    """Make a move in the game."""
    raise NotImplementedError()


def forfeit_game(
    request: chupacabra_pb2.PlayerGameInfo
) -> game_structs_pb2.GameStatusResponse:
    """Immediately forfeit the game."""
    raise NotImplementedError()
