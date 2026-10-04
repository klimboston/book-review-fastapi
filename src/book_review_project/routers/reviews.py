from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from src.book_review_project.core.dependencies import (
    CurrentUserDep,
    ReviewRepositoryDep,
)
from src.book_review_project.models import Review
from src.book_review_project.schemas import ReviewCreate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    review: Annotated[ReviewCreate, Body()],
    review_repository: ReviewRepositoryDep,
    current_user: CurrentUserDep,
):

    db_review = await review_repository.create_review(review, current_user=current_user)
    if db_review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
        )

    return db_review
