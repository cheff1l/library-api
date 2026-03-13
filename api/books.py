from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from schemas.books import BookCreate, BookResponse, BookStatus
from services.books import BookService
from database import get_db

router = APIRouter()


def get_service(db=Depends(get_db)):
    return BookService(db)


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
    return {"items": books, "limit": limit, "offset": offset}


@router.get("/{book_id}", response_model=BookResponse, status_code=200)
async def get_book_by_id(
    book_id: str,
    service: BookService = Depends(get_service)
):
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Книга з ID '{book_id}' не знайдена")
    return book


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(
    book_data: BookCreate,
    service: BookService = Depends(get_service)
):
    return await service.create_book(book_data)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    service: BookService = Depends(get_service)
):
    await service.delete_book(book_id)
    return None