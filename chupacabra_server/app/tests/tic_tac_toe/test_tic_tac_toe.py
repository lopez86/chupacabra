import unittest

import arrow
from chupacabra_client.protos.game_structs_pb2 import (
    Coordinate, Coordinates, GamePieceMove, Move, PlayerInfo
)
import numpy as np

from tic_tac_toe import tic_tac_toe_game


class TestTicTacToeGame(unittest.TestCase):
    def test__init(self):
        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState('', [], [], 0, 0)

        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState(
                '1',
                [],
                [PlayerInfo(), PlayerInfo()],
                0,
                0
            )

        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState(
                '1',
                ['1', '2'],
                [],
                0,
                0
            )

        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState(
                '1',
                ['1', '2'],
                [PlayerInfo(), PlayerInfo()],
                0,
                0,
                board=[1, 2, 3]
            )

        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState(
                '1',
                ['1', '2'],
                [PlayerInfo(), PlayerInfo()],
                0,
                0,
                board=np.zeros([3, 3], dtype=np.float32)
            )

        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState(
                '1',
                ['1', '2'],
                [PlayerInfo(), PlayerInfo()],
                0,
                0,
                board=np.zeros([2, 2], dtype=np.int8)
            )

        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState(
                '1',
                ['1', '2'],
                [PlayerInfo(), PlayerInfo()],
                0,
                0,
                mode='Illegal mode'
            )

        with self.assertRaises(AssertionError):
            tic_tac_toe_game.TicTacToeInternalState(
                '1',
                ['1', '2'],
                [PlayerInfo(), PlayerInfo()],
                0,
                0,
                turn=2
            )

        state = tic_tac_toe_game.TicTacToeInternalState(
            '1',
            ['1', '2'],
            [PlayerInfo(), PlayerInfo()],
            0,
            0,
            turn=None,
            winner=1,
            board=np.zeros([3, 3], dtype=np.int8)
        )

        self.assertEqual(1, state.winner)
        self.assertEqual(0, state.turn)

    def test_serialize_state(self):
        state = tic_tac_toe_game.TicTacToeInternalState(
            '1',
            ['1', '2'],
            [PlayerInfo(), PlayerInfo()],
            5,
            6,
        )
        serialized = tic_tac_toe_game.serialize_state(state)
        deserialized = tic_tac_toe_game.deserialize_state(serialized)
        self.assertEqual('1', deserialized.id)
        self.assertEqual(['1', '2'], deserialized.player_ids)
        self.assertEqual(6, deserialized.game_expiration_time)
        self.assertEqual(5, deserialized.turn_expiration_time)

    def test__validate_game_state(self):
        expiration_time = arrow.utcnow().timestamp + 3600
        players = [
            PlayerInfo(username='player1'),
            PlayerInfo(username='player2')
        ]
        player_ids = ['1', '2']
        state = tic_tac_toe_game.TicTacToeInternalState(
            'a', player_ids, players, expiration_time, expiration_time, turn=0)
        validated, message = tic_tac_toe_game._validate_game_state(state, '1')
        self.assertTrue(validated)
        self.assertEqual('', message)

        state = tic_tac_toe_game.TicTacToeInternalState(
            'a', player_ids, players, expiration_time, expiration_time, turn=0)
        validated, message = tic_tac_toe_game._validate_game_state(state, '2')
        self.assertFalse(validated)
        self.assertEqual(tic_tac_toe_game.CANNOT_MOVE_MESSAGE, message)

        state = tic_tac_toe_game.TicTacToeInternalState(
            'a',
            player_ids,
            players,
            expiration_time,
            expiration_time,
            turn=0,
            mode=tic_tac_toe_game.FINISHED_MODE
        )
        validated, message = tic_tac_toe_game._validate_game_state(state, '2')
        self.assertFalse(validated)
        self.assertEqual(tic_tac_toe_game.NOT_IN_PLAY_MODE_MESSAGE, message)

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
        coordinates, message = tic_tac_toe_game._validate_and_extract_coordinates(move)
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
        coordinates, message = tic_tac_toe_game._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe_game.ILLEGAL_MOVE_MESSAGE, message)

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
        coordinates, message = tic_tac_toe_game._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe_game.ILLEGAL_MOVE_MESSAGE, message)

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
        coordinates, message = tic_tac_toe_game._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe_game.ILLEGAL_MOVE_MESSAGE, message)

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
        coordinates, message = tic_tac_toe_game._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe_game.ILLEGAL_MOVE_MESSAGE, message)

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
        coordinates, message = tic_tac_toe_game._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe_game.ILLEGAL_MOVE_MESSAGE, message)

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
        coordinates, message = tic_tac_toe_game._validate_and_extract_coordinates(move)
        self.assertEqual({}, coordinates)
        self.assertEqual(tic_tac_toe_game.ILLEGAL_MOVE_MESSAGE, message)

    def test__check_for_game_over(self):
        board = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        game_over, winner = tic_tac_toe_game._check_for_game_over(board)
        self.assertEqual(game_over, False)
        self.assertEqual(winner, -1)

        board = np.array([[1, -1, 1], [-1, 0, 1], [0, 0, -1]])
        game_over, winner = tic_tac_toe_game._check_for_game_over(board)
        self.assertEqual(game_over, False)
        self.assertEqual(winner, -1)

        # Games with winners (may not necessarily be actual valid states)

        board = np.array([[1, 1, 1], [0, -1, 0], [-1, 0, -1]])
        game_over, winner = tic_tac_toe_game._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 0)

        board = np.array([[0, 1, -1], [0, 1, 0], [-1, 1, 0]])
        game_over, winner = tic_tac_toe_game._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 0)

        board = np.array([[0, -1, 0], [0, -1, 1], [1, -1, 0]])
        game_over, winner = tic_tac_toe_game._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 1)

        board = np.array([[-1, 0, 1], [0, 1, 0], [1, -1, 0]])
        game_over, winner = tic_tac_toe_game._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, 0)

        # A tie
        board = np.array([[1, -1, 1], [1, -1, 1], [-1, 1, -1]])
        game_over, winner = tic_tac_toe_game._check_for_game_over(board)
        self.assertEqual(game_over, True)
        self.assertEqual(winner, -1)

    def test_make_move(self):
        good_time = arrow.utcnow().timestamp + 3600
        state = tic_tac_toe_game.TicTacToeInternalState(
            '1',
            ['1', '2'],
            [PlayerInfo(), PlayerInfo()],
            0,
            0,
            turn=0
        )

        move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=0),
                                Coordinate(name='y', value=0)
                            ]
                        ),
                    ]
                )
            ]
        )

        result = tic_tac_toe_game.make_move(
            state,
            move,
            '3'
        )
        self.assertEqual((tic_tac_toe_game.CANNOT_MOVE_MESSAGE, None), result)

        result = tic_tac_toe_game.make_move(
            state,
            move,
            '1'
        )
        self.assertEqual(np.sum(state.board), np.sum(result[1].board))
        self.assertEqual(tic_tac_toe_game.FINISHED_MODE, result[1].mode)

        # Good turn time, bad game time
        state = tic_tac_toe_game.TicTacToeInternalState(
            '1',
            ['1', '2'],
            [PlayerInfo(), PlayerInfo()],
            good_time,
            0,
            turn=0
        )
        result = tic_tac_toe_game.make_move(
            state,
            move,
            '1'
        )
        self.assertEqual(np.sum(state.board), np.sum(result[1].board))
        self.assertEqual(tic_tac_toe_game.FINISHED_MODE, result[1].mode)

        state = tic_tac_toe_game.TicTacToeInternalState(
            '1',
            ['1', '2'],
            [PlayerInfo(), PlayerInfo()],
            good_time,
            good_time,
            turn=0
        )
        message, new_state = tic_tac_toe_game.make_move(
            state,
            move,
            '1'
        )
        self.assertEqual(
             0,
             np.sum(
                np.array(
                    [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                    dtype=np.int8
                ) - new_state.board
             )
        )

        bad_move = Move(
            piece_moves=[
                GamePieceMove(
                    locations=[
                        Coordinates(
                            values=[
                                Coordinate(name='x', value=0),
                                Coordinate(name='z', value=0)
                            ]
                        ),
                    ]
                )
            ]
        )
        _, new_state = tic_tac_toe_game.make_move(
            state,
            bad_move,
            '1'
        )
        self.assertIsNone(new_state)

        state = tic_tac_toe_game.TicTacToeInternalState(
            '1',
            ['1', '2'],
            [PlayerInfo(), PlayerInfo()],
            good_time,
            good_time,
            turn=0,
            board=np.array(
                [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                dtype=np.int8
            )
        )

        _, new_state = tic_tac_toe_game.make_move(
            state,
            move,
            '1'
        )
        self.assertIsNone(new_state)

        state = tic_tac_toe_game.TicTacToeInternalState(
            '1',
            ['1', '2'],
            [PlayerInfo(), PlayerInfo()],
            good_time,
            good_time,
            turn=0,
            board=np.array(
                [[0, 1, 1], [0, 0, 0], [0, 0, 0]],
                dtype=np.int8
            )
        )
        _, new_state = tic_tac_toe_game.make_move(
            state,
            move,
            '1'
        )
        self.assertEqual(tic_tac_toe_game.FINISHED_MODE, new_state.mode)
        self.assertEqual(0, new_state.winner)
