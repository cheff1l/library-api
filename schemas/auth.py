from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., examples=["student"])
    password: str = Field(..., examples=["password123"])


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    username: str
    full_name: str
