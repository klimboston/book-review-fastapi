import os

import pytest

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.book_review_project.dependencies import get_session
from src.book_review_project.main import app
from src.book_review_project.models import Book, Review, User

test_engine = create_async_engine(
    "sqlite+aiosqlite:///test.db", connect_args={"check_same_thread": False}
)


@pytest.fixture(name="session", scope="function")
async def session_fixture():

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(test_engine) as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(name="client")
def client_fixture(session):
    async def get_override_session():
        yield session

    app.dependency_overrides[get_session] = get_override_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
