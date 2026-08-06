"""Authentication and authorization tests."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from app.database.database import Base, engine
from main import app, seed_database

# Create tables and seed data before tests
Base.metadata.create_all(bind=engine)
seed_database()

client = TestClient(app)


def get_error_message(response):
    """Get error message from response, supporting both old and new error formats."""
    data = response.json()
    return data.get("message", data.get("detail", ""))


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_success():
    """Test successful login with admin credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@skcompany.com", "password": "admin@12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "admin@skcompany.com"


def test_login_invalid_password():
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@skcompany.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid email or password" in get_error_message(response)


def test_login_invalid_email():
    """Test login with non-existent email."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "password123"}
    )
    assert response.status_code == 401


def test_get_me_authenticated():
    """Test /auth/me with valid token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@skcompany.com", "password": "admin@12345"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@skcompany.com"


def test_get_me_unauthenticated():
    """Test /auth/me without token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_get_me_invalid_token():
    """Test /auth/me with invalid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


def test_get_orders_authenticated():
    """Test that authenticated user can access orders."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@skcompany.com", "password": "admin@12345"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "orders" in response.json()


def test_get_users_admin():
    """Test that admin can access users list."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@skcompany.com", "password": "admin@12345"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "users" in response.json()


def test_create_order_admin():
    """Test that admin can create an order."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@skcompany.com", "password": "admin@12345"}
    )
    token = login_res.json()["access_token"]

    response = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Order", "quantity": 5, "price": 99.99}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Order"


def test_get_profile():
    """Test profile endpoint."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@skcompany.com", "password": "admin@12345"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@skcompany.com"