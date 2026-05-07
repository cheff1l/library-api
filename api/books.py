from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from bson import ObjectId
from core.security import get_current_user
from schemas.books import BookCreate, BookResponse, BookStatus
from services.books import BookService
from database import get_db

router = APIRouter(dependencies=[Depends(get_current_user)])


def get_service(db=Depends(get_db)):
    return BookService(db)


def serialize_book(book: dict) -> dict:
    book["id"] = str(book["_id"])
    del book["_id"]
    return book


@router.get("/", status_code=200)
async def get_all_books(
    status: Optional[BookStatus] = Query(None),
    author: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: BookService = Depends(get_service)
):
    books = await service.get_all_books(
        status=status.value if status else None,
        author=author,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    return {
        "items": [serialize_book(b) for b in books],
        "limit": limit,
        "offset": offset
    }


@router.get("/{book_id}", status_code=200)
async def get_book_by_id(
    book_id: str,
    service: BookService = Depends(get_service)
):
    try:
        book = await service.get_book_by_id(book_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Книга з ID '{book_id}' не знайдена")
    if not book:
        raise HTTPException(status_code=404, detail=f"Книга з ID '{book_id}' не знайдена")
    return serialize_book(book)


@router.post("/", status_code=201)
async def create_book(
    book_data: BookCreate,
    service: BookService = Depends(get_service)
):
    book = await service.create_book(book_data)
    return serialize_book(book)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    service: BookService = Depends(get_service)
):
    await service.delete_book(book_id)
    return None
