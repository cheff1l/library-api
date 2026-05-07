from enum import Enum


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"