import pytest
from httpx import AsyncClient, Response


async def test_create_book_no_jwt(client: AsyncClient):
    payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    response: Response = await client.post("/books/", json=payload)
    assert response.status_code == 401


async def test_create_book_with_jwt(client: AsyncClient, logged_in_user):
    payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    response: Response = await client.post(
        "/books/", json=payload, headers=logged_in_user["auth_header"]
    )
    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["user_id"] > 0
    assert response.json()["title"] == payload["title"]
    assert response.json()["author"] == payload["author"]
    assert response.json()["description"] == payload["description"]

    assert response.json()["user_id"] == logged_in_user["user_id"]


@pytest.mark.parametrize(
    "title, author, description, status",
    [
        (1, "author", "Description", 422),
        ("Книга", False, "Description", 422),
        ("Книга", "author", "t" * 501, 422),
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
    assert get_response.status_code == 200
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
    assert get_response.status_code == 404


async def test_delete_book_with_jwt(client: AsyncClient, logged_in_user):
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
    book_with_review_responce: Response = await client.get(
        f"books/{create_book_response.json()['id']}"
    )

    response: Response = await client.delete(
        f"books/{create_book_response.json()['id']}",
        headers=logged_in_user["auth_header"],
    )

    book_with_review_responce: Response = await client.get(
        f"books/{create_book_response.json()['id']}"
    )
    assert book_with_review_responce.status_code == 404
    assert response.status_code == 204
    assert logged_in_user["user_id"] == create_book_response.json()["user_id"]


async def test_delete_another_users_book_is_forbidden(
    client: AsyncClient,
):
    first_user_payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    register_response: Response = await client.post("/users/", json=first_user_payload)
    assert register_response.status_code == 201
    login_payload = {
        "username": first_user_payload["email"],
        "password": first_user_payload["password"],
    }
    login_response: Response = await client.post("/users/login", data=login_payload)
    assert login_response.status_code == 200
    first_user_auth_header = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=first_user_auth_header
    )
    assert create_book_response.status_code == 201

    second_user_payload = {
        "username": "Spiderman",
        "email": "PiterParker@mail.ru",
        "password": "secret_password",
    }
    register_response: Response = await client.post("/users/", json=second_user_payload)
    assert register_response.status_code == 201
    login_payload = {"username": second_user_payload["email"], "password": second_user_payload["password"]}
    login_response: Response = await client.post("/users/login", data=login_payload)
    assert login_response.status_code == 200
    second_user_auth_header = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    response: Response = await client.delete(
        f"books/{create_book_response.json()['id']}",
        headers=second_user_auth_header,
    )

    assert response.status_code == 403
    

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
        f"books/{create_book_response.json()['id']}",
    )

    assert response.status_code == 401
