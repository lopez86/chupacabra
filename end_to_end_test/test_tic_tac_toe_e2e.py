from unittest import TestCase

from chupacabra_client.protos.game_structs_pb2 import (
    Coordinate, Coordinates, GamePieceMove, Move, PlayerInfo
)
import grpc
from protos.game_server_pb2 import (
    GameRequest, GameRequestStatusRequest, MoveRequest, UserGameInfo
)
from protos.game_server_pb2 import google_dot_protobuf_dot_empty__pb2
from protos.game_server_pb2_grpc import GameServerStub


Empty = google_dot_protobuf_dot_empty__pb2.Empty


class TestTicTacToeServer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.channel = grpc.insecure_channel('127.0.0.1:7654')
        cls.client_stub = GameServerStub(cls.channel)
        cls.player1 = {
            'id': '1',
            'info': PlayerInfo(
                username='player1',
                nickname='ABC',
                team='Team A',
                level='8999'
            )
        }
        cls.player2 = {
            'id': '2',
            'info': PlayerInfo(
                username='player2',
                nickname='DEF',
                team='Team B',
                level='9001'
            )
        }

    def test_tic_tac_toe_server(self):
        request1 = GameRequest(
            player_id=self.player1['id'],
            player_info=self.player1['info']
        )
        request2 = GameRequest(
            player_id=self.player2['id'],
            player_info=self.player2['info']
        )

        # First check requesting a game
        request_response1 = self.client_stub.RequestGame(request1)
        self.assertTrue(request_response1.success)
        # Adding a second request should fail
        request_response1 = self.client_stub.RequestGame(request1)
        self.assertFalse(request_response1.success)
        # Another user's request will get matched and start a game
        request_response2 = self.client_stub.RequestGame(request2)

        # Check the request statuses: they should give back the game id
        status_request1 = GameRequestStatusRequest(
            player_id=self.player1['id'],
            request_id=request_response1.request_id
        )
        status_request2 = GameRequestStatusRequest(
            player_id=self.player2['id'],
            request_id=request_response2.request_id
        )

        status_response1 = self.client_stub.CheckGameRequest(status_request1)
        status_response2 = self.client_stub.CheckGameRequest(status_request2)
        self.assertTrue(status_response1.game_found)
        self.assertTrue(status_response2.game_found)
        self.assertEqual(status_response1.game_id, status_response2.game_id)

        # Check the game state
        game_info1 = UserGameInfo(
            player_id=self.player1['id'],
            game_id=status_response1.game_id
        )
        game_info2 = UserGameInfo(
            player_id=self.player2['id'],
            game_id=status_response2.game_id
        )

        game_response1 = self.client_stub.GetGameStatus(game_info1)
        game_response2 = self.client_stub.GetGameStatus(game_info2)
        legal_moves = (
            list(game_response1.status_info.legal_moves) +
            list(game_response2.status_info.legal_moves)
        )
        self.assertEqual(['place_mark'], legal_moves)

        if len(game_response1.status_info.legal_moves) == 1:
            first_player = game_info1
            second_player = game_info2
        else:
            first_player = game_info2
            second_player = game_info1

        # TODO: Add in a full example game and check that it works
        move1 = MoveRequest(
            game_info=first_player,
            move=Move(
                move_name='place_mark',
                piece_moves=[
                    GamePieceMove(
                        locations=[
                            Coordinates(
                                values=[
                                    Coordinate(name='x', value=0),
                                    Coordinate(name='y', value=0)
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        move_response = self.client_stub.MakeMove(move1)
        self.assertTrue(move_response.success)
        # Can't move twice in a row
        move_response = self.client_stub.MakeMove(move1)
        self.assertFalse(move_response.success)
        move2 = MoveRequest(game_info=second_player, move=move1.move)
        # This position is already taken
        move_response = self.client_stub.MakeMove(move2)
        self.assertFalse(move_response.success)

