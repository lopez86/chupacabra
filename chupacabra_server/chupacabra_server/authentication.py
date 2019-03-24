import json
import logging
from typing import Optional

import arrow
import numpy as np

from dbs.authentication import AuthenticationServerHandler, UserAuthData
from dbs.redis_cache import RedisCacheHandler


logger = logging.getLogger(__name__)


SESSION_ATTEMPT_RETRIES = 5
BIG_NUMBER = 1000000000
SESSION_LENGTH = 12 * 60 * 60  # 12 hours
SESSION_CACHE_EXPIRATION = SESSION_LENGTH + 5


def authenticate_user(
    username: str,
    password_hash: str,
    handler: AuthenticationServerHandler
) -> Optional[UserAuthData]:
    """Check if the user has passed in the right credentials."""
    return handler.check_user_creds(username, password_hash)


def create_session(
    user_data: UserAuthData,
    handler: RedisCacheHandler
) -> Optional[str]:
    """Create a session for a user or get the current active one"""
    # Check if the user has an active session and if so return that
    session_key = user_data.username
    data = handler.get(session_key)
    now = arrow.utcnow().float_timestamp

    if data and now < data['expiration']:
        return data['session_id']

    # Get a session id
    seed = int(now * BIG_NUMBER) % BIG_NUMBER
    random_state = np.random.RandomState(seed)
    session_id = str(random_state.randint(BIG_NUMBER))
    session_data = {
        'session_id': session_id,
        'user_id': user_data.user_id,
        'username': user_data.username,
        'nickname': user_data.nickname,
        'email': user_data.email,
        'expiration': int(now) + SESSION_LENGTH
    }
    handler.set(session_key, session_data, lifetime=SESSION_CACHE_EXPIRATION)
    return session_id


def authenticate_session(
    username: str,
    session_id: str,
    handler: RedisCacheHandler
) -> Optional[UserAuthData]:
    """Check if a user has passed the correct session data and return user info."""
    session_key = username
    session_data = handler.get(session_key)
    if not session_data:
        return None
    session_data = json.loads(session_data)
    if session_data['session_id'] != session_id:
        return None

    # Get the timestamp
    now = arrow.utcnow().float_timestamp
    # Load session data
    session_data = json.loads(session_data)
    if now > session_data['expiration']:
        return None  # This session has expired

    return UserAuthData(
        user_id=session_data['user_id'],
        username=session_data['username'],
        nickname=session_data['nickname'],
        email=session_data['email']
    )
