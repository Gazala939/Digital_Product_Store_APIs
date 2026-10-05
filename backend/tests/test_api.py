import os

# Use a separate database for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_store.db"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from main import app
from database import Base, get_db
from models import User, Product
from auth import hash_password


# ============================================================
# TEST DATABASE
# ============================================================

TEST_DATABASE_URL = "sqlite:///./test_store.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# ============================================================
# DATABASE OVERRIDE
# ============================================================

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[
    get_db
] = override_get_db


client = TestClient(app)


# ============================================================
# FIXTURE — FRESH DATABASE FOR EVERY TEST
# ============================================================

@pytest.fixture(autouse=True)
def reset_database():

    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield


# ============================================================
# HELPER — CREATE ADMIN
# ============================================================

def create_test_admin():

    db = TestingSessionLocal()

    admin = User(
        name="Test Admin",
        email="admin@test.com",
        password=hash_password("admin123"),
        role="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    db.close()


# ============================================================
# HELPER — GET USER TOKEN
# ============================================================

def register_and_login(
    email="user@test.com"
):

    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


# ============================================================
# TEST 1 — REGISTRATION
# ============================================================

def test_registration():

    response = client.post(
        "/auth/register",
        json={
            "name": "Gazala",
            "email": "gazala@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Gazala"
    assert data["email"] == "gazala@test.com"
    assert data["role"] == "USER"


# ============================================================
# TEST 2 — LOGIN
# ============================================================

def test_login():

    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@test.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ============================================================
# TEST 3 — INVALID LOGIN
# ============================================================

def test_invalid_login():

    client.post(
        "/auth/register",
        json={
            "name": "Invalid User",
            "email": "invalid@test.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


# ============================================================
# TEST 4 — PRODUCT LISTING + PAGINATION
# ============================================================

def test_product_listing():

    create_test_admin()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create products
    for number in range(5):

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": f"Product {number}",
                "description": "Test product",
                "price": 100 + number
            }
        )

        assert response.status_code == 201

    # Test pagination
    response = client.get(
        "/products?page=1&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["total_pages"] == 3


# ============================================================
# TEST 5 — ADMIN PRODUCT CREATION
# ============================================================

def test_product_creation():

    create_test_admin()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post(
        "/products",
        headers=headers,
        json={
            "name": "Python Course",
            "description": "Complete Python course",
            "price": 500,
            "image": "python.jpg"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Python Course"
    assert data["price"] == 500


# ============================================================
# TEST 6 — CART
# ============================================================

def test_cart():

    # Create admin
    create_test_admin()

    admin_login = client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )

    admin_token = admin_login.json()["access_token"]

    # Create product
    product_response = client.post(
        "/products",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "name": "Python Course",
            "description": "Python course",
            "price": 500
        }
    )

    product_id = product_response.json()["id"]

    # Create user
    user_token = register_and_login()

    user_headers = {
        "Authorization": f"Bearer {user_token}"
    }

    # Add product to cart
    response = client.post(
        "/cart/items",
        headers=user_headers,
        json={
            "product_id": product_id,
            "quantity": 2
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total_amount"] == 1000


# ============================================================
# TEST 7 — ORDER CREATION
# ============================================================

def test_order_creation():

    create_test_admin()

    admin_login = client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )

    admin_token = admin_login.json()["access_token"]

    # Create product
    product_response = client.post(
        "/products",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "name": "Python Course",
            "description": "Python course",
            "price": 500
        }
    )

    product_id = product_response.json()["id"]

    # Create user
    user_token = register_and_login()

    user_headers = {
        "Authorization": f"Bearer {user_token}"
    }

    # Add product
    client.post(
        "/cart/items",
        headers=user_headers,
        json={
            "product_id": product_id,
            "quantity": 1
        }
    )

    # Create order
    response = client.post(
        "/orders",
        headers=user_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "PENDING"
    assert data["payment_status"] == "PENDING"
    assert len(data["items"]) == 1
    assert data["total_amount"] == 500


# ============================================================
# TEST 8 — UNAUTHORIZED PRODUCT CREATION
# ============================================================

def test_unauthorized_product_creation():

    token = register_and_login()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post(
        "/products",
        headers=headers,
        json={
            "name": "Unauthorized Product",
            "description": "Should not be created",
            "price": 100
        }
    )

    assert response.status_code == 403


# ============================================================
# TEST 9 — PROFILE
# ============================================================

def test_profile():

    token = register_and_login()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(
        "/auth/profile",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "user@test.com"


# ============================================================
# TEST 10 — EMPTY CART ORDER
# ============================================================

def test_empty_cart_order():

    token = register_and_login(
        email="empty@test.com"
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post(
        "/orders",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"