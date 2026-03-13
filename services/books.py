from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from repository.books import BookRepository
from schemas.books import BookCreate


class BookService:

    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = BookRepository(db)

    async def get_all_books(
        self,
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ):
        return await self.repo.get_all(
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )

    async def get_book_by_id(self, book_id: str):
        return await self.repo.get_by_id(book_id)

    async def create_book(self, book_data: BookCreate):
        data = {
            "title": book_data.title,
            "author": book_data.author,
            "description": book_data.description,
            "status": book_data.status.value,
            "year": book_data.year
        }
        return await self.repo.create(data)

    async def delete_book(self, book_id: str):
        return await self.repo.delete(book_id)