from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from httpx import ASGITransport, AsyncClient

from database import get_db
from core.security import USERS
from main import app


class MockCollection:
    def __init__(self):
        self.data = []

    def find(self, query=None):
        query = query or {}
        result = []
        for book in self.data:
            match = True
            if "status" in query and book.get("status") != query["status"]:
                match = False
            if "author" in query:
                import re

                pattern = query["author"]["$regex"]
                if not re.search(pattern, book.get("author", ""), re.IGNORECASE):
                    match = False
            if match:
                result.append(dict(book))

        mock_cursor = MagicMock()

        def sort_func(field, direction):
            result.sort(key=lambda item: item.get(field), reverse=direction == -1)
            return mock_cursor

        mock_cursor.sort.side_effect = sort_func
        mock_cursor.skip.return_value = mock_cursor

        def limit_func(limit):
            limited = MagicMock()
            limited.to_list = AsyncMock(return_value=result[:limit])
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
        self.data = [book for book in self.data if book.get("_id") != query.get("_id")]
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


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_db():
    mock_db.books.data.clear()
    for username in list(USERS):
        if username != "student":
            del USERS[username]
    yield
    mock_db.books.data.clear()
    for username in list(USERS):
        if username != "student":
            del USERS[username]


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
async def auth_headers(client):
    response = await client.post(
        "/auth/login",
        json={"username": "student", "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_register_returns_tokens_and_creates_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "new_student",
            "password": "strong123",
            "full_name": "New Student",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]

    me = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["username"] == "new_student"


@pytest.mark.anyio
async def test_register_existing_username_returns_409(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "student",
            "password": "strong123",
            "full_name": "Duplicate Student",
        },
    )

    assert response.status_code == 409


@pytest.mark.anyio
async def test_login_returns_access_and_refresh_tokens(client):
    response = await client.post(
        "/auth/login",
        json={"username": "student", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.anyio
async def test_login_with_wrong_password_returns_401(client):
    response = await client.post(
        "/auth/login",
        json={"username": "student", "password": "wrong"},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_refresh_token_flow_returns_new_access_token(client):
    login = await client.post(
        "/auth/login",
        json={"username": "student", "password": "password123"},
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


@pytest.mark.anyio
async def test_books_are_protected_without_token(client):
    response = await client.get("/books/")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_all_books_empty(client, auth_headers):
    response = await client.get("/books/", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.anyio
async def test_create_book(client, auth_headers):
    payload = {
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "description": "Збірка поетичних творів",
        "status": "available",
        "year": 1840,
    }

    response = await client.post("/books/", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Кобзар"
    assert "id" in data


@pytest.mark.anyio
async def test_get_book_by_id(client, auth_headers):
    payload = {"title": "Кобзар", "author": "Шевченко", "year": 1840}
    create = await client.post("/books/", json=payload, headers=auth_headers)
    book_id = create.json()["id"]

    response = await client.get(f"/books/{book_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == book_id


@pytest.mark.anyio
async def test_get_book_not_found(client, auth_headers):
    response = await client.get(f"/books/{ObjectId()}", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_book(client, auth_headers):
    payload = {"title": "Кобзар", "author": "Шевченко", "year": 1840}
    create = await client.post("/books/", json=payload, headers=auth_headers)
    book_id = create.json()["id"]

    response = await client.delete(f"/books/{book_id}", headers=auth_headers)

    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_idempotent(client, auth_headers):
    response = await client.delete(f"/books/{ObjectId()}", headers=auth_headers)

    assert response.status_code == 204


@pytest.mark.anyio
async def test_filter_by_status(client, auth_headers):
    await client.post(
        "/books/",
        json={"title": "Книга 1", "author": "Автор", "year": 2000, "status": "available"},
        headers=auth_headers,
    )
    await client.post(
        "/books/",
        json={"title": "Книга 2", "author": "Автор", "year": 2001, "status": "issued"},
        headers=auth_headers,
    )

    response = await client.get("/books/?status=available", headers=auth_headers)
    data = response.json()["items"]

    assert all(book["status"] == "available" for book in data)


@pytest.mark.anyio
async def test_filter_by_author(client, auth_headers):
    await client.post(
        "/books/",
        json={"title": "Кобзар", "author": "Шевченко", "year": 1840},
        headers=auth_headers,
    )
    await client.post(
        "/books/",
        json={"title": "Інша", "author": "Франко", "year": 1900},
        headers=auth_headers,
    )

    response = await client.get("/books/?author=Шевченко", headers=auth_headers)
    data = response.json()["items"]

    assert len(data) == 1
    assert "Шевченко" in data[0]["author"]


@pytest.mark.anyio
async def test_pagination(client, auth_headers):
    for index in range(5):
        await client.post(
            "/books/",
            json={"title": f"Книга {index}", "author": "Автор", "year": 2000 + index},
            headers=auth_headers,
        )

    response = await client.get("/books/?limit=2&offset=0", headers=auth_headers)

    assert len(response.json()["items"]) == 2


@pytest.mark.anyio
async def test_create_book_invalid(client, auth_headers):
    response = await client.post(
        "/books/",
        json={"author": "Автор", "year": 2000},
        headers=auth_headers,
    )

    assert response.status_code == 422
