from fastapi import FastAPI

from api.auth import router as auth_router
from api.books import router as books_router

app = FastAPI(
    title="Library API",
    description="REST API для бібліотеки книг з JWT access/refresh authentication.",
    version="6.0.0",
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(books_router, prefix="/books", tags=["Books"])


@app.get("/")
async def root():
    return {"message": "Library API is running!", "docs": "/docs"}
