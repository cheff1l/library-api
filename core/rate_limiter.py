import os
import time
from uuid import uuid4

from fastapi import HTTPException, Request, status
from redis import asyncio as redis

from core.security import decode_token


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

RATE_LIMITS = {
    "anonymous": (2, 60),
    "authenticated": (10, 60),
}

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

EXCLUDED_PATH_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
)


def is_excluded_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in EXCLUDED_PATH_PREFIXES)


def get_bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def get_client_host(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown-client"


def get_rate_limit_identity(request: Request) -> tuple[str, str]:
    token = get_bearer_token(request)
    if token:
        try:
            payload = decode_token(token, expected_type="access")
            return f"user:{payload['sub']}", "authenticated"
        except HTTPException:
            pass

    return f"ip:{get_client_host(request)}", "anonymous"


async def rate_limit(request: Request) -> None:
    if is_excluded_path(request.url.path):
        return

    identity, limit_type = get_rate_limit_identity(request)
    limit, period = RATE_LIMITS[limit_type]
    now = int(time.time())
    window_start = now - period
    key = f"rate_limit:{limit_type}:{identity}"

    await redis_client.zremrangebyscore(key, 0, window_start)
    request_count = await redis_client.zcard(key)

    if request_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for {limit_type} user",
            headers={"Retry-After": str(period)},
        )

    await redis_client.zadd(key, {f"{now}:{uuid4()}": now})
    await redis_client.expire(key, period)
