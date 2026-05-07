from fastapi import APIRouter, Depends, HTTPException, status

from core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from schemas.auth import AccessTokenResponse, LoginRequest, RefreshRequest, TokenPair, UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenPair, status_code=200)
async def login(credentials: LoginRequest):
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenPair(
        access_token=create_access_token(user["username"]),
        refresh_token=create_refresh_token(user["username"]),
    )


@router.post("/refresh", response_model=AccessTokenResponse, status_code=200)
async def refresh_token(payload: RefreshRequest):
    decoded = decode_token(payload.refresh_token, expected_type="refresh")
    return AccessTokenResponse(access_token=create_access_token(decoded["sub"]))


@router.get("/me", response_model=UserResponse, status_code=200)
async def get_me(current_user=Depends(get_current_user)):
    return current_user
