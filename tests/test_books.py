import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy import select

from src.book_review_project.models import Review


async def test_create_book_no_jwt(client: AsyncClient):
    payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    response: Response = await client.post("/books/", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_book_with_jwt(client: AsyncClient, logged_in_user):
    payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    response: Response = await client.post(
        "/books/", json=payload, headers=logged_in_user["auth_header"]
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] > 0
    assert response.json()["user_id"] > 0
    assert response.json()["title"] == payload["title"]
    assert response.json()["author"] == payload["author"]
    assert response.json()["description"] == payload["description"]

    assert response.json()["user_id"] == logged_in_user["user_id"]


@pytest.mark.parametrize(
    "title, author, description, status",
    [
        (1, "author", "Description", status.HTTP_422_UNPROCESSABLE_CONTENT),
        ("Книга", False, "Description", status.HTTP_422_UNPROCESSABLE_CONTENT),
        ("Книга", "author", "t" * 501, status.HTTP_422_UNPROCESSABLE_CONTENT),
    ],
)
async def test_create_book_invalid_data(
    client: AsyncClient, title, author, description, status, logged_in_user
):
    payload = {
        "title": title,
        "author": author,
        "description": description,
    }
    response: Response = await client.post(
        "/books/", json=payload, headers=logged_in_user["auth_header"]
    )
    assert response.status_code == status


async def test_get_book_by_id(client: AsyncClient, logged_in_user):
    payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_response: Response = await client.post(
        "/books/", json=payload, headers=logged_in_user["auth_header"]
    )

    get_response: Response = await client.get(f"/books/{create_response.json()['id']}")
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["id"] == create_response.json()["id"]
    assert get_response.json()["user_id"] == logged_in_user["user_id"]
    assert get_response.json()["title"] == create_response.json()["title"]
    assert get_response.json()["author"] == create_response.json()["author"]
    assert get_response.json()["description"] == create_response.json()["description"]


async def test_get_book_not_found(client: AsyncClient, logged_in_user):
    payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_response: Response = await client.post(
        "/books/", json=payload, headers=logged_in_user["auth_header"]
    )

    get_response: Response = await client.get(
        f"books/{create_response.json()['id'] + 1}"
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_book_with_jwt(client: AsyncClient, logged_in_user, session):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    review_payload = {
        "text": "Текст отзыва",
        "rating": 5,
        "book_id": create_book_response.json()["id"],
    }
    review_response: Response = await client.post(
        "/reviews/", json=review_payload, headers=logged_in_user["auth_header"]
    )

    assert review_response.status_code == status.HTTP_201_CREATED

    book_id = create_book_response.json()["id"]

    response: Response = await client.delete(
        f"/books/{book_id}",
        headers=logged_in_user["auth_header"],
    )

    deleted_book_responce: Response = await client.get(f"/books/{book_id}")
    assert deleted_book_responce.status_code == status.HTTP_404_NOT_FOUND
    assert response.status_code == status.HTTP_204_NO_CONTENT

    statement = select(Review).where(Review.book_id == book_id)
    reviews = (await session.execute(statement)).scalars().all()
    assert reviews == []


async def test_delete_another_users_book_is_forbidden(
    client: AsyncClient,
):
    first_user_payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    register_response: Response = await client.post("/users/", json=first_user_payload)
    assert register_response.status_code == status.HTTP_201_CREATED
    login_payload = {
        "username": first_user_payload["email"],
        "password": first_user_payload["password"],
    }
    login_response: Response = await client.post("/users/login", data=login_payload)
    assert login_response.status_code == status.HTTP_200_OK
    first_user_auth_header = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=first_user_auth_header
    )
    assert create_book_response.status_code == status.HTTP_201_CREATED

    second_user_payload = {
        "username": "Spiderman",
        "email": "PiterParker@mail.ru",
        "password": "secret_password",
    }
    register_response: Response = await client.post("/users/", json=second_user_payload)
    assert register_response.status_code == status.HTTP_201_CREATED
    login_payload = {
        "username": second_user_payload["email"],
        "password": second_user_payload["password"],
    }
    login_response: Response = await client.post("/users/login", data=login_payload)
    assert login_response.status_code == status.HTTP_200_OK
    second_user_auth_header = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    response: Response = await client.delete(
        f"/books/{create_book_response.json()['id']}",
        headers=second_user_auth_header,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_delete_book_no_jwt(client: AsyncClient, logged_in_user):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )

    response: Response = await client.delete(
        f"/books/{create_book_response.json()['id']}",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_book_reviews(client: AsyncClient, created_review: Response):
    response: Response = await client.get(
        f"/books/{created_review.json()['book_id']}/reviews"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_book_reviews_not_found(
    client: AsyncClient, created_review: Response
):
    response: Response = await client.get(
        f"/books/{created_review.json()['book_id'] + 1}/reviews"
    )
    assert response.status_code == 404


async def test_change_book_with_jwt(client: AsyncClient, logged_in_user):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    assert create_book_response.json()["title"] == create_book_payload["title"]

    changed_payload = {"title": "Измененное название книги"}
    response: Response = await client.patch(
        f"/books/{create_book_response.json()['id']}",
        json=changed_payload,
        headers=logged_in_user["auth_header"],
    )
    assert response.status_code == 200
    assert response.json()["title"] == changed_payload["title"]
    responce_saved_in_bd: Response = await client.get(f"/books/{response.json()["id"]}")

    assert responce_saved_in_bd.json() == response.json()

async def test_change_book_no_jwt(client: AsyncClient, logged_in_user):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    assert create_book_response.json()["title"] == create_book_payload["title"]

    changed_payload = {"title": "Измененное название книги"}
    response: Response = await client.patch(
        f"/books/{create_book_response.json()['id']}",
        json=changed_payload,
    )
    assert response.status_code == 401
    
async def test_change_book_is_forbidden(client: AsyncClient, logged_in_user, another_logged_in_user):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    assert create_book_response.json()["title"] == create_book_payload["title"]

    changed_payload = {"title": "Измененное название книги"}
    response: Response = await client.patch(
        f"/books/{create_book_response.json()['id']}",
        json=changed_payload,
        headers=another_logged_in_user["auth_header"]
    )
    assert response.status_code == 403
