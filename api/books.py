from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.books import BookCreate, BookResponse, BookStatus
from services.books import BookService
from database import get_db

router = APIRouter()
service = BookService()


@router.get("/", response_model=List[BookResponse], status_code=200)
async def get_all_books(
    status: Optional[BookStatus] = Query(None),
    author: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db)
):
    return await service.get_all_books(
        session=session,
        status=status.value if status else None,
        author=author,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )


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