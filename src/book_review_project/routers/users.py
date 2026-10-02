from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from src.book_review_project.core.dependencies import UserRepositoryDep
from src.book_review_project.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from src.book_review_project.models import User
from src.book_review_project.schemas import CreateUser, Token, UserWithBooks

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/{user_id}",
    response_model=UserWithBooks,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: Annotated[int, Path(ge=1)], user_repository: UserRepositoryDep
):
    """Получить пользователя с его книгами по user_id"""
    user = await user_repository.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.get(
    "/",
    response_model=list[User],
    status_code=status.HTTP_200_OK,
    summary="Получить всех пользователей",
)
async def get_users(
    user_repository: UserRepositoryDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """Получить всех пользователей"""
    users = await user_repository.get_all_users(offset=offset, limit=limit)
    return users


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, user_repository: UserRepositoryDep):
    """Регистрация пользователя"""
    hashed_password = hash_password(user.password)
    db_user = await user_repository.create_user(user, hashed_password)
    return db_user


@router.post("/login", response_model=Token, status_code=200)
async def login_user(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repository: UserRepositoryDep,
):

    user = await user_repository.login_user(login_data)
    if user is None or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")
