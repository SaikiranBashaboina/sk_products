"""Tests for the 7 issues fixed."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from app.database.database import Base, engine
from main import app, seed_database

# Setup
Base.metadata.create_all(bind=engine)
seed_database()

client = TestClient(app)


def get_admin_token():
    """Helper to get admin token."""
    res = client.post("/api/v1/auth/login", json={"email": "admin@skcompany.com", "password": "admin@12345"})
    return res.json()["access_token"]


def test_issue_1_unlimited_orders():
    """Issue 1: Users should be able to place unlimited orders."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    order_res = client.post("/api/v1/orders", headers=headers, json={"title": "Test Product", "quantity": 10, "price": 99.99})
    assert order_res.status_code == 201
    order_id = order_res.json()["id"]

    # Select order multiple times (simulating unlimited orders)
    user_id = "test-user-123"
    for i in range(3):
        res = client.post(f"/api/v1/orders/{order_id}/select", headers=headers)
        # Should succeed each time (no duplicate check)
        assert res.status_code == 200
        assert res.json()["status"] == "ORDERED"


def test_issue_3_no_auto_identity_role():
    """Issue 3: New users should not automatically get IDENTITY role."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a new user with unique email
    import uuid
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    res = client.post("/api/v1/users", headers=headers, json={
        "name": "Test User",
        "email": unique_email,
        "password": "TestPass123!"
    })
    assert res.status_code == 201
    user_data = res.json()

    # Verify no roles assigned (normal user)
    assert "IDENTITY" not in user_data["roles"]
    assert "ADMIN" not in user_data["roles"]
    assert len(user_data["roles"]) == 0


def test_issue_5_edit_order():
    """Issue 5: Admin should be able to edit existing orders."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    create_res = client.post("/api/v1/orders", headers=headers, json={
        "title": "Original Title",
        "description": "Original desc",
        "quantity": 5,
        "price": 50.0
    })
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Edit the order
    edit_res = client.put(f"/api/v1/orders/{order_id}", headers=headers, json={
        "title": "Updated Title",
        "price": 75.0
    })
    assert edit_res.status_code == 200
    updated = edit_res.json()
    assert updated["title"] == "Updated Title"
    assert updated["price"] == 75.0
    assert updated["description"] == "Original desc"  # unchanged


def test_issue_4_edit_user():
    """Issue 4: Admin/Identity should be able to edit user profile."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a user first with unique email
    import uuid
    unique_email = f"edittest_{uuid.uuid4().hex[:8]}@example.com"
    create_res = client.post("/api/v1/users", headers=headers, json={
        "name": "Edit Test User",
        "email": unique_email,
        "password": "TestPass123!"
    })
    assert create_res.status_code == 201
    user_id = create_res.json()["id"]

    # Edit the user
    edit_res = client.put(f"/api/v1/users/{user_id}", headers=headers, json={
        "name": "Updated Name",
        "phone": "1234567890"
    })
    assert edit_res.status_code == 200
    updated = edit_res.json()
    assert updated["name"] == "Updated Name"
    assert updated["phone"] == "1234567890"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])