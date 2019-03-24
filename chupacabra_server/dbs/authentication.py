from enum import IntEnum
from typing import NamedTuple, Optional, Tuple

import arrow
import numpy as np
from sqlalchemy import create_engine


CHECK_USER_QUERY = """
SELECT username, email
FROM user_auth
WHERE
username='{}' OR 
email='{}'
"""


class CheckUserIndices(IntEnum):
    """Tuple indices for the associated query"""

    USERNAME = 0
    EMAIL = 1


CHECK_USER_ID_QUERY = """
SELECT user_id
FROM user_auth
WHERE
user_id='{}'
"""


class CheckUserIdIndices(IntEnum):
    """Tuple indices for the associated query"""

    ID = 0


NEW_USER_QUERY = """
INSERT INTO user_auth
(username, email, user_id, nickname, password_hash)
VALUES
('{}', '{}', '{}', '{}', '{}')
"""


CHECK_USER_AUTH_QUERY = """
SELECT user_id, username, nickname, email
FROM user_auth
WHERE
username='{}' AND password_hash='{}'
"""


class CheckUserAuthIndices(IntEnum):
    """Tuple indices for the associated query"""

    ID = 0
    USERNAME = 1
    NICKNAME = 2
    EMAIL = 3


UPDATE_PASSWORD_QUERY = """
UPDATE user_auth
SET password_hash='{}' WHERE user_id='{}'
"""

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS user_auth(
    user_id text PRIMARY KEY,
    username text NOT NULL UNIQUE,
    email text NOT NULL UNIQUE,
    nickname text NOT NULL,
    password_hash text NOT NULL
  )
"""

MAX_USER_ID_ATTEMPTS = 5
RANDOMIZATION_SCALE = 1000000000


class UserAuthData(NamedTuple):
    """User authentication data"""

    user_id: str
    username: str
    nickname: str
    email: str


class AuthenticationServerHandler:
    def __init__(self, url: str, port: int, db: str, username: str, password: str) -> None:
        self._engine = create_engine(
            'postgres://{}:{}@{}:{}/{}'.format(username, password, url, port, db)
        )

    def create_database(self) -> None:
        conn = self._engine.connect()
        conn.execute('commit')
        conn.execute('CREATE DATABASE chupacabra')
        conn.close()

    def create_table(self) -> None:
        self._engine.execute(CREATE_TABLE_QUERY)

    def add_new_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        nickname: str
    ) -> Tuple[bool, str]:
        results = self._engine.execute(
            CHECK_USER_QUERY.format(username, email)
        ).fetchall()
        for result in results:
            if result[CheckUserIndices.USERNAME.value] == username:
                return False, 'This username has already been chosen.'
            if result[CheckUserIndices.EMAIL.value] == email:
                return False, 'This email has already been used.'

        user_id = ''
        time = int(arrow.utcnow().float_timestamp * RANDOMIZATION_SCALE) % RANDOMIZATION_SCALE
        random_state = np.random.RandomState(time)
        for _ in range(MAX_USER_ID_ATTEMPTS):
            proposed_user_id = str(random_state.randint(RANDOMIZATION_SCALE))
            results = self._engine.execute(
                CHECK_USER_ID_QUERY.format(proposed_user_id)
            ).fetchone()
            if not results:
                user_id = proposed_user_id
                break

        if not user_id:
            return False, 'Could not create a new user. Please try again.'

        self._engine.execute(
            NEW_USER_QUERY.format(username, email, user_id, nickname, password_hash)
        )

        return True, 'Success'

    def check_user(self, username: str, password_hash: str) -> Optional[UserAuthData]:
        user_data = self._engine.execute(
            CHECK_USER_AUTH_QUERY.format(username, password_hash)
        ).fetchone()
        if not user_data != 1:
            return None

        print(user_data)

        user_auth_data = UserAuthData(
            user_id=user_data[CheckUserAuthIndices.ID.value],
            username=user_data[CheckUserAuthIndices.USERNAME.value],
            nickname=user_data[CheckUserAuthIndices.NICKNAME.value],
            email=user_data[CheckUserAuthIndices.EMAIL.value]
        )
        return user_auth_data
