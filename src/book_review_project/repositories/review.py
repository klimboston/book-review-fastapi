from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.book_review_project.models import Book, Review, User
from src.book_review_project.schemas import ChangeReview, ReviewCreate


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_review(self, review: ReviewCreate, current_user: User):
        book = await self.session.get(Book, review.book_id)
        if book is None:
            return None

        db_review = Review(**review.model_dump(), user_id=current_user.id)

        self.session.add(db_review)
        await self.session.commit()
        await self.session.refresh(db_review)
        return db_review

    async def get_review_by_id(self, review_id: int) -> Review | None:
        review = await self.session.get(Review, review_id)
        return review

    async def delete_review(self, review: Review):
        await self.session.delete(review)
        await self.session.commit()

    async def change_review(self, review: Review, payload: ChangeReview):
        payload = payload.model_dump(exclude_unset=True)
        statement = update(Review).where(Review.id == review.id).values(**payload)
        await self.session.execute(statement)
        await self.session.commit()
        return await self.get_review_by_id(review.id)
        
