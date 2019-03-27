import json
import os

from dbs.redis_cache import RedisCacheHandler
from utils.config_utils import get_variable_with_fallback


TICTACTOE_CONFIG_PATH = (
    os.getenv('TICTACTOE_CONFIG_PATH') or
    os.path.dirname(os.path.abspath(__file__)) + '/config.json'
)

TICTACTOE_REDIS_HOST = 'TICTACTOE_REDIS_HOST'
TICTACTOE_REDIS_PORT = 'TICTACTOE_REDIS_PORT'
TICTACTOE_REDIS_DB = 'TICTACTOE_REDIS_DB'


class TicTacToeConfig:
    def __init__(self, config_file_path: str) -> None:
        """Configuration data for Tic Tac Toe"""
        if config_file_path:
            with open(config_file_path) as config_file:
                config_data = json.load(config_file)
        else:
            config_data = {}

        self.redis_host = get_variable_with_fallback(TICTACTOE_REDIS_HOST, config_data)
        self.redis_port = get_variable_with_fallback(TICTACTOE_REDIS_PORT, config_data)
        self.redis_db = get_variable_with_fallback(TICTACTOE_REDIS_DB, config_data)


# Standard configuration
TICTACTOE_CONFIG = TicTacToeConfig(TICTACTOE_CONFIG_PATH)


def get_default_tictactoe_config() -> TicTacToeConfig:
    """Get the default configuration"""
    return TICTACTOE_CONFIG


TICTACTOE_REDIS_HANDLER = RedisCacheHandler(
    TICTACTOE_CONFIG.redis_host,
    TICTACTOE_CONFIG.redis_port,
    TICTACTOE_CONFIG.redis_db
)


def get_default_tictactoe_cache_handler() -> RedisCacheHandler:
    """Get the default redis handler for the Tic Tac Toe server."""
    return TICTACTOE_REDIS_HANDLER
