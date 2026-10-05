from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, status

from src.book_review_project.core.dependencies import (
    CurrentUserDep,
    ReviewRepositoryDep,
)
from src.book_review_project.models import Review
from src.book_review_project.schemas import ReviewCreate, ChangeReview

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отзыв",
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


@router.get(
    "/{review_id}",
    response_model=Review,
    status_code=status.HTTP_200_OK,
    summary="Получить отзыв",
)
async def get_review(
    review_id: Annotated[int, Path()], review_repository: ReviewRepositoryDep
):
    review = await review_repository.get_review_by_id(review_id=review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден"
        )
    return review


@router.delete(
    "/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление отзыва"
)
async def delete_review(
    review_id: Annotated[int, Path()],
    review_repository: ReviewRepositoryDep,
    current_user: CurrentUserDep,
):
    review = await review_repository.get_review_by_id(review_id=review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден"
        )
    if current_user.id != review.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление"
        )
    await review_repository.delete_review(review)


@router.patch(
    "/{review_id}",
    response_model=Review,
    status_code=status.HTTP_200_OK,
    summary="Изменить отзыв",
)
async def change_review(
    review_id: Annotated[int, Path()],
    payload: Annotated[ChangeReview, Body()],
    review_repository: ReviewRepositoryDep,
    current_user: CurrentUserDep,
):
    review = await review_repository.get_review_by_id(review_id=review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден"
        )    
    if current_user.id != review.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на изменение"
        )
    return await review_repository.change_review(review=review, payload=payload)
