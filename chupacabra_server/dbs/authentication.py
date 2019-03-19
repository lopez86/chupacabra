from typing import Tuple

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

CHECK_USER_ID_QUERY = """
SELECT user_id
FROM user_auth
WHERE
user_id='{}'

"""

NEW_USER_QUERY = """
INSERT INTO user_auth
(username, email, user_id, nickname, password_hash)
VALUES
('{}', '{}', '{}', '{}', '{}')
"""

CHECK_USER_AUTH_QUERY = """
SELECT username, nickname, user_id
FROM user_auth
WHERE
username='{}' AND password_hash='{}'
"""

UPDATE_PASSWORD_QUERY = """
UPDATE user_auth
SET password_hash='{}' WHERE user_id='{}'
"""

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS user_auth(
    user_id text PRIMARY_KEY,
    username text UNIQUE NOT NULL,
    email text UNIQUE NOT NULL,
    nickname text NOT NULL,
    password_hash text NOT NULL
  )
"""

MAX_USER_ID_ATTEMPTS = 5
RANDOMIZATION_SCALE = 1000000000


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
        )
        for result in results:
            if result['username'] == username:
                return False, 'This username has already been chosen.'
            if result['email'] == email:
                return False, 'This email has already been used.'

        user_id = ''
        time = int(arrow.utcnow().float_timestamp * RANDOMIZATION_SCALE) % RANDOMIZATION_SCALE
        random_state = np.random.RandomState(time)
        for _ in range(MAX_USER_ID_ATTEMPTS):
            proposed_user_id = str(random_state.randint(RANDOMIZATION_SCALE))
            results = self._engine.execute(
                CHECK_USER_ID_QUERY.format(proposed_user_id)
            )
            if not results:
                user_id = proposed_user_id
                break

        if not user_id:
            return False, 'Could not create a new user. Please try again.'

        self._engine.execute(
            NEW_USER_QUERY.format(username, email, nickname, user_id, password_hash)
        )

        return True, 'Success'

