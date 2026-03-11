from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: BookStatus = Field(default=BookStatus.available)
    year: int = Field(..., ge=1000, le=2100)


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    description: Optional[str]
    status: BookStatus
    year: int

    model_config = {"from_attributes": True}