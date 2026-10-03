import pytest
from httpx import AsyncClient, Response


@pytest.fixture
async def create_user(client: AsyncClient):
    payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    responce: Response = await client.post("/users/", json=payload)
    return {"payload": payload, "responce": responce}


async def test_register_user(client: AsyncClient, create_user):
    responce: Response = create_user["responce"]
    assert responce.status_code == 201
    print(responce.json())
    print("Тест регистрации успешен")


async def test_login_user(client: AsyncClient, create_user):

    payload = create_user["payload"]
    login_payload = {"username": payload["email"], "password": payload["password"]}
    responce: Response = await client.post("/users/login", data=login_payload)
    print(responce.json())
    assert responce.status_code == 200
    assert "access_token" in responce.json()
    assert responce.json()["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": payload["email"], "password": "wrong_password"}
    responce: Response = await client.post("/users/login", data=login_payload)
    assert responce.status_code == 401
    
    
async def test_login_wrong_email(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": "wrongemail@mail.ru", "password": payload["password"]}
    responce: Response = await client.post("/users/login", data=login_payload)
    assert responce.status_code == 401
    
async def test_login_empty_email(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": "", "password": payload["password"]}
    responce: Response = await client.post("/users/login", data=login_payload)
    assert responce.status_code == 422
    
async def test_login_empty_password(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": payload["email"], "password": ""}
    responce: Response = await client.post("/users/login", data=login_payload)
    assert responce.status_code == 422

async def test_login_missing_email(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"password": payload["password"]}
    responce: Response = await client.post("/users/login", data=login_payload)
    assert responce.status_code == 422
    
async def test_login_missing_password(client: AsyncClient, create_user):
    payload = create_user["payload"]
    login_payload = {"username": payload["email"]}
    responce: Response = await client.post("/users/login", data=login_payload)
    assert responce.status_code == 422
    

async def test_get_user(client: AsyncClient, create_user):
    responce: Response = await client.get(f"/users/{create_user['responce'].json()['id']}")
    assert responce.status_code == 200
    assert responce.json()["id"] == create_user['responce'].json()['id']


@pytest.mark.parametrize("invalid_id", ["abc", "1.5", "-2", "null"])
async def test_get_user_validation_errors(client: AsyncClient, invalid_id):
    responce: Response = await client.get(f"/users/{invalid_id}")
    assert responce.status_code == 422
    
    
@pytest.mark.parametrize("invalid_email", ["abc", "1.5", True, "null", "123email@ mail.ru"])
async def test_register_invalid_email(client: AsyncClient, invalid_email, create_user):
    payload = {
        "username": "Petr1995",
        "email": invalid_email,
        "password": "piterparker1234",
    }
    responce: Response = await client.post("/users/", json=payload)
    assert responce.status_code == 422
