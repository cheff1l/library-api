import uuid
from typing import List, Optional, Dict, Any
from repository.books import BookRepository
from schemas.books import BookCreate


class BookService:

    def __init__(self):
        self.repo = BookRepository()

    async def get_all_books(
        self,
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        return await self.repo.get_all(
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order
        )

    async def get_book_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(book_id)

    async def create_book(self, book_data: BookCreate) -> Dict[str, Any]:
        new_book = {
            "id": str(uuid.uuid4()),
            "title": book_data.title,
            "author": book_data.author,
            "description": book_data.description,
            "status": book_data.status.value,
            "year": book_data.year
        }
        return await self.repo.create(new_book)

    async def delete_book(self, book_id: str) -> bool:
        return await self.repo.delete(book_id)
