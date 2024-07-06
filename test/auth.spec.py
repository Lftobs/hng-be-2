import pytest
from app.auth import create_access_token, get_current_user
from datetime import timedelta
from fastapi.testclient import TestClient
from main import app

from app.auth import TestingSessionLocal

client = TestClient(app)

def test_register_user_success(db):
    response = client.post("/auth/register", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    assert response.status_code == 201
    assert response.json()["data"]["first_name"] == "John"
    assert response.json()["data"]["last_name"] == "Doe"
    assert response.json()["data"]["email"] == "john.doe@example.com"

def test_login_user_success(db):
    response = client.post("/auth/login", data={
        "username": "john.doe@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]

def test_register_user_missing_fields(db):
    response = client.post("/auth/register", json={
        "first_name": "John",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    assert response.status_code == 422

def test_register_user_duplicate_email(db):
    client.post("/auth/register", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    response = client.post("/auth/register", json={
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "0987654321"
    })
    assert response.status_code == 400



def test_token_creation():
    access_token = create_access_token(
        data={"sub": "test_user_id"}, expires_delta=timedelta(minutes=15)
    )
    assert access_token is not None

def test_token_validation(db):
    token = create_access_token(data={"sub": "test_user_id"})
    current_user = get_current_user(token=token, db=db)
    assert current_user.user_id == "test_user_id"
    




@pytest.fixture(scope="module")
def db():
    yield TestingSessionLocal()

def test_get_organisations(db, client, access_token):
    response = client.get("/api/organisations", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert "organisations" in response.json()["data"]

def test_get_organisation(db, client, access_token):
    org_id = "existing_org_id"
    response = client.get(f"/api/organisations/{org_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["org_id"] == org_id

def test_create_organisation(db, client, access_token):
    response = client.post("/api/organisations", json={
        "name": "New Organisation",
        "description": "A new organisation"
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "New Organisation"

