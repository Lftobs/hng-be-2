import pytest
from app.auth import create_access_token, current_user
from main import get_current_user
from datetime import timedelta
from fastapi.testclient import TestClient
from main import app

from app.db import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    yield TestingSessionLocal()

def test_register_user_success():
    response = client.post("/auth/register", json={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe707@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    assert response.status_code == 201
    print(response.json())
    assert response.json()["data"]["user"]["firstName"] == "John"
    assert response.json()["data"]["user"]["lastName"] == "Doe"
    assert response.json()["data"]["user"]["email"] == "john.doe707@example.com"

def test_login_user_success():
    response = client.post("/auth/login", json={
        "email": "john.doe4@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["data"]["user"]["firstName"] == "John"
    assert response.json()["data"]["user"]["lastName"] == "Doe"
    assert response.json()["data"]["user"]["email"] == "john.doe4@example.com"
    assert "accessToken" in response.json()["data"]

def test_register_user_missing_fields():
    response = client.post("/auth/register", json={
        "firstName": "John",
        "email": "john.doe1@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    assert response.status_code == 422

def test_register_user_duplicate_email():
    client.post("/auth/register", json={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe6@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    response = client.post("/auth/register", json={
        "firstName": "Jane",
        "lastName": "Doe",
        "email": "john.doe6@example.com",
        "password": "password123",
        "phone": "0987654321"
    })
    assert response.status_code == 400

#unit_test

def test_token_creation():
    access_token = create_access_token(
        data={"sub": "test_user_id"}, expires_delta=timedelta(minutes=15)
    )
    assert access_token is not None

def test_token_validation():
    access_token = create_access_token(
        data={"sub": "test_user_id"}, expires_delta=timedelta(minutes=15)
    )
    print(access_token)
    currentUser = current_user(token=access_token)
    assert currentUser == "test_user_id"
    






def test_get_organisations():
    res =  client.post("/auth/login", json={
        "email": "john.doe4@example.com",
        "password": "password123"
    })
    access_token = res.json()["data"]["accessToken"]
    response = client.get("/api/organisations", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    print(response.json())
    assert "organisations" in response.json()["data"]

def test_get_organisation():
    res =  client.post("/auth/login", json={
        "email": "john.doe4@example.com",
        "password": "password123"
    })
    access_token = res.json()["data"]["accessToken"]
    
    org_res = client.post("/api/organisations", json={
        "name": "New Organisation707",
        "description": "A new organisation"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    org_id = org_res.json()["data"]["orgId"]
    
    response = client.get(f"/api/organisations/{org_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["orgId"] == org_id

def test_create_organisation():
    res =  client.post("/auth/login", json={
        "email": "john.doe4@example.com",
        "password": "password123"
    })
    access_token = res.json()["data"]["accessToken"]
    
    response = client.post("/api/organisations", json={
        "name": "New Organisation88",
        "description": "A new organisation"
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "New Organisation88"

