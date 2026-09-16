from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed_password_bytes = bcrypt.hashpw(pwd_bytes, salt=salt)
    return hashed_password_bytes.decode("utf-8")


def verify_password(input_password: str, hashed_password: str) -> bool:
    input_bytes = input_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(input_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt
