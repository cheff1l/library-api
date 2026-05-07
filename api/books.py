from flask import current_app, request
from flask_restful import Resource
from flasgger import swag_from

from database import get_db
from schemas.books import BOOK_RESPONSE_SCHEMA, BOOK_SCHEMA, BookStatus, validate_book_payload
from services.books import BookService


def get_service():
    if current_app.config.get("BOOK_SERVICE"):
        return current_app.config["BOOK_SERVICE"]
    db = current_app.config.get("DB") or get_db()
    return BookService(db)


def serialize_book(book):
    book = dict(book)
    book["id"] = str(book.pop("_id"))
    return book


def error_response(message, status_code=400, details=None):
    payload = {"message": message}
    if details:
        payload["errors"] = details
    return payload, status_code


def parse_int_arg(name, default, minimum=None, maximum=None):
    raw_value = request.args.get(name, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f"Query parameter '{name}' must be an integer.")

    if minimum is not None and value < minimum:
        raise ValueError(f"Query parameter '{name}' must be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"Query parameter '{name}' must be at most {maximum}.")
    return value


BOOK_LIST_GET_DOC = {
    "tags": ["Books"],
    "summary": "Отримати список книг",
    "parameters": [
        {
            "name": "status",
            "in": "query",
            "type": "string",
            "enum": ["available", "issued"],
            "required": False,
            "description": "Фільтр за статусом книги.",
        },
        {
            "name": "author",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Пошук за частиною імені автора.",
        },
        {
            "name": "sort_by",
            "in": "query",
            "type": "string",
            "enum": ["title", "year"],
            "required": False,
            "description": "Поле сортування.",
        },
        {
            "name": "sort_order",
            "in": "query",
            "type": "string",
            "enum": ["asc", "desc"],
            "default": "asc",
            "required": False,
        },
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "default": 10,
            "minimum": 1,
            "maximum": 100,
            "required": False,
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer",
            "default": 0,
            "minimum": 0,
            "required": False,
        },
    ],
    "responses": {
        200: {
            "description": "Список книг",
            "schema": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": BOOK_RESPONSE_SCHEMA},
                    "limit": {"type": "integer"},
                    "offset": {"type": "integer"},
                    "total": {"type": "integer"},
                },
            },
        },
        400: {"description": "Некоректні query-параметри"},
    },
}

BOOK_CREATE_DOC = {
    "tags": ["Books"],
    "summary": "Додати нову книгу",
    "parameters": [
        {
            "name": "book",
            "in": "body",
            "required": True,
            "schema": BOOK_SCHEMA,
        }
    ],
    "responses": {
        201: {"description": "Книгу створено", "schema": BOOK_RESPONSE_SCHEMA},
        400: {"description": "Некоректні дані книги"},
    },
}

BOOK_GET_DOC = {
    "tags": ["Books"],
    "summary": "Отримати книгу за ID",
    "parameters": [
        {"name": "book_id", "in": "path", "type": "string", "required": True},
    ],
    "responses": {
        200: {"description": "Книгу знайдено", "schema": BOOK_RESPONSE_SCHEMA},
        404: {"description": "Книгу не знайдено"},
    },
}

BOOK_UPDATE_DOC = {
    "tags": ["Books"],
    "summary": "Оновити книгу за ID",
    "parameters": [
        {"name": "book_id", "in": "path", "type": "string", "required": True},
        {"name": "book", "in": "body", "required": True, "schema": BOOK_SCHEMA},
    ],
    "responses": {
        200: {"description": "Книгу оновлено", "schema": BOOK_RESPONSE_SCHEMA},
        400: {"description": "Некоректні дані книги"},
        404: {"description": "Книгу не знайдено"},
    },
}

BOOK_DELETE_DOC = {
    "tags": ["Books"],
    "summary": "Видалити книгу за ID",
    "parameters": [
        {"name": "book_id", "in": "path", "type": "string", "required": True},
    ],
    "responses": {
        204: {"description": "Книгу видалено або вона вже не існувала"},
    },
}


class BookListResource(Resource):
    @swag_from(BOOK_LIST_GET_DOC)
    def get(self):
        status = request.args.get("status")
        author = request.args.get("author")
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")

        allowed_statuses = {item.value for item in BookStatus}
        if status and status not in allowed_statuses:
            return error_response("Invalid status filter.", details={"status": "Use available or issued."})

        if sort_by and sort_by not in {"title", "year"}:
            return error_response("Invalid sort field.", details={"sort_by": "Use title or year."})

        if sort_order not in {"asc", "desc"}:
            return error_response("Invalid sort order.", details={"sort_order": "Use asc or desc."})

        try:
            limit = parse_int_arg("limit", 10, minimum=1, maximum=100)
            offset = parse_int_arg("offset", 0, minimum=0)
        except ValueError as exc:
            return error_response(str(exc))

        books, total = get_service().get_all_books(
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

        return {
            "items": [serialize_book(book) for book in books],
            "limit": limit,
            "offset": offset,
            "total": total,
        }, 200

    @swag_from(BOOK_CREATE_DOC)
    def post(self):
        payload = request.get_json(silent=True)
        data, errors = validate_book_payload(payload)
        if errors:
            return error_response("Validation failed.", details=errors)

        book = get_service().create_book(data)
        return serialize_book(book), 201


class BookResource(Resource):
    @swag_from(BOOK_GET_DOC)
    def get(self, book_id):
        try:
            book = get_service().get_book_by_id(book_id)
        except ValueError:
            book = None

        if not book:
            return error_response(f"Book with ID '{book_id}' was not found.", status_code=404)
        return serialize_book(book), 200

    @swag_from(BOOK_UPDATE_DOC)
    def put(self, book_id):
        payload = request.get_json(silent=True)
        data, errors = validate_book_payload(payload, partial=True)
        if errors:
            return error_response("Validation failed.", details=errors)

        try:
            book = get_service().update_book(book_id, data)
        except ValueError:
            book = None

        if not book:
            return error_response(f"Book with ID '{book_id}' was not found.", status_code=404)
        return serialize_book(book), 200

    @swag_from(BOOK_DELETE_DOC)
    def delete(self, book_id):
        try:
            get_service().delete_book(book_id)
        except ValueError:
            pass
        return "", 204
