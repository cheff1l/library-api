from fastapi import FastAPI
from api.books import router as books_router
from database import engine
from models.books import Base


async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Library API",
    description="REST API для бібліотеки книг",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(books_router, prefix="/books", tags=["Books"])


@app.get("/")
async def root():
    return {"message": "Library API is running!"}