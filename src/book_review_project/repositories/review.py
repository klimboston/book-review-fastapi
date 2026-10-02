from sqlalchemy.ext.asyncio import AsyncSession

from src.book_review_project.models import Book, Review, User


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_review(self, review: Review, current_user: User):
        book = await self.session.get(Book, review.book_id)
        if book is None:
            return None

        db_review = Review(**review.model_dump(), user_id=current_user.id)

        self.session.add(db_review)
        await self.session.commit()
        await self.session.refresh(db_review)
        return db_review
