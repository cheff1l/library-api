from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-for-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

security_scheme = HTTPBearer(auto_error=False)

# Demo user storage for the lab. In a real project this data would be stored in DB.
USERS = {
    "student": {
        "username": "student",
        "full_name": "Library API Student",
        "password_hash": hashlib.sha256("password123".encode("utf-8")).hexdigest(),
    }
}


def verify_password(plain_password: str, password_hash: str) -> bool:
    current_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(current_hash, password_hash)


def authenticate_user(username: str, password: str):
    user = USERS.get(username)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return {"username": user["username"], "full_name": user["full_name"]}


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_access_token(username: str) -> str:
    return create_token(
        subject=username,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(username: str) -> str:
    return create_token(
        subject=username,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str) -> dict:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise credentials_error from exc

    username = payload.get("sub")
    token_type = payload.get("type")
    if not username or token_type != expected_type or username not in USERS:
        raise credentials_error

    return payload


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)]
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header with Bearer token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials, expected_type="access")
    username = payload["sub"]
    user = USERS[username]
    return {"username": user["username"], "full_name": user["full_name"]}
