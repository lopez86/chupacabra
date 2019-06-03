import abc
from typing import Callable, NamedTuple, Optional, Tuple

from werkzeug.security import check_password_hash, generate_password_hash


class UserAuthData(NamedTuple):
    """User authentication data"""

    user_id: str
    username: str
    nickname: str
    email: str

class AuthenticationHandler(abc.ABC):
    @abc.abstractmethod
    def add_new_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        nickname: str
    ) -> Tuple[bool, str]:
        """Add a new user to the user database"""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_user_data_and_hash(
        self,
        username: str,
    ) -> Tuple[Optional[UserAuthData], Optional[str]]:
        """Retrieve the data needed for auth and session creating."""
        raise NotImplementedError()


def get_authenticated_user_data(
    handler: AuthenticationHandler,
    username: str,
    password: str,
    password_checker: Callable[[str, str], bool]
) -> Optional[UserAuthData]:
    """Get user data if the authentication credentials match."""
    user_data, password_hash = handler.get_user_data_and_hash(username)
    if not user_data or not password_hash:
        return None

    if not password_checker(password_hash, password):
        return None

    return user_data


def hash_password(
    password: str
) -> str:
    """Hash the password. WARNING: Not meant to be up to production standards."""
    return generate_password_hash(password)


def authenticate_user(
    username: str,
    password: str,
    handler: AuthenticationHandler
) -> Optional[UserAuthData]:
    """Check if the user has passed in the right credentials."""
    return get_authenticated_user_data(
        handler, username, password, check_password_hash)
