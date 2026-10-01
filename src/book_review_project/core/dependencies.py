from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.book_review_project.core.database import async_session_maker
from src.book_review_project.core.security import ALGORITHM, SECRET_KEY
from src.book_review_project.models import User
from src.book_review_project.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def get_session():
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
"""
Зависимость для создания асинхронной сессии с базой данных
"""


async def get_current_user(
    db: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded_token.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )
    user = await db.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
"""
Зависимость для проверки пользователя на наличие валидного JWT токена.
"""



def get_user_repository(session: SessionDep):
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
"""
Зависимость для работы с репозиторием таблицы User, возвращает экземпляр
UserRepository(session)
"""
