import abc
from typing import Optional, Tuple

from dbs.authentication import UserAuthData


class SessionHandler(abc.ABC):
    @abc.abstractmethod
    def create_or_retrieve_session(
        self,
        user_data: UserAuthData
    ) -> Tuple[str, str]:
        """Create a new session for the user or retrieve an existing one."""
        raise NotImplementedError()

    @abc.abstractmethod
    def authenticate_session(
        self,
        username: str,
        session_id: str
    ) -> Optional[UserAuthData]:
        """Authenticate a session and return the associated user info."""
        raise NotImplementedError()
