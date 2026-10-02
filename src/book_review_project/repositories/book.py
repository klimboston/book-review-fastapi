from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.book_review_project.models import Book
from src.book_review_project.schemas import CreateBook


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_book(self, book: CreateBook):
        db_book = Book(**book.model_dump())
        self.session.add(db_book)
        await self.session.commit()
        await self.session.refresh(db_book)
        return db_book

    async def get_book_by_id(self, book_id: int):
        statement = (
            select(Book)
            .where(Book.id == book_id)
            .options(selectinload(Book.book_reviews))
        )
        book = (await self.session.execute(statement)).scalar_one_or_none()
        return book

    async def get_books_all(self, offset: int, limit: int):
        statement = (
            select(Book)
            .offset(offset)
            .limit(limit)
            .options(selectinload(Book.book_reviews))
        )
        books = (await self.session.execute(statement)).scalars().all()
        return books
