import uuid
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


class BookRepository:

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.books

    async def get_all(
        self,
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ):
        query = {}

        if status:
            query["status"] = status

        if author:
            query["author"] = {"$regex": author, "$options": "i"}

        cursor = self.collection.find(query)

        if sort_by in ("title", "year"):
            direction = -1 if sort_order == "desc" else 1
            cursor = cursor.sort(sort_by, direction)

        cursor = cursor.skip(offset).limit(limit)
        books = await cursor.to_list(length=limit)

        for book in books:
            if "_id" in book:
                book["id"] = str(book["_id"])
                del book["_id"]

        return books

    async def get_by_id(self, book_id: str):
        book = await self.collection.find_one({"id": book_id})
        if book:
            if "_id" in book:
                del book["_id"]
        return book

    async def create(self, book_data: dict):
        book_data["id"] = str(uuid.uuid4())
        await self.collection.insert_one(book_data)
        if "_id" in book_data:
            del book_data["_id"]
        return book_data

    async def delete(self, book_id: str):
        await self.collection.delete_one({"id": book_id})
        return True