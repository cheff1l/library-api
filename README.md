# Library API - Lab 6

Лабораторна робота 6: автентифікація та авторизація з використанням JWT.

Проект реалізовано на FastAPI. API працює з книгами бібліотеки, а всі `/books` ендпоінти захищені Bearer JWT access token. Також реалізовано refresh token flow.

## Що реалізовано

- `POST /auth/login` - генерація access token і refresh token;
- `POST /auth/register` - реєстрація нового користувача з одразу виданими токенами;
- `POST /auth/refresh` - генерація нового access token через refresh token;
- `GET /auth/me` - перевірка поточного користувача за access token;
- захист усіх `/books` ендпоінтів через `Authorization: Bearer <access_token>`;
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
JWT_SECRET_KEY=change-this-secret-for-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Перемикання між лабораторними

Кожна лабораторна зберігається в окремій Git-гілці.

```bash
git checkout lab-5
```

Показати лабораторну 5.

```bash
git checkout lab-6
```

Показати лабораторну 6.

Після перемикання гілки краще перезапустити Docker:

```bash
docker compose down
docker compose up --build
```

## Запуск тестів

```bash
pytest tests -q
```
