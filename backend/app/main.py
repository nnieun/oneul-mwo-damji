from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int
    name: str
    price: int
    ingredients: list[str]


class CartItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=0)


class CartEstimateRequest(BaseModel):
    items: list[CartItem] = Field(default_factory=list)


class CartEstimateResponse(BaseModel):
    total: int
    item_count: int


class RecipeRecommendation(BaseModel):
    id: int
    name: str
    ingredients: list[str]
    matched: list[str]
    missing: list[str]
    time: str


PRODUCTS = [
    Product(id=1, name="계란 (10구)", price=3200, ingredients=["계란"]),
    Product(id=2, name="두부 (300g)", price=1800, ingredients=["두부"]),
    Product(id=3, name="대파 (1단)", price=2500, ingredients=["대파"]),
]

RECIPES = [
    {"id": 1, "name": "계란볶음밥", "ingredients": ["계란", "대파", "밥", "간장"], "time": "10분"},
    {"id": 2, "name": "순두부찌개", "ingredients": ["두부", "계란", "고춧가루", "멸치육수", "애호박"], "time": "20분"},
    {"id": 3, "name": "파계란탕", "ingredients": ["계란", "대파", "소금", "참기름"], "time": "8분"},
]

app = FastAPI(
    title="오늘 뭐 담지 API",
    description="AI 스마트 마트카트 MVP를 위한 상품·장바구니·요리 추천 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8443", "http://127.0.0.1:8443"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str | bool]:
    return {"ok": True, "service": "oneul-mwo-damji-backend"}


@app.get("/api/products", response_model=list[Product])
def get_products() -> list[Product]:
    return PRODUCTS


@app.post("/api/cart/estimate", response_model=CartEstimateResponse)
def estimate_cart(request: CartEstimateRequest) -> CartEstimateResponse:
    prices = {product.id: product.price for product in PRODUCTS}
    total = sum(prices.get(item.product_id, 0) * item.quantity for item in request.items)
    item_count = sum(item.quantity for item in request.items)
    return CartEstimateResponse(total=total, item_count=item_count)


@app.get("/api/recipes", response_model=list[RecipeRecommendation])
def get_recipes(
    ingredients: Annotated[list[str] | None, Query(description="보유 재료 목록")]=None,
) -> list[RecipeRecommendation]:
    owned = set(ingredients or [])
    recommendations = []

    for recipe in RECIPES:
        matched = [ingredient for ingredient in recipe["ingredients"] if ingredient in owned]
        missing = [ingredient for ingredient in recipe["ingredients"] if ingredient not in owned]
        recommendations.append(RecipeRecommendation(**recipe, matched=matched, missing=missing))

    return sorted(recommendations, key=lambda recipe: len(recipe.matched), reverse=True)
