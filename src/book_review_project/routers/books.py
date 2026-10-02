from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status

from src.book_review_project.core.dependencies import (
    BookRepositoryDep,
    CurrentUserDep,
)
from src.book_review_project.models import Book
from src.book_review_project.schemas import BookWithReviews, CreateBook

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: Annotated[CreateBook, Body()],
    book_repository: BookRepositoryDep,
    current_user: CurrentUserDep,
):
    book.user_id = current_user.id
    db_book = await book_repository.create_book(book)
    return db_book


@router.get(
    "/{book_id}",
    response_model=BookWithReviews,
    status_code=status.HTTP_200_OK,
)
async def get_book(book_id: Annotated[int, Path()], book_repository: BookRepositoryDep):
    book = await book_repository.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    return book


@router.get("/", response_model=list[BookWithReviews], status_code=status.HTTP_200_OK)
async def get_books(
    book_repository: BookRepositoryDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    books = await book_repository.get_books_all(offset=offset, limit=limit)
    return books
