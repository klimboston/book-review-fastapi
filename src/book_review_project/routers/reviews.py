from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, status

from src.book_review_project.core.dependencies import (
    CurrentUserDep,
    ReviewRepositoryDep,
    ReviewServiceDep,
)
from src.book_review_project.models import Review
from src.book_review_project.schemas import ChangeReview, ReviewCreate
from src.book_review_project.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отзыв",
)
async def create_review(
    review: Annotated[ReviewCreate, Body()],
    review_service: ReviewServiceDep,
    current_user: CurrentUserDep,
):
    return await review_service.create_review(review, current_user)


@router.get(
    "/{review_id}",
    response_model=Review,
    status_code=status.HTTP_200_OK,
    summary="Получить отзыв",
)
async def get_review(
    review_id: Annotated[int, Path()], review_service: ReviewServiceDep
):
    return await review_service.get_review(review_id)


@router.delete(
    "/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление отзыва"
)
async def delete_review(
    review_id: Annotated[int, Path()],
    review_service: ReviewServiceDep,
    current_user: CurrentUserDep,
):
    await review_service.delete_review(review_id, current_user)


@router.patch(
    "/{review_id}",
    response_model=Review,
    status_code=status.HTTP_200_OK,
    summary="Изменить отзыв",
)
async def change_review(
    review_id: Annotated[int, Path()],
    payload: Annotated[ChangeReview, Body()],
    review_service: ReviewServiceDep,
    current_user: CurrentUserDep,
):
    return await review_service.change_review(
        review_id, current_user, payload=payload
    )
