# Library API - Lab 7

Лабораторна робота 7: Rate limiter.

Проект реалізовано на FastAPI. API працює з книгами бібліотеки, має JWT access/refresh authentication з лабораторної 6 і додатково захищений rate limiter-ом на Redis.

## Що реалізовано

- `POST /auth/login` - генерація access token і refresh token;
- `POST /auth/register` - реєстрація нового користувача з одразу виданими токенами;
- `POST /auth/refresh` - генерація нового access token через refresh token;
- `GET /auth/me` - перевірка поточного користувача за access token;
- захист усіх `/books` ендпоінтів через `Authorization: Bearer <access_token>`;
- Redis rate limiter;
- anonymous users: 2 запити за хвилину;
- authenticated users: 10 запитів за хвилину;
- при перевищенні ліміту API повертає `429 Too Many Requests`;
- CRUD-операції читання/створення/видалення книг;
- фільтрація, сортування і пагінація книг;
- Swagger UI через стандартну FastAPI документацію.

## Демо-користувач

```text
username: student
password: password123
```

## Реєстрація нового користувача

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"new_student\",\"password\":\"strong123\",\"full_name\":\"New Student\"}"
```

У відповідь API поверне `access_token` і `refresh_token`, як і після login.

## Запуск через Docker Compose

```bash
docker compose up --build
```

Compose запускає:

- `api` - FastAPI застосунок;
- `mongo_db` - MongoDB для книг;
- `redis` - кеш-сервер для rate limiter.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

## Запуск локально без Docker

Потрібно, щоб MongoDB уже була запущена.

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Як отримати токени

Через login для демо-користувача:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"student\",\"password\":\"password123\"}"
```

У відповідь буде:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

## Як викликати захищений books endpoint

```bash
curl http://127.0.0.1:8000/books/ \
  -H "Authorization: Bearer <access_token>"
```

Без access token `/books` поверне `401 Unauthorized`.

## Rate limiter

Rate limiter реалізовано у файлі:

```text
core/rate_limiter.py
```

Логіка:

- якщо в запиті є валідний `Authorization: Bearer <access_token>`, користувач вважається авторизованим;
- для авторизованого користувача identity = username з JWT;
- якщо токена немає, користувач вважається анонімним;
- для анонімного користувача identity = IP-адреса клієнта;
- для підрахунку використовується Redis sorted set;
- застосовано sliding time window;
- старі записи за межами вікна 60 секунд очищуються;
- якщо ліміт перевищено, повертається `429`.

Ліміти задані так:

```python
RATE_LIMITS = {
    "anonymous": (2, 60),
    "authenticated": (10, 60),
}
```

Тобто:

- анонімний користувач: 2 запити за 60 секунд;
- авторизований користувач: 10 запитів за 60 секунд.

Rate limiter підключений як FastAPI middleware у `main.py`, тому перевірка виконується перед обробкою endpoint.

## Refresh token flow

```bash
curl -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"<refresh_token>\"}"
```

У відповідь буде новий `access_token`.

## Основні файли

```text
main.py                 # створення FastAPI app і підключення router-ів
api/auth.py             # auth endpoints: register, login, refresh, me
api/books.py            # захищені endpoints для книг
core/security.py        # користувачі, паролі, створення, декодування і перевірка JWT
core/rate_limiter.py    # Redis sliding-window rate limiter
schemas/auth.py         # Pydantic-схеми для auth
schemas/books.py        # Pydantic-схеми для книг
services/books.py       # бізнес-логіка книг
repository/books.py     # робота з MongoDB
database.py             # підключення до MongoDB
tests/test_books.py     # тести API та JWT flow
```

## Змінні середовища

```env
MONGO_URL=mongodb://mongo_admin:password@localhost:27017
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=change-this-secret-for-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```


## Запуск тестів

```bash
pytest tests -q
```
