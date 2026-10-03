import pytest
from httpx import AsyncClient, Response


@pytest.fixture
async def create_user(client: AsyncClient):
    payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    response: Response = await client.post("/users/", json=payload)
    return {"payload": payload, "responce": response}


async def test_register_user(client: AsyncClient, create_user):
    response: Response = create_user["responce"]
    assert response.status_code == 201
    assert response.json()["id"]
    assert response.json()["username"]
    assert response.json()["email"]


async def test_login_user(client: AsyncClient, create_user):

    payload = create_user["payload"]
    login_payload = {"username": payload["email"], "password": payload["password"]}
    response: Response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": payload["email"], "password": "wrong_password"}
    response: Response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 401


async def test_login_wrong_email(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": "wrongemail@mail.ru", "password": payload["password"]}
    response: Response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 401


async def test_login_empty_email(client: AsyncClient):

    login_payload = {"username": "", "password": "password"}
    response: Response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 422


async def test_login_empty_password(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": payload["email"], "password": ""}
    response: Response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 422


async def test_login_missing_email(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"password": payload["password"]}
    response: Response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 422


async def test_login_missing_password(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": payload["email"]}
    response: Response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 422


async def test_get_user(client: AsyncClient, create_user):
    response: Response = await client.get(
        f"/users/{create_user['responce'].json()['id']}"
    )
    assert response.status_code == 200
    assert response.json()["id"] == create_user["responce"].json()["id"]


@pytest.mark.parametrize("invalid_id", ["abc", "1.5", "-2", "null"])
async def test_get_user_validation_errors(client: AsyncClient, invalid_id):
    response: Response = await client.get(f"/users/{invalid_id}")
    assert response.status_code == 422


@pytest.mark.parametrize(
    "invalid_email", ["abc", "1.5", True, "null", "123email@ mail.ru"]
)
async def test_register_invalid_email(client: AsyncClient, invalid_email, create_user):
    payload = {
        "username": "Petr1995",
        "email": invalid_email,
        "password": "piterparker1234",
    }
    response: Response = await client.post("/users/", json=payload)
    assert response.status_code == 422
