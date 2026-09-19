import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from src.book_review_project.dependencies import get_session
from src.book_review_project.main import app
from src.book_review_project.models import Book, Review, User

test_engine = create_engine(
    "sqlite:///test.db", connect_args={"check_same_thread": False}
)


@pytest.fixture(name="session", scope="function")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session

    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def get_override_session():
        yield session

    app.dependency_overrides[get_session] = get_override_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
