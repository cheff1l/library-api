from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from main import create_app


class MockCursor:
    def __init__(self, data):
        self.data = data
        self.offset = 0
        self.limit_value = len(data)

    def sort(self, field, direction):
        self.data = sorted(self.data, key=lambda item: item.get(field), reverse=direction == -1)
        return self

    def skip(self, offset):
        self.offset = offset
        return self

    def limit(self, limit):
        self.limit_value = limit
        return self

    def __iter__(self):
        return iter(self.data[self.offset:self.offset + self.limit_value])


class MockCollection:
    def __init__(self):
        self.data = []

    def _matches(self, book, query):
        if "status" in query and book.get("status") != query["status"]:
            return False
        if "author" in query:
            import re

            pattern = query["author"]["$regex"]
            if not re.search(pattern, book.get("author", ""), re.IGNORECASE):
                return False
        return True

    def find(self, query=None):
        query = query or {}
        return MockCursor([dict(book) for book in self.data if self._matches(book, query)])

    def count_documents(self, query=None):
        query = query or {}
        return len([book for book in self.data if self._matches(book, query)])

    def find_one(self, query):
        for book in self.data:
            if book.get("_id") == query.get("_id"):
                return dict(book)
        return None

    def insert_one(self, doc):
        stored = dict(doc)
        stored["_id"] = ObjectId()
        self.data.append(stored)
        result = MagicMock()
        result.inserted_id = stored["_id"]
        return result

    def update_one(self, query, update):
        result = MagicMock()
        result.matched_count = 0
        for book in self.data:
            if book.get("_id") == query.get("_id"):
                book.update(update["$set"])
                result.matched_count = 1
                break
        return result

    def delete_one(self, query):
        before = len(self.data)
        self.data = [book for book in self.data if book.get("_id") != query.get("_id")]
        result = MagicMock()
        result.deleted_count = before - len(self.data)
        return result


class MockDB:
    def __init__(self):
        self.books = MockCollection()


@pytest.fixture()
def mock_db():
    return MockDB()


@pytest.fixture()
def client(mock_db):
    app = create_app({"TESTING": True, "DB": mock_db})
    return app.test_client()


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["swagger"] == "/apidocs/"


def test_swagger_spec_is_available(client):
    response = client.get("/apispec_1.json")
    assert response.status_code == 200
    assert "/books" in response.get_json()["paths"]


def test_get_all_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.get_json()["items"] == []


def test_create_book(client):
    payload = {
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "description": "Збірка поетичних творів",
        "status": "available",
        "year": 1840,
    }

    response = client.post("/books", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Кобзар"
    assert data["status"] == "available"
    assert "id" in data


def test_get_book_by_id(client):
    create = client.post("/books", json={"title": "Кобзар", "author": "Шевченко", "year": 1840})
    book_id = create.get_json()["id"]

    response = client.get(f"/books/{book_id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == book_id


def test_get_book_not_found(client):
    response = client.get(f"/books/{ObjectId()}")
    assert response.status_code == 404


def test_get_book_with_invalid_id_returns_404(client):
    response = client.get("/books/not-a-valid-id")
    assert response.status_code == 404


def test_update_book(client):
    create = client.post("/books", json={"title": "Кобзар", "author": "Шевченко", "year": 1840})
    book_id = create.get_json()["id"]

    response = client.put(f"/books/{book_id}", json={"status": "issued", "year": 1841})

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "issued"
    assert data["year"] == 1841


def test_delete_book(client):
    create = client.post("/books", json={"title": "Кобзар", "author": "Шевченко", "year": 1840})
    book_id = create.get_json()["id"]

    response = client.delete(f"/books/{book_id}")

    assert response.status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404


def test_delete_is_idempotent(client):
    response = client.delete(f"/books/{ObjectId()}")
    assert response.status_code == 204


def test_filter_by_status(client):
    client.post("/books", json={"title": "Книга 1", "author": "Автор", "year": 2000, "status": "available"})
    client.post("/books", json={"title": "Книга 2", "author": "Автор", "year": 2001, "status": "issued"})

    response = client.get("/books?status=available")
    data = response.get_json()["items"]

    assert len(data) == 1
    assert data[0]["status"] == "available"


def test_filter_by_author(client):
    client.post("/books", json={"title": "Кобзар", "author": "Шевченко", "year": 1840})
    client.post("/books", json={"title": "Інша", "author": "Франко", "year": 1900})

    response = client.get("/books?author=Шевченко")
    data = response.get_json()["items"]

    assert len(data) == 1
    assert "Шевченко" in data[0]["author"]


def test_sort_and_pagination(client):
    for index, title in enumerate(["C", "A", "B"]):
        client.post("/books", json={"title": title, "author": "Автор", "year": 2000 + index})

    response = client.get("/books?sort_by=title&sort_order=asc&limit=2&offset=0")
    data = response.get_json()

    assert [book["title"] for book in data["items"]] == ["A", "B"]
    assert data["total"] == 3


def test_create_book_invalid(client):
    response = client.post("/books", json={"author": "Автор", "year": 2000})

    assert response.status_code == 400
    assert "title" in response.get_json()["errors"]
