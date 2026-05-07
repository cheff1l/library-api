import re

from bson import ObjectId


class BookRepository:
    def __init__(self, db):
        self.collection = db.books

    @staticmethod
    def to_object_id(book_id):
        if not ObjectId.is_valid(book_id):
            raise ValueError("Invalid book id.")
        return ObjectId(book_id)

    def get_all(
        self,
        status=None,
        author=None,
        sort_by=None,
        sort_order="asc",
        limit=10,
        offset=0,
    ):
        query = {}

        if status:
            query["status"] = status

        if author:
            query["author"] = {"$regex": re.escape(author), "$options": "i"}

        total = self.collection.count_documents(query)
        cursor = self.collection.find(query)

        if sort_by in ("title", "year"):
            direction = -1 if sort_order == "desc" else 1
            cursor = cursor.sort(sort_by, direction)

        books = list(cursor.skip(offset).limit(limit))
        return books, total

    def get_by_id(self, book_id):
        return self.collection.find_one({"_id": self.to_object_id(book_id)})

    def create(self, book_data):
        result = self.collection.insert_one(book_data)
        return self.collection.find_one({"_id": result.inserted_id})

    def update(self, book_id, book_data):
        object_id = self.to_object_id(book_id)
        result = self.collection.update_one({"_id": object_id}, {"$set": book_data})
        if result.matched_count == 0:
            return None
        return self.collection.find_one({"_id": object_id})

    def delete(self, book_id):
        return self.collection.delete_one({"_id": self.to_object_id(book_id)}).deleted_count
