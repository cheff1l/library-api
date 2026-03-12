from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.books import BookCreate, BookResponse, BookStatus
from services.books import BookService
from database import get_db

router = APIRouter()
service = BookService()


@router.get("/", status_code=200)
async def get_all_books(
    status: Optional[BookStatus] = Query(None),
    author: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db)
):
    books, next_cursor = await service.get_all_books(
        session=session,
        status=status.value if status else None,
        author=author,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        cursor=cursor
    )
    return {
        "items": [BookResponse.model_validate(b) for b in books],
        "next_cursor": next_cursor
    }


@router.get("/{book_id}", response_model=BookResponse, status_code=200)
async def get_book_by_id(
    book_id: str,
    session: AsyncSession = Depends(get_db)
):
    book = await service.get_book_by_id(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Книга з ID '{book_id}' не знайдена")
    return book


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_db)
):
    return await service.create_book(session, book_data)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    session: AsyncSession = Depends(get_db)
):
    await service.delete_book(session, book_id)
    return None