from fastapi import HTTPException, status
from httpx import AsyncClient, Response

from src.book_review_project.models import Book
from src.book_review_project.repositories.book import BookRepository


class StatsService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def get_book_stats(self, book_id: int):
        book: Book | None = await self.repository.get_book_by_id(book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
            )

        ratings = [review.rating for review in book.book_reviews]

        async with AsyncClient() as client:
            response: Response = await client.post(
                "http://localhost:8081/stats", json={"ratings": ratings}
            )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code)
        return response.json()
        
