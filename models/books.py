import uuid
from sqlalchemy import Column, String, Integer, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase
from enum import Enum


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(SAEnum(BookStatus), nullable=False, default=BookStatus.available)
    year = Column(Integer, nullable=False)