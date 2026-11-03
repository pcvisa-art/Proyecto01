import pytest

from app_factory import create_app
from extensions import db


@pytest.fixture
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_register_and_login(client):
    response = client.post(
        "/api/auth/register",
        json={
            "nombre": "Ana Perez",
            "email": "ana@example.com",
            "password": "Password1",
            "rol": "EDITOR",
        },
    )
    assert response.status_code == 201

    login = client.post(
        "/api/auth/login",
        json={
            "email": "ana@example.com",
            "password": "Password1",
        },
    )
    assert login.status_code == 200
    payload = login.get_json()
    assert "access_token" in payload
    assert payload["usuario"]["rol"] == "EDITOR"


def test_create_category_and_product(client):
    client.post(
        "/api/auth/register",
        json={
            "nombre": "Luis Gomez",
            "email": "luis@example.com",
            "password": "Password1",
            "rol": "EDITOR",
        },
    )
    login = client.post(
        "/api/auth/login",
        json={
            "email": "luis@example.com",
            "password": "Password1",
        },
    )
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    category = client.post(
        "/api/categorias",
        json={
            "nombre": "Laptops",
            "descripcion": "Computadoras portátiles",
            "estado": True,
        },
        headers=headers,
    )
    assert category.status_code == 201
    category_id = category.get_json()["categoria"]["id"]

    product = client.post(
        "/api/productos",
        json={
            "nombre": "Laptop Pro",
            "descripcion": "Laptop de alto rendimiento",
            "precio": 1200.50,
            "stock": 18,
            "estado": True,
            "categoria_id": category_id,
        },
        headers=headers,
    )
    assert product.status_code == 201
    assert product.get_json()["producto"]["nombre"] == "Laptop Pro"

    listing = client.get("/api/productos?categoria_id=" + str(category_id), headers=headers)
    assert listing.status_code == 200
    assert len(listing.get_json()) == 1
