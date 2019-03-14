import unittest


from chupacabra_client.protos.game_structs_pb2 import (
    Coordinate, Coordinates, GamePieceMove, Move, PlayerInfo
)
import numpy as np

from tic_tac_toe import tic_tac_toe


class TestTicTacToe(unittest.TestCase):
    def test__validate_game_state(self):
        players = [
            PlayerInfo(id='1', name='player1'),
            PlayerInfo(id='2', name='player2')
        ]
        state = tic_tac_toe.TicTacToeInternalState('a', players, turn=0)
        move = Move(player_id='1')
        validated, message = tic_tac_toe._validate_game_state(state, move)
        self.assertTrue(validated)
        self.assertEqual('', message)

        state = tic_tac_toe.TicTacToeInternalState('a', players, turn=0)
        move = Move(player_id='2')
        validated, message = tic_tac_toe._validate_game_state(state, move)
        self.assertFalse(validated)
        self.assertEqual(tic_tac_toe.CANNOT_MOVE_MESSAGE, message)

        state = tic_tac_toe.TicTacToeInternalState(
            'a', players, turn=0, mode=tic_tac_toe.FINISHED_MODE)
        move = Move(player_id='2')
        validated, message = tic_tac_toe._validate_game_state(state, move)
        self.assertFalse(validated)
        self.assertEqual(tic_tac_toe.NOT_IN_PLAY_MODE_MESSAGE, message)

    def test__validate_and_extract_coordinates(self):
        # A good move
        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=0),
                                Coordinate(name='y', value=1)
                            ]
                        )
                    ]
                )
            ]
        )
        coordinates, message = tic_tac_toe._validate_and_extract_coordinates(move)
        expected_coordinates = {
            'x': 0,
            'y': 1
        }
        self.assertEqual(expected_coordinates, coordinates)
        self.assertEqual('', message)

        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=5),
                                Coordinate(name='y', value=1)
                            ]
                        )
                    ]
                )
            ]
        )
        coordinates, message = tic_tac_toe._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe.ILLEGAL_MOVE_MESSAGE, message)

        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=0),
                            ]
                        )
                    ]
                )
            ]
        )
        coordinates, message = tic_tac_toe._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe.ILLEGAL_MOVE_MESSAGE, message)

        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=1),
                                Coordinate(name='y', value=1),
                                Coordinate(name='z', value=0)
                            ]
                        )
                    ]
                )
            ]
        )
        coordinates, message = tic_tac_toe._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe.ILLEGAL_MOVE_MESSAGE, message)

        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=5),
                                Coordinate(name='z', value=1)
                            ]
                        )
                    ]
                )
            ]
        )
        coordinates, message = tic_tac_toe._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe.ILLEGAL_MOVE_MESSAGE, message)

        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=0),
                                Coordinate(name='y', value=1)
                            ]
                        ),
                    ] * 2
                )
            ]
        )
        coordinates, message = tic_tac_toe._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe.ILLEGAL_MOVE_MESSAGE, message)

        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=0),
                                Coordinate(name='y', value=1)
                            ]
                        ),
                    ]
                )
            ] * 2
        )
        coordinates, message = tic_tac_toe._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe.ILLEGAL_MOVE_MESSAGE, message)

    def test__check_for_game_over(self):
        board = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        game_over, winner = tic_tac_toe._check_for_game_over(board)
        self.assertEqual(game_over, False)
        self.assertEqual(winner, -1)

        board = np.array([[1, -1, 1], [-1, 0, 1], [0, 0, -1]])
        game_over, winner = tic_tac_toe._check_for_game_over(board)
        self.assertEqual(game_over, False)
        self.assertEqual(winner, -1)

        # Games with winners (may not necessarily be actual valid states)

        board = np.array([[1, 1, 1], [0, -1, 0], [-1, 0, -1]])
        game_over, winner = tic_tac_toe._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 0)

        board = np.array([[0, 1, -1], [0, 1, 0], [-1, 1, 0]])
        game_over, winner = tic_tac_toe._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 0)

        board = np.array([[0, -1, 0], [0, -1, 1], [1, -1, 0]])
        game_over, winner = tic_tac_toe._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 1)

        board = np.array([[-1, 0, 1], [0, 1, 0], [1, -1, 0]])
        game_over, winner = tic_tac_toe._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 0)

        # A tie
        board = np.array([[1, -1, 1], [1, -1, 1], [-1, 1, -1]])
        game_over, winner = tic_tac_toe._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, -1)
