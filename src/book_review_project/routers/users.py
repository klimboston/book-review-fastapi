from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.book_review_project.dependencies import SessionDep
from src.book_review_project.models import (
    CreateUser,
    Token,
    User,
    UserLogin,
    UserWithBooks,
)
from src.book_review_project.security import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/{user_id}",
    response_model=UserWithBooks,
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: Annotated[int, Path()], db: SessionDep):
    statement = select(User).where(User.id == user_id).options(selectinload(User.books))
    user = (await db.exec(statement)).first()
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
    db: SessionDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = (await db.exec(select(User).offset(offset=offset).limit(limit=limit))).all()
    return users


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, db: SessionDep):
    """Регистрация пользователя"""
    hashed_password = hash_password(user.password)
    db_user = User(
        **user.model_dump(exclude={"password"}), hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token, status_code=200)
async def login_user(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep
):
    user = (
        await db.exec(select(User).where(User.email == login_data.username))
    ).first()
    if user is None or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")
