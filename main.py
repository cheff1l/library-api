from fastapi import FastAPI
from api.books import router as books_router

app = FastAPI(
    title="Library API",
    description="REST API для бібліотеки книг",
    version="3.0.0"
)

app.include_router(books_router, prefix="/books", tags=["Books"])


@app.get("/")
async def root():
    return {"message": "Library API is running!"}