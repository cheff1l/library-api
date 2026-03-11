from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repository.books import BookRepository
from schemas.books import BookCreate


class BookService:

    def __init__(self):
        self.repo = BookRepository()

    async def get_all_books(
        self,
        session: AsyncSession,
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ):
        return await self.repo.get_all(
            session=session,
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )

    async def get_book_by_id(self, session: AsyncSession, book_id: str):
        return await self.repo.get_by_id(session, book_id)

    async def create_book(self, session: AsyncSession, book_data: BookCreate):
        data = {
            "title": book_data.title,
            "author": book_data.author,
            "description": book_data.description,
            "status": book_data.status,
            "year": book_data.year
        }
        return await self.repo.create(session, data)

    async def delete_book(self, session: AsyncSession, book_id: str):
        return await self.repo.delete(session, book_id)