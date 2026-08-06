"""Tests for stock management feature."""

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


def test_admin_can_set_out_of_stock():
    """Test Admin can change product to Out of Stock."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    create_res = client.post("/api/v1/orders", headers=headers, json={
        "title": "Stock Test Product",
        "quantity": 10,
        "price": 99.99
    })
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Update to OUT_OF_STOCK
    update_res = client.patch(f"/api/v1/orders/{order_id}/stock", headers=headers, json={
        "stock_status": "OUT_OF_STOCK"
    })
    assert update_res.status_code == 200
    assert update_res.json()["stock_status"] == "OUT_OF_STOCK"


def test_admin_can_set_in_stock():
    """Test Admin can change product back to In Stock."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    create_res = client.post("/api/v1/orders", headers=headers, json={
        "title": "Stock Test Product 2",
        "quantity": 10,
        "price": 99.99
    })
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Set to OUT_OF_STOCK first
    client.patch(f"/api/v1/orders/{order_id}/stock", headers=headers, json={
        "stock_status": "OUT_OF_STOCK"
    })

    # Update back to IN_STOCK
    update_res = client.patch(f"/api/v1/orders/{order_id}/stock", headers=headers, json={
        "stock_status": "IN_STOCK"
    })
    assert update_res.status_code == 200
    assert update_res.json()["stock_status"] == "IN_STOCK"


def test_user_cannot_order_out_of_stock():
    """Test user cannot order an Out of Stock product."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    create_res = client.post("/api/v1/orders", headers=headers, json={
        "title": "Out of Stock Product",
        "quantity": 10,
        "price": 99.99
    })
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Set to OUT_OF_STOCK
    client.patch(f"/api/v1/orders/{order_id}/stock", headers=headers, json={
        "stock_status": "OUT_OF_STOCK"
    })

    # Try to order - should fail
    res = client.post(f"/api/v1/orders/{order_id}/select", headers=headers)
    assert res.status_code == 400
    data = res.json()
    assert "out of stock" in data.get("message", data.get("detail", "")).lower()


def test_user_can_order_in_stock():
    """Test user can order an In Stock product."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    create_res = client.post("/api/v1/orders", headers=headers, json={
        "title": "In Stock Product",
        "quantity": 10,
        "price": 99.99
    })
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Ensure it's IN_STOCK
    client.patch(f"/api/v1/orders/{order_id}/stock", headers=headers, json={
        "stock_status": "IN_STOCK"
    })

    # Try to order - should succeed
    res = client.post(f"/api/v1/orders/{order_id}/select", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "ORDERED"


def test_default_stock_status_is_in_stock():
    """Test new orders default to IN_STOCK."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    create_res = client.post("/api/v1/orders", headers=headers, json={
        "title": "Default Stock Product",
        "quantity": 10,
        "price": 99.99
    })
    assert create_res.status_code == 201
    assert create_res.json()["stock_status"] == "IN_STOCK"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])