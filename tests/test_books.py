import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app
from database import get_db
from models.books import Base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(DATABASE_URL)
AsyncSessionTest = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with AsyncSessionTest() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_get_all_books_empty(client):
    response = await client.get("/books/")
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["next_cursor"] is None


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
    response = await client.get("/books/non-existent-id")
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
    response = await client.delete("/books/non-existent-id")
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
async def test_cursor_pagination(client):
    for i in range(5):
        await client.post("/books/", json={"title": f"Книга {i}", "author": "Автор", "year": 2000 + i})

    first = await client.get("/books/?limit=2")
    data = first.json()
    assert len(data["items"]) == 2
    assert data["next_cursor"] is not None

    second = await client.get(f"/books/?limit=2&cursor={data['next_cursor']}")
    data2 = second.json()
    assert len(data2["items"]) == 2

    first_ids = [b["id"] for b in data["items"]]
    second_ids = [b["id"] for b in data2["items"]]
    assert not any(i in second_ids for i in first_ids)


@pytest.mark.anyio
async def test_create_book_invalid(client):
    response = await client.post("/books/", json={"author": "Автор", "year": 2000})
    assert response.status_code == 422