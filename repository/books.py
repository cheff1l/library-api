from typing import List, Dict, Any, Optional
from models.books import books_db


class BookRepository:

    async def get_all(
        self,
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        result = list(books_db)  # копія списку

        if status:
            result = [b for b in result if b["status"] == status]

        if author:
            result = [b for b in result if author.lower() in b["author"].lower()]

        if sort_by in ("title", "year"):
            reverse = sort_order == "desc"
            result = sorted(result, key=lambda b: b[sort_by], reverse=reverse)

        return result

    async def get_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        for book in books_db:
            if book["id"] == book_id:
                return book
        return None

    async def create(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        books_db.append(book_data)
        return book_data

    async def delete(self, book_id: str) -> bool:
        for i, book in enumerate(books_db):
            if book["id"] == book_id:
                books_db.pop(i)
                return True
        return False
