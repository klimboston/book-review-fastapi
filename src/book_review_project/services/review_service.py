from fastapi import HTTPException, status

from src.book_review_project.models import User
from src.book_review_project.repositories.review import ReviewRepository
from src.book_review_project.schemas import ChangeReview, ReviewCreate


class ReviewService:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    async def create_review(self, review: ReviewCreate, current_user: User):
        db_review = await self.repository.create_review(
            review, current_user=current_user
        )
        if db_review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
            )

        return db_review

    async def get_review(self, review_id: int):
        review = await self.repository.get_review_by_id(review_id=review_id)
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден"
            )
        return review

    async def delete_review(self, review_id: int, current_user: User):
        review = await self.repository.get_review_by_id(review_id=review_id)
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден"
            )
        if current_user.id != review.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление"
            )
        await self.repository.delete_review(review)

    async def change_review(
        self, review_id: int, current_user: User, payload: ChangeReview
    ):
        review = await self.repository.get_review_by_id(review_id=review_id)
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден"
            )
        if current_user.id != review.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на изменение"
            )
        return await self.repository.change_review(review=review, payload=payload)
