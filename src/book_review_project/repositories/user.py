from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.book_review_project.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_id(self, user_id: int):
        """Получить пользователя по user_id в таблице user"""

        statement = (
            select(User).where(User.id == user_id).options(selectinload(User.books))
        )
        user = (await self.session.execute(statement)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    async def get_all_users(self, offset: int, limit: int):
        """Получить всех пользователей из таблицы user"""
        
        statement = select(User).offset(offset=offset).limit(limit=limit)
        users = (await self.session.execute(statement)).scalars().all()
        return users
