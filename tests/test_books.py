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

    get_response: Response = await client.get(f"books/{create_response.json()['id']}")
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

    get_response: Response = await client.get(f"books/{2}")
    assert get_response.status_code == 404
