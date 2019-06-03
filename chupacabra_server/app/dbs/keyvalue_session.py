import json
import secrets
from typing import Optional, Tuple

import arrow

from dbs.authentication import UserAuthData
from dbs.keyvalue_store import KeyValueStore
from dbs.session import SessionHandler


class KeyValueSessionHandler(SessionHandler):
    def __init__(
        self,
        store: KeyValueStore,
        session_length: int,
        session_cache_expiration: int
    ) -> None:
        self._store = store
        self._session_length = session_length
        self._session_cache_expiration = session_cache_expiration

    def create_or_retrieve_session(
        self,
        user_data: UserAuthData
    ) -> Tuple[str, str]:
        """Create a new session for the user or retrieve an existing one."""
        session_key = user_data.username
        data = self._store.get(session_key)
        now = arrow.utcnow().float_timestamp

        if data:
            deserialized_data = json.loads(data)
            if now < deserialized_data['expiration']:
                return deserialized_data['session_id'], 'Success'

        # Get a session id
        session_id = secrets.token_hex(8)
        session_data = json.dumps({
            'session_id': session_id,
            'user_id': user_data.user_id,
            'username': user_data.username,
            'nickname': user_data.nickname,
            'email': user_data.email,
            'expiration': int(now) + self._session_length
        })
        self._store.set(
            session_key,
            session_data,
            lifetime=self._session_cache_expiration
        )
        return session_id, 'Success'

    def authenticate_session(
        self,
        username: str,
        session_id: str
    ) -> Optional[UserAuthData]:
        """Authenticate a session and return the associated user info."""
        session_key = username
        session_string = self._store.get(session_key)
        if not session_string:
            return None
        session_data = json.loads(session_string)
        if session_data['session_id'] != session_id:
            return None

        # Get the timestamp
        now = arrow.utcnow().float_timestamp
        # Load session data
        if now > session_data['expiration']:
            return None  # This session has expired

        return UserAuthData(
            user_id=session_data['user_id'],
            username=session_data['username'],
            nickname=session_data['nickname'],
            email=session_data['email']
        )
