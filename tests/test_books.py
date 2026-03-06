

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models.books import books_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    original = [
        {
            "id": "test-id-0001",
            "title": "Кобзар",
            "author": "Тарас Шевченко",
            "description": "Збірка поетичних творів",
            "status": "available",
            "year": 1840
        },
        {
            "id": "test-id-0002",
            "title": "Тіні забутих предків",
            "author": "Михайло Коцюбинський",
            "description": "Повість про гуцульське кохання",
            "status": "issued",
            "year": 1911
        }
    ]
    books_db.clear()
    books_db.extend(original)
    yield
    books_db.clear()
    books_db.extend(original)


class TestGetAllBooks:

    def test_get_all_books_returns_200(self):
        response = client.get("/books/")
        assert response.status_code == 200

    def test_get_all_books_returns_list(self):
        response = client.get("/books/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_filter_by_status_available(self):
        response = client.get("/books/?status=available")
        data = response.json()
        assert all(b["status"] == "available" for b in data)

    def test_filter_by_status_issued(self):
        response = client.get("/books/?status=issued")
        data = response.json()
        assert all(b["status"] == "issued" for b in data)

    def test_filter_by_author(self):
        response = client.get("/books/?author=Шевченко")
        data = response.json()
        assert len(data) == 1
        assert "Шевченко" in data[0]["author"]

    def test_filter_by_author_case_insensitive(self):
        response = client.get("/books/?author=шевченко")
        data = response.json()
        assert len(data) == 1

    def test_sort_by_year_asc(self):
        response = client.get("/books/?sort_by=year&sort_order=asc")
        data = response.json()
        years = [b["year"] for b in data]
        assert years == sorted(years)

    def test_sort_by_year_desc(self):
        response = client.get("/books/?sort_by=year&sort_order=desc")
        data = response.json()
        years = [b["year"] for b in data]
        assert years == sorted(years, reverse=True)

    def test_sort_by_title(self):
        response = client.get("/books/?sort_by=title&sort_order=asc")
        data = response.json()
        titles = [b["title"] for b in data]
        assert titles == sorted(titles)

    def test_invalid_status_returns_422(self):
        response = client.get("/books/?status=unknown_status")
        assert response.status_code == 422



class TestGetBookById:

    def test_get_existing_book_returns_200(self):
        response = client.get("/books/test-id-0001")
        assert response.status_code == 200

    def test_get_existing_book_returns_correct_data(self):
        response = client.get("/books/test-id-0001")
        data = response.json()
        assert data["id"] == "test-id-0001"
        assert data["title"] == "Кобзар"
        assert data["author"] == "Тарас Шевченко"

    def test_get_nonexistent_book_returns_404(self):
        response = client.get("/books/non-existent-id")
        assert response.status_code == 404

    def test_get_nonexistent_book_returns_detail(self):
        response = client.get("/books/non-existent-id")
        data = response.json()
        assert "detail" in data


class TestCreateBook:

    def test_create_book_returns_201(self):
        payload = {
            "title": "Нова книга",
            "author": "Іван Тест",
            "description": "Опис",
            "status": "available",
            "year": 2020
        }
        response = client.post("/books/", json=payload)
        assert response.status_code == 201

    def test_create_book_returns_data_with_id(self):
        payload = {
            "title": "Книга з UUID",
            "author": "Автор",
            "year": 2021
        }
        response = client.post("/books/", json=payload)
        data = response.json()
        assert "id" in data
        assert len(data["id"]) > 0  # ID не порожній

    def test_create_book_default_status_available(self):
        payload = {
            "title": "Книга без статусу",
            "author": "Автор",
            "year": 2022
        }
        response = client.post("/books/", json=payload)
        data = response.json()
        assert data["status"] == "available"

    def test_create_book_missing_title_returns_422(self):
        payload = {
            "author": "Автор",
            "year": 2020
        }
        response = client.post("/books/", json=payload)
        assert response.status_code == 422

    def test_create_book_missing_author_returns_422(self):
        payload = {
            "title": "Назва",
            "year": 2020
        }
        response = client.post("/books/", json=payload)
        assert response.status_code == 422

    def test_create_book_invalid_year_returns_422(self):
        payload = {
            "title": "Книга",
            "author": "Автор",
            "year": 500  # занадто старий
        }
        response = client.post("/books/", json=payload)
        assert response.status_code == 422

    def test_create_book_invalid_status_returns_422(self):
        payload = {
            "title": "Книга",
            "author": "Автор",
            "year": 2020,
            "status": "lost"  # не існуючий статус
        }
        response = client.post("/books/", json=payload)
        assert response.status_code == 422


class TestDeleteBook:

    def test_delete_existing_book_returns_204(self):
        response = client.delete("/books/test-id-0001")
        assert response.status_code == 204

    def test_delete_existing_book_actually_deletes(self):
        client.delete("/books/test-id-0001")
        response = client.get("/books/test-id-0001")
        assert response.status_code == 404

    def test_delete_nonexistent_book_returns_204(self):
        response = client.delete("/books/non-existent-id")
        assert response.status_code == 204

    def test_delete_same_book_twice_both_204(self):
        first = client.delete("/books/test-id-0001")
        second = client.delete("/books/test-id-0001")
        assert first.status_code == 204
        assert second.status_code == 204
