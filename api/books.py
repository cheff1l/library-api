
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from schemas.books import BookCreate, BookResponse, BookStatus
from services.books import BookService

router = APIRouter()
service = BookService()


@router.get(
    "/",
    response_model=List[BookResponse],
    status_code=200,
    summary="Отримати всі книги"
)
async def get_all_books(
    status: Optional[BookStatus] = Query(None, description="Фільтр по статусу: available або issued"),
    author: Optional[str] = Query(None, description="Фільтр по автору (часткове співпадіння)"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Сортування: title або year"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Порядок: asc або desc")
):

    books = await service.get_all_books(
        status=status.value if status else None,
        author=author,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return books


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    status_code=200,
    summary="Отримати книгу по ID"
)
async def get_book_by_id(book_id: str):

    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Книга з ID '{book_id}' не знайдена")
    return book


@router.post(
    "/",
    response_model=BookResponse,
    status_code=201,
    summary="Додати нову книгу"
)
async def create_book(book_data: BookCreate):
    new_book = await service.create_book(book_data)
    return new_book


@router.delete(
    "/{book_id}",
    status_code=204,
    summary="Видалити книгу (ідемпотентно)"
)
async def delete_book(book_id: str):
    await service.delete_book(book_id)
    return None
