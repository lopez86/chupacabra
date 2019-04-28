from enum import IntEnum
from typing import NamedTuple, Optional, Tuple

import arrow
import numpy as np
import sqlalchemy


# Check if a username or email is already taken
CHECK_USER_QUERY = sqlalchemy.text("""
SELECT username, email
FROM user_auth
WHERE
  username=:username OR
  email=:email
""")


class CheckUserIndices(IntEnum):
    """Tuple indices for the associated query"""

    USERNAME = 0
    EMAIL = 1


# Check if a user id is already taken
CHECK_USER_ID_QUERY = sqlalchemy.text("""
SELECT user_id
FROM user_auth
WHERE
  user_id=:user_id
""")


class CheckUserIdIndices(IntEnum):
    """Tuple indices for the associated query"""

    ID = 0


# Insert a new user into the table
NEW_USER_QUERY = sqlalchemy.text("""
INSERT INTO user_auth
(username, email, user_id, nickname, password_hash)
VALUES
(:username, :email, :user_id, :nickname, :password_hash)
""")


# Check if a user has given the correct password
CHECK_USER_AUTH_QUERY = sqlalchemy.text("""
SELECT user_id, username, nickname, email
FROM user_auth
WHERE
  username=:username AND
  password_hash=:password_hash
""")


class CheckUserAuthIndices(IntEnum):
    """Tuple indices for the associated query"""

    ID = 0
    USERNAME = 1
    NICKNAME = 2
    EMAIL = 3


# Update a user's password
UPDATE_PASSWORD_QUERY = sqlalchemy.text("""
UPDATE user_auth
SET password_hash=:password_hash
WHERE user_id=:user_id
""")

# Create a new user authentication table if it doesn't exist
CREATE_TABLE_QUERY = sqlalchemy.text("""
CREATE TABLE IF NOT EXISTS user_auth(
    user_id text PRIMARY KEY,
    username text NOT NULL UNIQUE,
    email text NOT NULL UNIQUE,
    nickname text NOT NULL,
    password_hash text NOT NULL
  )
""")

# If a proposed user id is taken, retry this many times before failing
MAX_USER_ID_ATTEMPTS = 5
# User IDs are random ints right now. They are less than this value
RANDOMIZATION_SCALE = 1000000000


class UserAuthData(NamedTuple):
    """User authentication data"""

    user_id: str
    username: str
    nickname: str
    email: str


class AuthenticationServerHandler:
    def __init__(
        self,
        url: str,
        port: int,
        db: str,
        username: str,
        password: str
    ) -> None:
        """Handler for a basic postgres database holding user authentication data.

        When deployed in the wild, the input values should be treated as secrets.

        Args:
            url: str, the base url for the server
            port: int, the port for the server
            db: str, the database name,
            username: str, the username for the database (should be a secret)
            password: str, the password for the database (definitely a secret)
        """
        self._engine = sqlalchemy.create_engine(
            'postgres://{}:{}@{}:{}/{}'.format(username, password, url, port, db)
        )

    def create_database(self) -> None:
        """Create the database if it doesn't exist."""
        conn = self._engine.connect()
        conn.execute('commit')
        conn.execute('CREATE DATABASE chupacabra')
        conn.close()

    def create_table(self) -> None:
        """Create the user authentication table if it doesn't exist."""
        self._engine.execute(CREATE_TABLE_QUERY)

    def add_new_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        nickname: str
    ) -> Tuple[bool, str]:
        """Try to add a new user to the database.

        The username and nickname are meant to be public within the platform
        and may be exposed to other users by games.

        Args:
            username: str, the proposed username (unique)
            email: str, the user's email (unique)
            password_hash: str, a hash of the proposed password
            nickname: str, the user's nickname (not necessarily unique)

        Returns:
            2-tuple of:
            bool: True for success, False for failure
            str: Any messages to be relayed back to the user.
        """
        # First check if the username or email has already been used
        results = self._engine.execute(
            CHECK_USER_QUERY,
            username=username,
            email=email
        ).fetchall()
        for result in results:
            if result[CheckUserIndices.USERNAME.value] == username:
                return False, 'This username has already been chosen.'
            if result[CheckUserIndices.EMAIL.value] == email:
                return False, 'This email has already been used.'

        # Now set up the random state to get a user id
        user_id = ''
        time = int(arrow.utcnow().float_timestamp * RANDOMIZATION_SCALE) % RANDOMIZATION_SCALE
        random_state = np.random.RandomState(time)
        # Propose a user id and check if it's available. On some number of failures
        # just fail.
        for _ in range(MAX_USER_ID_ATTEMPTS):
            proposed_user_id = str(random_state.randint(RANDOMIZATION_SCALE))
            results = self._engine.execute(
                CHECK_USER_ID_QUERY,
                user_id=proposed_user_id
            ).fetchone()
            if not results:
                user_id = proposed_user_id
                break

        # We didn't get a good id in enough tries
        if not user_id:
            return False, 'Could not create a new user. Please try again.'

        # Add the user
        self._engine.execute(
            NEW_USER_QUERY,
            username=username,
            email=email,
            user_id=user_id,
            nickname=nickname,
            password_hash=password_hash
        )

        return True, 'Success'

    def check_user_creds(
        self,
        username: str,
        password_hash: str
    ) -> Optional[UserAuthData]:
        """Check if the user passed in valid credentials

        Args:
            username: str, the username
            password_hash: str, a hash of the original password entered
                by the user

        Returns:
            maybe(UserAuthData), None if the check fails
        """
        user_data = self._engine.execute(
            CHECK_USER_AUTH_QUERY,
            username=username,
            password_hash=password_hash
        ).fetchone()
        if user_data is None:
            return None

        user_auth_data = UserAuthData(
            user_id=user_data[CheckUserAuthIndices.ID.value],
            username=user_data[CheckUserAuthIndices.USERNAME.value],
            nickname=user_data[CheckUserAuthIndices.NICKNAME.value],
            email=user_data[CheckUserAuthIndices.EMAIL.value]
        )
        return user_auth_data
