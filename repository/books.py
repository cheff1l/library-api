import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.books import Book, BookStatus


class BookRepository:

    async def get_all(
        self,
        session: AsyncSession,
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ):
        query = select(Book)

        if status:
            query = query.filter(Book.status == BookStatus(status))

        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))

        if sort_by == "title":
            query = query.order_by(Book.title.desc() if sort_order == "desc" else Book.title)
        elif sort_by == "year":
            query = query.order_by(Book.year.desc() if sort_order == "desc" else Book.year)

        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, book_id: str):
        result = await session.execute(select(Book).filter(Book.id == book_id))
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, book_data: dict):
        book = Book(
            id=str(uuid.uuid4()),
            **book_data
        )
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    async def delete(self, session: AsyncSession, book_id: str):
        book = await self.get_by_id(session, book_id)
        if book:
            await session.delete(book)
            await session.commit()
        return True