import json

from ..dbs.redis_cache import RedisCacheHandler


TICTACTOE_CONFIG_PATH = ''
DEFAULT_REDIS_HOST = ''
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB = 0


class TicTacToeConfig:
    def __init__(self) -> None:
        self.redis_host = DEFAULT_REDIS_HOST
        self.redis_port = DEFAULT_REDIS_PORT
        self.redis_db = DEFAULT_REDIS_DB

    @staticmethod
    def build_from_file(path: str) -> 'TicTacToeConfig':
        with open(path) as input_file:
            config_data = json.loads(input_file)

        config = TicTacToeConfig()
        redis_host = config_data.get('redis_host')
        if redis_host:
            config.redis_host = redis_host
        redis_port = config_data.get('redis_port')
        if redis_port:
            config.redis_port = redis_port
        redis_db = config_data.get('redis_db')
        if redis_db:
            config.redis_db = redis_db
        return config


TICTACTOE_CONFIG = TicTacToeConfig.build_from_file(TICTACTOE_CONFIG_PATH)


def get_config() -> TicTacToeConfig:
    return TICTACTOE_CONFIG


def get_redis_handler():
    config = get_config()
    return RedisCacheHandler(
        config.redis_host, config.redis_port, config.redis_db
    )
