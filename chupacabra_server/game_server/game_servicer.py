from chupacabra_server.protos.game_server_pb2_grpc import GameServerServicer

class BasicGameServicer(GameServerServicer):

    def __init__(self, game, redis_getter) -> None:
        """Basic game server to run on a fairly common game interface."""
        self._game = game
        self._redis_getter = redis_getter

    def RequestGame(self, request, context):
        raise NotImplementedError('RequestGame is not implemented.')

    def DescribeGame(self, request, context):
        raise NotImplementedError('DescribeGame is not implemented.')

    def DescribeMoves(self, request, context):
        raise NotImplementedError('DescribeMoves is not implemented.')

    def MakeMove(self, request, context):
        raise NotImplementedError('MakeMove is not implemented.')

    def GetGameStatus(self, request, context):
        raise NotImplementedError('GetGameStatus is not implemented.')

    def GetLegalMoves(self, request, context):
        raise NotImplementedError('GetLegalMoves is not implemented.')

    def ForfeitGame(self, request, context):
        raise NotImplementedError('ForfeitGame is not implemented.')
