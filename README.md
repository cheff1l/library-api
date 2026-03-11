# Library API — FastAPI

REST API для бібліотеки книг, розроблений на FastAPI з використанням Python async/await.

## Запуск проєкту

```bash
# 1. Встановити залежності
pip install -r requirements.txt

# 2. Запустити сервер
uvicorn main:app --reload

# 3. Відкрити документацію Swagger
# http://127.0.0.1:8000/docs
```

## Запуск тестів

```bash
pytest tests/test_books.py -v
```

## Структура проєкту

```
library_api/
├── main.py              # Точка входу FastAPI додатку
├── requirements.txt     # Залежності
├── api/
│   └── books.py         # Ендпоінти (маршрути)
├── schemas/
│   └── books.py         # Pydantic схеми (валідація)
├── services/
│   └── books.py         # Бізнес-логіка
├── repository/
│   └── books.py         # Взаємодія зі сховищем даних
├── models/
│   └── books.py         # Дані (List[Dict])
└── tests/
    └── test_books.py    # Юніт тести (25 тестів)
```

## Ендпоінти

| Метод | URL | Опис | HTTP статус |
|-------|-----|------|-------------|
| GET | /books/ | Всі книги (з фільтрацією/сортуванням) | 200 |
| GET | /books/{id} | Книга по ID | 200 / 404 |
| POST | /books/ | Додати книгу | 201 / 422 |
| DELETE | /books/{id} | Видалити книгу (ідемпотентно) | 204 |

## Фільтрація та сортування

```
GET /books/?status=available
GET /books/?status=issued
GET /books/?author=Шевченко
GET /books/?sort_by=year&sort_order=desc
GET /books/?sort_by=title&sort_order=asc
GET /books/?status=available&author=Тарас&sort_by=year
```

## Статуси книг

- `available` — наявна в бібліотеці
- `issued` — видана комусь

## Ідемпотентний DELETE

DELETE завжди повертає **204** — навіть якщо книги не існує.
Це означає: повторний виклик дає той самий результат.
