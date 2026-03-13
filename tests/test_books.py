import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from main import app
from database import get_db
from services.books import BookService


class MockCollection:
    def __init__(self):
        self.data = []

    def find(self, query={}):
        result = []
        for b in self.data:
            match = True
            if "status" in query and b.get("status") != query["status"]:
                match = False
            if "author" in query:
                import re
                pattern = query["author"]["$regex"]
                if not re.search(pattern, b.get("author", ""), re.IGNORECASE):
                    match = False
            if match:
                result.append(dict(b))

        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor

        def limit_func(n):
            limited = MagicMock()
            limited.to_list = AsyncMock(return_value=result[:n])
            return limited

        mock_cursor.limit.side_effect = limit_func
        return mock_cursor

    async def find_one(self, query):
        for book in self.data:
            if "_id" in query and book.get("_id") == query["_id"]:
                return dict(book)
        return None

    async def insert_one(self, doc):
        doc["_id"] = ObjectId()
        self.data.append(dict(doc))
        result = MagicMock()
        result.inserted_id = doc["_id"]
        return result

    async def delete_one(self, query):
        before = len(self.data)
        self.data = [b for b in self.data if b.get("_id") != query.get("_id")]
        result = MagicMock()
        result.deleted_count = before - len(self.data)
        return result


class MockDB:
    def __init__(self):
        self.books = MockCollection()


mock_db = MockDB()


def override_get_db():
    return mock_db


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    mock_db.books.data.clear()
    yield
    mock_db.books.data.clear()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_get_all_books_empty(client):
    response = await client.get("/books/")
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.anyio
async def test_create_book(client):
    payload = {
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "description": "Збірка поетичних творів",
        "status": "available",
        "year": 1840
    }
    response = await client.post("/books/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Кобзар"
    assert "id" in data


@pytest.mark.anyio
async def test_get_book_by_id(client):
    payload = {"title": "Кобзар", "author": "Шевченко", "year": 1840}
    create = await client.post("/books/", json=payload)
    book_id = create.json()["id"]
    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id


@pytest.mark.anyio
async def test_get_book_not_found(client):
    response = await client.get(f"/books/{str(ObjectId())}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_book(client):
    payload = {"title": "Кобзар", "author": "Шевченко", "year": 1840}
    create = await client.post("/books/", json=payload)
    book_id = create.json()["id"]
    response = await client.delete(f"/books/{book_id}")
    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_idempotent(client):
    response = await client.delete(f"/books/{str(ObjectId())}")
    assert response.status_code == 204


@pytest.mark.anyio
async def test_filter_by_status(client):
    await client.post("/books/", json={"title": "Книга 1", "author": "Автор", "year": 2000, "status": "available"})
    await client.post("/books/", json={"title": "Книга 2", "author": "Автор", "year": 2001, "status": "issued"})
    response = await client.get("/books/?status=available")
    data = response.json()["items"]
    assert all(b["status"] == "available" for b in data)


@pytest.mark.anyio
async def test_filter_by_author(client):
    await client.post("/books/", json={"title": "Кобзар", "author": "Шевченко", "year": 1840})
    await client.post("/books/", json={"title": "Інша", "author": "Франко", "year": 1900})
    response = await client.get("/books/?author=Шевченко")
    data = response.json()["items"]
    assert len(data) == 1
    assert "Шевченко" in data[0]["author"]


@pytest.mark.anyio
async def test_pagination(client):
    for i in range(5):
        await client.post("/books/", json={"title": f"Книга {i}", "author": "Автор", "year": 2000 + i})
    response = await client.get("/books/?limit=2&offset=0")
    assert len(response.json()["items"]) == 2


@pytest.mark.anyio
async def test_create_book_invalid(client):
    response = await client.post("/books/", json={"author": "Автор", "year": 2000})
    assert response.status_code == 422