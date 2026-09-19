from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.book_review_project.dependencies import CurrentUserDep, SessionDep
from src.book_review_project.models import Book, BookWithReviews

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: Annotated[Book, Body()], db: SessionDep, current_user: CurrentUserDep
):
    book.user_id = current_user.id
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


@router.get(
    "/{book_id}",
    response_model=BookWithReviews,
    status_code=status.HTTP_200_OK,
)
async def get_book(book_id: Annotated[int, Path()], db: SessionDep):
    statement = select(Book).where(Book.id==book_id).options(selectinload(Book.book_reviews))
    book = (await db.exec(statement)).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    return book


@router.get("/", response_model=list[BookWithReviews], status_code=status.HTTP_200_OK)
async def get_books(
    db: SessionDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    statement = (
        select(Book).offset(offset).limit(limit).options(selectinload(Book.book_reviews))
    )
    books = (await db.exec(statement)).all()
    return books
