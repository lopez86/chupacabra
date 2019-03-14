from unittest import TestCase

from tic_tac_toe import config


class TestConfig(TestCase):
    def test_build_from_file(self):
        ttt_config = config.TicTacToeConfig.build_from_file('')
        expected_config_dict = {
            'redis_host': config.DEFAULT_REDIS_HOST,
            'redis_port': config.DEFAULT_REDIS_PORT,
            'redis_db': config.DEFAULT_REDIS_DB
        }
        config_dict = {
            'redis_host': ttt_config.redis_host,
            'redis_port': ttt_config.redis_port,
            'redis_db': ttt_config.redis_db
        }
        self.assertEqual(expected_config_dict, config_dict)
