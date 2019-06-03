from typing import Dict, List

from chupacabra_client.protos import chupacabra_pb2, game_structs_pb2

from dbs.authentication import AuthenticationHandler, authenticate_user, hash_password
from dbs.session import SessionHandler
from protos import game_server_pb2
from protos.game_server_pb2_grpc import GameServerStub


AUTHENTICATION_FAILED = 'Authentication failed.'
GAME_TYPE_NOT_FOUND = 'Game of type \'{}\' not found.'


def register_user(
    request: chupacabra_pb2.UserRequest,
    handler: AuthenticationHandler
) -> chupacabra_pb2.UserResponse:
    """Register a new user."""
    username = request.username
    nickname = request.nickname
    password_hash = hash_password(request.password)
    email = request.email
    success, message = handler.add_new_user(username, email, password_hash, nickname)
    response = chupacabra_pb2.UserResponse(
        success=success,
        message=message
    )
    return response


def begin_session(
    request: chupacabra_pb2.SessionRequest,
    auth_handler: AuthenticationHandler,
    session_handler: SessionHandler
) -> chupacabra_pb2.SessionResponse:
    """Try to begin a new session."""
    username = request.username
    password = request.password
    user_auth_data = authenticate_user(username, password, auth_handler)
    del password
    if user_auth_data is None:
        return chupacabra_pb2.SessionResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )
    session_id, message = session_handler.create_or_retrieve_session(user_auth_data)
    if session_id:
        response = chupacabra_pb2.SessionResponse(
            success=True,
            message=message,
            session_id=session_id
        )
    else:
        response = chupacabra_pb2.SessionResponse(
            success=False,
            message=message
        )
    return response


def list_available_games(
    request: chupacabra_pb2.PlayerGameInfo,
    games: List[str],
    session_handler: SessionHandler
) -> chupacabra_pb2.AvailableGamesResponse:
    """List the games available on the server."""
    username = request.username
    session_id = request.session_id
    user_info = session_handler.authenticate_session(username, session_id)
    if not user_info:
        return chupacabra_pb2.AvailableGamesResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )

    descriptions = [
        game_structs_pb2.GameDescription(
            name=game
        )
        for game in games
    ]
    return chupacabra_pb2.AvailableGamesResponse(
        descriptions=descriptions,
        success=True,
        message='Success'
    )


def request_game(
    request: chupacabra_pb2.GameRequest,
    game_map: Dict[str, GameServerStub],
    session_handler: SessionHandler
) -> game_structs_pb2.GameRequestResponse:
    """Request a new game."""
    username = request.username
    session_id = request.session_id
    user_data = session_handler.authenticate_session(username, session_id)
    if user_data is None:
        return game_structs_pb2.GameRequestResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )

    game_stub = game_map.get(request.game_type)
    if game_stub is None:
        return game_structs_pb2.GameRequestResponse(
            success=False,
            message=GAME_TYPE_NOT_FOUND.format(request.game_type)
        )

    player_info = game_structs_pb2.PlayerInfo(
        username=username,
        nickname=user_data.nickname
    )

    internal_request = game_server_pb2.GameRequest(
        player_id=user_data.user_id,
        player_info=player_info
    )

    response = game_stub.RequestGame(internal_request)
    return response


def check_game_request(
    request: chupacabra_pb2.GameRequestStatus,
    game_map: Dict[str, GameServerStub],
    session_handler: SessionHandler
) -> game_structs_pb2.GameRequestStatusResponse:
    """Check if the game request has been fulfilled"""
    username = request.username
    session_id = request.session_id
    user_data = session_handler.authenticate_session(username, session_id)
    if user_data is None:
        return game_structs_pb2.GameRequestStatusResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )

    game_stub = game_map.get(request.game_type)
    if game_stub is None:
        return game_structs_pb2.GameRequestStatusResponse(
            success=False,
            message=GAME_TYPE_NOT_FOUND.format(request.game_type)
        )

    internal_request = game_server_pb2.GameRequestStatusRequest(
        player_id=user_data.user_id,
        request_id=request.request_id
    )

    response = game_stub.CheckGameRequest(internal_request)
    return response


def check_game_state(
    request: chupacabra_pb2.PlayerGameInfo,
    game_map: Dict[str, GameServerStub],
    session_handler: SessionHandler
) -> game_structs_pb2.GameStatusResponse:
    """Check the state of an existing game."""
    username = request.username
    session_id = request.session_id
    user_data = session_handler.authenticate_session(username, session_id)
    if user_data is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )

    game_stub = game_map.get(request.game_type)
    if game_stub is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=GAME_TYPE_NOT_FOUND.format(request.game_type)
        )

    internal_request = game_server_pb2.UserGameInfo(
        player_id=user_data.user_id,
        game_id=request.game_id
    )

    response = game_stub.GetGameStatus(internal_request)
    return response


def check_legal_moves(
    request: chupacabra_pb2.PlayerGameInfo,
    game_map: Dict[str, GameServerStub],
    session_handler: SessionHandler
) -> game_structs_pb2.LegalMovesResponse:
    """Check what types of moves are available for the player at this point in the game."""
    username = request.username
    session_id = request.session_id
    user_data = session_handler.authenticate_session(username, session_id)
    if user_data is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )

    game_stub = game_map.get(request.game_type)
    if game_stub is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=GAME_TYPE_NOT_FOUND.format(request.game_type)
        )

    internal_request = game_server_pb2.UserGameInfo(
        player_id=user_data.user_id,
        game_id=request.game_id
    )

    response = game_stub.GetLegalMoves(internal_request)
    return response


def make_move(
    request: chupacabra_pb2.MoveRequest,
    game_map: Dict[str, GameServerStub],
    session_handler: SessionHandler
) -> game_structs_pb2.GameStatusResponse:
    """Make a move in the game."""
    username = request.game_info.username
    session_id = request.game_info.session_id
    user_data = session_handler.authenticate_session(username, session_id)
    if user_data is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )

    game_stub = game_map.get(request.game_info.game_type)
    if game_stub is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=GAME_TYPE_NOT_FOUND.format(request.game_info.game_type)
        )

    user_game_info = game_server_pb2.UserGameInfo(
        player_id=user_data.user_id,
        game_id=request.game_info.game_id
    )
    internal_request = game_server_pb2.MoveRequest(
        game_info=user_game_info,
        move=request.move
    )

    response = game_stub.MakeMove(internal_request)
    return response


def forfeit_game(
    request: chupacabra_pb2.PlayerGameInfo,
    game_map: Dict[str, GameServerStub],
    session_handler: SessionHandler
) -> game_structs_pb2.GameStatusResponse:
    """Immediately forfeit the game."""
    username = request.username
    session_id = request.session_id
    user_data = session_handler.authenticate_session(username, session_id)
    if user_data is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=AUTHENTICATION_FAILED
        )

    game_stub = game_map.get(request.game_type)
    if game_stub is None:
        return game_structs_pb2.GameStatusResponse(
            success=False,
            message=GAME_TYPE_NOT_FOUND.format(request.game_type)
        )

    internal_request = game_server_pb2.UserGameInfo(
        player_id=user_data.user_id,
        game_id=request.game_id
    )

    response = game_stub.ForfeitGame(internal_request)
    return response
