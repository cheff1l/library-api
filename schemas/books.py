from enum import Enum


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"


BOOK_FIELDS = {"title", "author", "description", "status", "year"}


def validate_book_payload(payload, partial=False):
    errors = {}
    data = {}

    if not isinstance(payload, dict):
        return {}, {"body": "Request body must be a JSON object."}

    unknown_fields = sorted(set(payload) - BOOK_FIELDS)
    if unknown_fields:
        errors["unknown_fields"] = f"Unknown fields: {', '.join(unknown_fields)}."

    required_fields = [] if partial else ["title", "author", "year"]
    for field in required_fields:
        if field not in payload:
            errors[field] = "This field is required."

    if "title" in payload:
        title = payload.get("title")
        if not isinstance(title, str) or not title.strip():
            errors["title"] = "Title must be a non-empty string."
        elif len(title) > 255:
            errors["title"] = "Title must not exceed 255 characters."
        else:
            data["title"] = title.strip()

    if "author" in payload:
        author = payload.get("author")
        if not isinstance(author, str) or not author.strip():
            errors["author"] = "Author must be a non-empty string."
        elif len(author) > 255:
            errors["author"] = "Author must not exceed 255 characters."
        else:
            data["author"] = author.strip()

    if "description" in payload:
        description = payload.get("description")
        if description is None:
            data["description"] = None
        elif not isinstance(description, str):
            errors["description"] = "Description must be a string or null."
        elif len(description) > 1000:
            errors["description"] = "Description must not exceed 1000 characters."
        else:
            data["description"] = description.strip()

    if "status" in payload:
        status = payload.get("status")
        allowed_statuses = {item.value for item in BookStatus}
        if status not in allowed_statuses:
            errors["status"] = "Status must be one of: available, issued."
        else:
            data["status"] = status
    elif not partial:
        data["status"] = BookStatus.available.value

    if "year" in payload:
        year = payload.get("year")
        if isinstance(year, bool) or not isinstance(year, int):
            errors["year"] = "Year must be an integer."
        elif year < 1000 or year > 2100:
            errors["year"] = "Year must be between 1000 and 2100."
        else:
            data["year"] = year

    if partial and not data and not errors:
        errors["body"] = "At least one book field must be provided."

    return data, errors


BOOK_SCHEMA = {
    "type": "object",
    "required": ["title", "author", "year"],
    "properties": {
        "title": {"type": "string", "example": "Кобзар"},
        "author": {"type": "string", "example": "Тарас Шевченко"},
        "description": {
            "type": "string",
            "nullable": True,
            "example": "Збірка поетичних творів",
        },
        "status": {
            "type": "string",
            "enum": ["available", "issued"],
            "example": "available",
        },
        "year": {"type": "integer", "example": 1840},
    },
}

BOOK_RESPONSE_SCHEMA = {
    "allOf": [
        BOOK_SCHEMA,
        {
            "type": "object",
            "required": ["id"],
            "properties": {"id": {"type": "string", "example": "6637834775d37b3ed238d16e"}},
        },
    ]
}
