# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from chupacabra_client.protos import game_structs_pb2 as chupacabra__client_dot_protos_dot_game__structs__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from protos import game_server_pb2 as protos_dot_game__server__pb2


class GameServerStub(object):
  """A fairly generic game server
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.RequestGame = channel.unary_unary(
        '/game_server.GameServer/RequestGame',
        request_serializer=protos_dot_game__server__pb2.GameRequest.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameRequestResponse.FromString,
        )
    self.CheckGameRequest = channel.unary_unary(
        '/game_server.GameServer/CheckGameRequest',
        request_serializer=protos_dot_game__server__pb2.GameRequestStatusRequest.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameRequestStatusResponse.FromString,
        )
    self.DescribeGame = channel.unary_unary(
        '/game_server.GameServer/DescribeGame',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameDescription.FromString,
        )
    self.DescribeMoves = channel.unary_unary(
        '/game_server.GameServer/DescribeMoves',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameMovesResponse.FromString,
        )
    self.MakeMove = channel.unary_unary(
        '/game_server.GameServer/MakeMove',
        request_serializer=protos_dot_game__server__pb2.MoveRequest.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameStatusResponse.FromString,
        )
    self.GetGameStatus = channel.unary_unary(
        '/game_server.GameServer/GetGameStatus',
        request_serializer=protos_dot_game__server__pb2.UserGameInfo.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameStatusResponse.FromString,
        )
    self.GetLegalMoves = channel.unary_unary(
        '/game_server.GameServer/GetLegalMoves',
        request_serializer=protos_dot_game__server__pb2.UserGameInfo.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.LegalMovesResponse.FromString,
        )
    self.ForfeitGame = channel.unary_unary(
        '/game_server.GameServer/ForfeitGame',
        request_serializer=protos_dot_game__server__pb2.UserGameInfo.SerializeToString,
        response_deserializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameStatusResponse.FromString,
        )


class GameServerServicer(object):
  """A fairly generic game server
  """

  def RequestGame(self, request, context):
    """Request a new game
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CheckGameRequest(self, request, context):
    """Check a request
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DescribeGame(self, request, context):
    """Describe the game contained in this server
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DescribeMoves(self, request, context):
    """Describe the moves available in this game
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def MakeMove(self, request, context):
    """Make a move
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetGameStatus(self, request, context):
    """Get the game status
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetLegalMoves(self, request, context):
    """Get the moves available to the user at this point in the game
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ForfeitGame(self, request, context):
    """Forfeit the game
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GameServerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'RequestGame': grpc.unary_unary_rpc_method_handler(
          servicer.RequestGame,
          request_deserializer=protos_dot_game__server__pb2.GameRequest.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameRequestResponse.SerializeToString,
      ),
      'CheckGameRequest': grpc.unary_unary_rpc_method_handler(
          servicer.CheckGameRequest,
          request_deserializer=protos_dot_game__server__pb2.GameRequestStatusRequest.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameRequestStatusResponse.SerializeToString,
      ),
      'DescribeGame': grpc.unary_unary_rpc_method_handler(
          servicer.DescribeGame,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameDescription.SerializeToString,
      ),
      'DescribeMoves': grpc.unary_unary_rpc_method_handler(
          servicer.DescribeMoves,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameMovesResponse.SerializeToString,
      ),
      'MakeMove': grpc.unary_unary_rpc_method_handler(
          servicer.MakeMove,
          request_deserializer=protos_dot_game__server__pb2.MoveRequest.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameStatusResponse.SerializeToString,
      ),
      'GetGameStatus': grpc.unary_unary_rpc_method_handler(
          servicer.GetGameStatus,
          request_deserializer=protos_dot_game__server__pb2.UserGameInfo.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameStatusResponse.SerializeToString,
      ),
      'GetLegalMoves': grpc.unary_unary_rpc_method_handler(
          servicer.GetLegalMoves,
          request_deserializer=protos_dot_game__server__pb2.UserGameInfo.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.LegalMovesResponse.SerializeToString,
      ),
      'ForfeitGame': grpc.unary_unary_rpc_method_handler(
          servicer.ForfeitGame,
          request_deserializer=protos_dot_game__server__pb2.UserGameInfo.FromString,
          response_serializer=chupacabra__client_dot_protos_dot_game__structs__pb2.GameStatusResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'game_server.GameServer', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
