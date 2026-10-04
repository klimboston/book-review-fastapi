import pytest
from httpx import AsyncClient, Response


async def test_create_review(client: AsyncClient, logged_in_user):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    payload = {
        "text": "Текст отзыва",
        "rating": 5,
        "book_id": create_book_response.json()["id"],
    }
    response: Response = await client.post(
        "/reviews/", json=payload, headers=logged_in_user["auth_header"]
    )
    assert response.status_code == 201
    assert response.json()["book_id"] == create_book_response.json()["id"]
    assert response.json()["id"] > 0
    assert response.json()["user_id"] == logged_in_user["user_id"]
    assert 1 <= len(response.json()["text"]) <= 400
    assert 1 <= response.json()["rating"] <= 5


@pytest.mark.parametrize(
    "text, rating, book_id, status",
    [
        (False, 3, 1, 422),
        ("t" * 401, 3, 1, 422),
        ("Text", 7, 1, 422),
        ("text", 5, 0, 404),
    ],
)
async def test_create_invalid_review(
    client: AsyncClient, logged_in_user, text, rating, book_id, status
):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    payload = {"text": text, "rating": rating, "book_id": book_id}
    response: Response = await client.post(
        "/reviews/", json=payload, headers=logged_in_user["auth_header"]
    )
    assert response.status_code == status
    
async def test_create_review_no_jwt(client: AsyncClient, logged_in_user):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    payload = {
        "text": "Текст отзыва",
        "rating": 5,
        "book_id": create_book_response.json()["id"],
    }
    response: Response = await client.post(
        "/reviews/", json=payload
    )    
    assert response.status_code == 401
