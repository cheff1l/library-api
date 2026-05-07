from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., examples=["student"])
    password: str = Field(..., examples=["password123"])


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["new_student"])
    password: str = Field(..., min_length=6, max_length=128, examples=["strong123"])
    full_name: str = Field(..., min_length=1, max_length=100, examples=["New Student"])


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
