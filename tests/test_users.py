from jose import jwt
from app import schemas
from app.config import settings


def test_create_user(client):
    response = client.post(
        "/users", json={"email": "test@test.com", "password": "password"}
    )
    new_user = schemas.UserResponse(**response.json())
    assert new_user.email == "test@test.com"
    assert response.status_code == 201


def test_login_correct(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_response = schemas.Token(**response.json())
    assert login_response.token_type == "bearer"
    payload = jwt.decode(
        login_response.access_token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    id_ = payload.get("user_id")
    assert id_ == test_user["id"]
    assert response.status_code == 200


def test_login_incorrect(client, test_user):
    for username, password in (
        (test_user["email"], "fakepw"),
        ("fakemail", test_user["password"]),
    ):
        response = client.post(
            "/login", data={"username": username, "password": password}
        )
        assert response.status_code == 403
        assert response.json().get("detail") == "Invalid credentials"
