from unittest import TestCase

from tic_tac_toe import config


class TestConfig(TestCase):
    def test_tictactoe_config(self):
        ttt_config = config.TicTacToeConfig(config.TICTACTOE_CONFIG_PATH)
        expected_config_dict = {
            'redis_host': 'redis',
            'redis_port': 6379,
            'redis_db': 1
        }
        config_dict = {
            'redis_host': ttt_config.redis_host,
            'redis_port': ttt_config.redis_port,
            'redis_db': ttt_config.redis_db
        }
        self.assertEqual(expected_config_dict, config_dict)

        with self.assertRaises(AssertionError):
            config.TicTacToeConfig('')
