from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from api.auth import router as auth_router
from api.books import router as books_router
from core.rate_limiter import rate_limit

app = FastAPI(
    title="Library API",
    description="REST API для бібліотеки книг з JWT access/refresh authentication та Redis rate limiter.",
    version="7.0.0",
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(books_router, prefix="/books", tags=["Books"])


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        await rate_limit(request)
    except HTTPException as exc:
        if exc.status_code == 429:
            return JSONResponse(
                status_code=429,
                content={"detail": exc.detail},
                headers=exc.headers,
            )
        raise

    return await call_next(request)


@app.get("/")
async def root():
    return {"message": "Library API is running!", "docs": "/docs"}
