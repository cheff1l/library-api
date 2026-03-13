from typing import Optional
from bson import ObjectId
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
        return await cursor.to_list(length=limit)

    async def get_by_id(self, book_id: str):
        return await self.collection.find_one({"_id": ObjectId(book_id)})

    async def create(self, book_data: dict):
        result = await self.collection.insert_one(book_data)
        return await self.collection.find_one({"_id": result.inserted_id})

    async def delete(self, book_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count