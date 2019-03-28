CREATE TABLE IF NOT EXISTS user_auth (
    user_id text PRIMARY KEY,
    username text NOT NULL UNIQUE,
    email text NOT NULL UNIQUE,
    nickname text NOT NULL,
    password_hash text NOT NULL
);
