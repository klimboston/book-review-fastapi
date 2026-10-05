import pytest
from fastapi import status
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
    response: Response = await client.post("/reviews/", json=payload)
    assert response.status_code == 401


async def test_get_review_by_id(client: AsyncClient, created_review: Response):
    result = created_review.json()
    print(result)
    response: Response = await client.get(f"/reviews/{created_review.json()['id']}")
    assert response.status_code == status.HTTP_200_OK


async def test_get_review_by_nonexistent_id(
    client: AsyncClient, created_review: Response
):
    response: Response = await client.get(f"/reviews/{created_review.json()['id'] + 1}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.parametrize("invalid_id", ["abc", True, None])
async def test_get_review_by_invalid_id(client: AsyncClient, created_review: Response, invalid_id):
    response: Response = await client.get(f"/reviews/{invalid_id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    
async def test_delete_review_with_jwt(client: AsyncClient, logged_in_user):
    create_book_payload = {
        "title": "Название книги",
        "author": "Автор",
        "description": "Описание книги",
    }
    create_book_response: Response = await client.post(
        "/books/", json=create_book_payload, headers=logged_in_user["auth_header"]
    )
    create_review_payload = {
        "text": "Текст отзыва",
        "rating": 5,
        "book_id": create_book_response.json()["id"],
    }
    created_review_response: Response = await client.post(
        "/reviews/", json=create_review_payload, headers=logged_in_user["auth_header"]
    )
    response: Response = await client.delete(f"/reviews/{created_review_response.json()["id"]}", headers=logged_in_user["auth_header"])
    assert response.status_code == 204
    
async def test_delete_review_no_jwt(client: AsyncClient, logged_in_user, created_review: Response):
    response: Response = await client.delete(f"/reviews/{created_review.json()["id"]}")
    assert response.status_code == 401 
    
async def test_delete_review_is_forbidden(client: AsyncClient, logged_in_user, another_logged_in_user, created_review: Response):
    review_id = created_review.json()["id"]
    response: Response = await client.delete(f"/reviews/{review_id}", headers=another_logged_in_user["auth_header"])
    assert response.status_code == 403
    
async def test_delete_review_not_found(client: AsyncClient, logged_in_user, created_review: Response):
    response: Response = await client.delete(f"/reviews/{created_review.json()["id"] + 1}", headers=logged_in_user["auth_header"])
    assert response.status_code == 404
    
@pytest.mark.parametrize("invalid_id", ["abc", True, None])
async def test_delete_review_by_invalid_id(client: AsyncClient, invalid_id, logged_in_user):
    response: Response = await client.delete(f"/reviews/{invalid_id}", headers=logged_in_user["auth_header"])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    
async def test_change_review_with_jwt(client: AsyncClient, logged_in_user, created_review: Response):
    payload = {
        "text": "Измененный текст отзыва",

    }
    response: Response = await client.patch(f"/reviews/{created_review.json()["id"]}", json=payload, headers=logged_in_user["auth_header"])
    print(response.json())
    assert response.status_code == 200
    assert logged_in_user["user_id"] == response.json()["user_id"]
    assert response.json()["rating"] == created_review.json()["rating"]
    assert response.json()["text"] == payload["text"]
    payload = {
        "rating": 2,
    }
    response: Response = await client.patch(f"/reviews/{created_review.json()["id"]}", json=payload, headers=logged_in_user["auth_header"])
    assert response.status_code == 200
    assert response.json()["rating"] == payload["rating"]
    
async def test_change_review_no_jwt(client: AsyncClient, created_review: Response):
    payload = {
        "text": "Измененный текст отзыва",

    }
    response: Response = await client.patch(f"/reviews/{created_review.json()["id"]}", json=payload)

    assert response.status_code == 401
    
async def test_change_review_is_forbidden(client: AsyncClient, created_review: Response, logged_in_user, another_logged_in_user):
    payload = {
        "text": "Измененный текст отзыва",

    }
    response: Response = await client.patch(f"/reviews/{created_review.json()["id"]}", json=payload, headers=another_logged_in_user["auth_header"])

    assert response.status_code == 403
    
    
async def test_change_review_not_found(client: AsyncClient, logged_in_user, created_review: Response):
    payload = {
        "text": "Измененный текст отзыва",

    }
    response: Response = await client.patch(f"/reviews/{created_review.json()["id"] + 1}", headers=logged_in_user["auth_header"], json=payload)
    assert response.status_code == 404
    
@pytest.mark.parametrize("invalid_id", ["abc", True, None])
async def test_change_review_by_invalid_id(client: AsyncClient, invalid_id, logged_in_user):
    payload = {
        "text": "Измененный текст отзыва",
    }
    response: Response = await client.patch(f"/reviews/{invalid_id}", headers=logged_in_user["auth_header"], json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT