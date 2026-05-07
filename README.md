# Library API - Flask RESTful

REST API для керування книгами бібліотеки. Проект реалізовано на Flask з використанням `Flask-RESTful`, а Swagger/OpenAPI документацію налаштовано через `flasgger`.

## Можливості

- отримання списку книг;
- фільтрація за статусом і автором;
- сортування за назвою або роком;
- пагінація через `limit` та `offset`;
- отримання книги за `id`;
- створення книги;
- оновлення книги;
- ідемпотентне видалення книги;
- Swagger UI за адресою `/apidocs/`.

## Структура проекту

```text
library-api-lab4-v2/
|-- main.py              # створення Flask app, підключення Swagger і ресурсів
|-- database.py          # підключення до MongoDB через PyMongo
|-- requirements.txt     # залежності проекту
|-- api/
|   `-- books.py         # Flask-RESTful ресурси та Swagger-описи
|-- schemas/
|   `-- books.py         # валідація payload і схеми документації
|-- services/
|   `-- books.py         # бізнес-логіка
|-- repository/
|   `-- books.py         # робота з MongoDB
`-- tests/
    `-- test_books.py    # тести API без реальної MongoDB
```

## Запуск локально

```bash
pip install -r requirements.txt
python main.py
```

Сервер буде доступний на `http://127.0.0.1:8000`.

Swagger UI: `http://127.0.0.1:8000/apidocs/`

OpenAPI JSON: `http://127.0.0.1:8000/apispec_1.json`

## Запуск через Docker Compose

```bash
docker compose up --build
```

Compose піднімає два сервіси:

- `mongo_db` - MongoDB;
- `api` - Flask REST API на порті `8000`.

## Змінні середовища

```env
MONGO_URL=mongodb://mongo_admin:password@localhost:27017
MONGO_DB_NAME=books
```

## Основні ендпоінти

| Метод | URL | Опис | Статуси |
| --- | --- | --- | --- |
| GET | `/` | Перевірка роботи API | 200 |
| GET | `/books` | Список книг | 200 / 400 |
| GET | `/books/<id>` | Книга за ID | 200 / 404 |
| POST | `/books` | Створення книги | 201 / 400 |
| PUT | `/books/<id>` | Оновлення книги | 200 / 400 / 404 |
| DELETE | `/books/<id>` | Видалення книги | 204 |

## Приклад створення книги

```bash
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Кобзар\",\"author\":\"Тарас Шевченко\",\"year\":1840,\"status\":\"available\"}"
```

## Приклади фільтрації

```text
GET /books?status=available
GET /books?author=Шевченко
GET /books?sort_by=year&sort_order=desc
GET /books?limit=5&offset=10
```

## Запуск тестів

```bash
pytest -q
```
