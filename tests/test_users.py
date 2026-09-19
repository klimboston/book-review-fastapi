from httpx import Response


def test_register_user(client):
    payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    responce: Response = client.post("/users/", json=payload)
    assert responce.status_code == 201
    assert "id" in responce.json()
    assert responce.json()["username"] == payload["username"]


def test_login_user(client):
    register_payload = {
        "username": "Petr1995",
        "email": "petyapetrov@mail.ru",
        "password": "piterparker1234",
    }
    responce: Response = client.post("/users/", json=register_payload)
    login_payload = {"username": "petyapetrov@mail.ru", "password": "piterparker1234"}
    responce: Response = client.post("/users/login", data=login_payload)
    assert responce.status_code == 200
    assert "access_token" in responce.json()
