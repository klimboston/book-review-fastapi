from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from sqlmodel import select

from src.book_review_project.dependencies import CurrentUserDep, SessionDep
from src.book_review_project.models import Book, BookWithReviews

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    book: Annotated[Book, Body()], db: SessionDep, current_user: CurrentUserDep
):
    book.user_id = current_user.id
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get(
    "/{book_id}",
    response_model=BookWithReviews,
    status_code=status.HTTP_200_OK,
)
def get_book(book_id: Annotated[int, Path()], db: SessionDep):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    return book


@router.get("/", response_model=list[BookWithReviews], status_code=status.HTTP_200_OK)
def get_books(
    db: SessionDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    books = db.exec(select(Book).offset(offset=offset).limit(limit=limit)).all()
    return books
