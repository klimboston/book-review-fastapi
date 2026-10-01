import pytest
from httpx import Response


@pytest.fixture
def create_user(client):
    payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    responce: Response = client.post("/users/", json=payload)
    return responce


def test_register_user(client, create_user):
    
    responce: Response = create_user
    body = responce.json()
    assert responce.status_code == 201
    assert "id" in responce.json()
    assert responce.json()["username"] == create_user.json()["username"]


def test_login_user(client, create_user):
    responce = create_user
    login_payload = {"username": "petyapetrov@mail.ru", "password": "piterparker1234"}
    responce: Response = client.post("/users/login", data=login_payload)
    assert responce.status_code == 200
    assert "access_token" in responce.json()


def test_get_user(client, create_user):
    responce: Response = client.get(f"/users/{create_user.json()["id"]}")
    assert responce.status_code == 200
    assert responce.json()["id"] == create_user.json()["id"]
    
@pytest.mark.parametrize("invalid_id", ["abc", "1.5", "-2", "null"])
def test_get_user_validation_errors(client, invalid_id):
    responce: Response = client.get(f"/users/{invalid_id}")
    assert responce.status_code == 422
