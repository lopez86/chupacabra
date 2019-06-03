import json
import os

from dbs.keyvalue_session import KeyValueSessionHandler
from dbs.postgres_auth import PostgresAuthenticationHandler
from dbs.redis_cache import RedisCacheHandler
from dbs.session import SessionHandler
from utils.config_utils import get_variable_with_fallback


# Session cache params
SESSION_LENGTH = 12 * 60 * 60  # 12 hours
SESSION_CACHE_EXPIRATION = SESSION_LENGTH + 5


SERVER_CONFIG_PATH = (
    os.getenv('SERVER_CONFIG_PATH') or
    os.path.dirname(os.path.abspath(__file__)) + '/config.json'
)

SESSION_REDIS_URL = 'SESSION_REDIS_URL'
SESSION_REDIS_PORT = 'SESSION_REDIS_PORT'
SESSION_REDIS_DB = 'SESSION_REDIS_DB'
AUTH_PG_URL = 'AUTH_PG_URL'
AUTH_PG_PORT = 'AUTH_PG_PORT'
AUTH_PG_DB = 'AUTH_PG_DB'
AUTH_PG_USERNAME = 'AUTH_PG_USERNAME'
AUTH_PG_PASSWORD = 'AUTH_PG_PASSWORD'


class ChupacabraServerConfig:
    def __init__(self, config_file_path: str) -> None:
        """Initialize the server configuration structure"""
        if config_file_path:
            with open(config_file_path) as config_file:
                config_data = json.load(config_file)
        else:
            config_data = {}

        # Use env variables first then the config data
        self.redis_url = get_variable_with_fallback(SESSION_REDIS_URL, config_data)
        self.redis_port = get_variable_with_fallback(SESSION_REDIS_PORT, config_data)
        self.redis_db = get_variable_with_fallback(SESSION_REDIS_DB, config_data)
        self.auth_url = get_variable_with_fallback(AUTH_PG_URL, config_data)
        self.auth_port = get_variable_with_fallback(AUTH_PG_PORT, config_data)
        self.auth_db = get_variable_with_fallback(AUTH_PG_DB, config_data)
        self.auth_username = get_variable_with_fallback(AUTH_PG_USERNAME, config_data)
        self.auth_password = get_variable_with_fallback(AUTH_PG_PASSWORD, config_data)


SERVER_CONFIG = ChupacabraServerConfig(SERVER_CONFIG_PATH)


def get_default_server_config() -> ChupacabraServerConfig:
    """Get the standard server configuration"""
    return SERVER_CONFIG


USER_AUTH_HANDLER = PostgresAuthenticationHandler(
    SERVER_CONFIG.auth_url,
    SERVER_CONFIG.auth_port,
    SERVER_CONFIG.auth_db,
    SERVER_CONFIG.auth_username,
    SERVER_CONFIG.auth_password
)

SESSION_REDIS = RedisCacheHandler(
    SERVER_CONFIG.redis_url,
    SERVER_CONFIG.redis_port,
    SERVER_CONFIG.redis_db
)

SESSION_HANDLER = KeyValueSessionHandler(
    SESSION_REDIS,
    SESSION_LENGTH,
    SESSION_CACHE_EXPIRATION
)


def get_user_authentication_handler() -> PostgresAuthenticationHandler:
    """Get a handler for the user authentication server"""
    return USER_AUTH_HANDLER


def get_session_handler() -> SessionHandler:
    """Get a handler for the session cache handler"""
    return SESSION_HANDLER
