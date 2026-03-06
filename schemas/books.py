from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Назва книги")
    author: str = Field(..., min_length=1, max_length=255, description="Автор книги")
    description: Optional[str] = Field(None, max_length=1000, description="Опис книги")
    status: BookStatus = Field(default=BookStatus.available, description="Статус книги")
    year: int = Field(..., ge=1000, le=2100, description="Рік випуску")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Майстер і Маргарита",
                "author": "Михайло Булгаков",
                "description": "Роман про добро і зло",
                "status": "available",
                "year": 1967
            }
        }
    }


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    description: Optional[str]
    status: BookStatus
    year: int

    model_config = {"from_attributes": True}
