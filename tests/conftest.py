import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:password123@localhost:5432/fastapi_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client(session):
    def get_test_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()



@pytest.fixture
def test_users(client):
    test_users_ = []
    for email, password in [("test_user_1@test.com", "password_test_user_1"), ("test_user_2@test.com", "password_test_user_2")]:
        user_data = {"email": email, "password": password}
        response = client.post("/users", json=user_data)
        test_user_ = response.json()
        test_user_["password"] = user_data["password"]
        assert response.status_code == 201
        test_users_.append(test_user_)
    return test_users_


@pytest.fixture
def test_user(test_users):
    return test_users[0]


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(test_users, session):
    posts_data = [
        {"title": "1st title", "content": "1st content", "user_id": test_users[0]["id"]},
        {"title": "2nd title", "content": "2nd content", "user_id": test_users[0]["id"]},
        {"title": "3rd title", "content": "3rd content", "user_id": test_users[0]["id"]},
        {"title": "extra user title", "content": "extra user content", "user_id": test_users[1]["id"]},
    ]
    session.add_all([models.Post(**post_data) for post_data in posts_data])
    session.commit()
    return session.query(models.Post).all()