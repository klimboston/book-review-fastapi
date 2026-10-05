import pytest
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.book_review_project.core.dependencies import get_session
from src.book_review_project.main import app

test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSession = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture()
async def session():

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSession() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture()
async def client(session):
    async def get_override_session():
        yield session

    app.dependency_overrides[get_session] = get_override_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def logged_in_user(client: AsyncClient):
    payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    register_response: Response = await client.post("/users/", json=payload)
    assert register_response.status_code == 201
    login_payload = {"username": payload["email"], "password": payload["password"]}
    login_response: Response = await client.post("/users/login", data=login_payload)
    assert login_response.status_code == 200
    auth_header = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    return {"user_id": register_response.json()["id"], "auth_header": auth_header}


@pytest.fixture
async def another_logged_in_user(client: AsyncClient):
    payload = {
        "username": "Spiderman",
        "email": "PiterParker@mail.ru",
        "password": "secret_password",
    }
    register_response: Response = await client.post("/users/", json=payload)
    assert register_response.status_code == 201
    login_payload = {
        "username": payload["email"],
        "password": payload["password"],
    }
    login_response: Response = await client.post("/users/login", data=login_payload)
    assert login_response.status_code == 200
    auth_header = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    return {"user_id": register_response.json()["id"], "auth_header": auth_header}
