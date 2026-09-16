from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from src.book_review_project.dependencies import CurrentUserDep, SessionDep
from src.book_review_project.models import Book, Review, ReviewCreate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
)
def create_review(review: Annotated[ReviewCreate, Body()], db: SessionDep, current_user: CurrentUserDep):
    book = db.get(Book, review.book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    
    db_review = Review(**review.model_dump(), user_id=current_user.id)
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review