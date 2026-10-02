from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.book_review_project.models import User
from src.book_review_project.schemas import CreateUser


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_id(self, user_id: int):
        """Получить пользователя по user_id в таблице user"""
        statement = (
            select(User).where(User.id == user_id).options(selectinload(User.books))
        )
        user = (await self.session.execute(statement)).scalar_one_or_none()

        return user

    async def get_all_users(self, offset: int, limit: int):
        """Получить всех пользователей из таблицы user"""
        statement = select(User).offset(offset=offset).limit(limit=limit)
        users = (await self.session.execute(statement)).scalars().all()
        return users

    async def create_user(self, user: CreateUser, hashed_password: str):
        db_user = User(
            **user.model_dump(exclude={"password"}), hashed_password=hashed_password
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def login_user(self, login_data: OAuth2PasswordRequestForm):
        user = (
            await self.session.execute(
                select(User).where(User.email == login_data.username)
            )
        ).scalar_one_or_none()
        return user
