import pytest
from fastapi.testclient import TestClient

from app.db import Database
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app(Database(":memory:"))) as test_client:
        yield test_client


def test_products_are_loaded_from_sqlite(client: TestClient) -> None:
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "계란 (10구)"


def test_cart_estimate_uses_quantity_and_product_price(client: TestClient) -> None:
    response = client.post("/api/cart/estimate", json={"items": [{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 1}]})
    assert response.status_code == 200
    assert response.json() == {"total": 8200, "item_count": 3}


def test_recognition_filters_low_confidence_and_deduplicates_product(client: TestClient) -> None:
    response = client.post(
        "/api/recognition/candidates",
        json={"detections": [
            {"label": "계란", "confidence": 0.81, "x": 10},
            {"label": "계란", "confidence": 0.94, "x": 20},
            {"label": "두부", "confidence": 0.60},
        ]},
    )
    assert response.status_code == 200
    assert response.json()["candidates"][0]["confidence"] == 0.94
    assert response.json()["candidates"][0]["position"]["x"] == 20.0
    assert len(response.json()["candidates"]) == 1


def test_recipes_are_sorted_by_owned_ingredients(client: TestClient) -> None:
    response = client.get("/api/recipes", params=[("ingredients", "계란"), ("ingredients", "대파")])
    assert response.status_code == 200
    assert response.json()[0]["name"] == "계란볶음밥"
    assert response.json()[0]["matched"] == ["계란", "대파"]


def test_unknown_product_cannot_be_confirmed(client: TestClient) -> None:
    response = client.post("/api/cart/items", json={"product_id": 999, "quantity": 1})
    assert response.status_code == 404
