import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import Database


from .schemas import Product, ERRORS


class CartItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=0)


class CartEstimateRequest(BaseModel):
    items: list[CartItem] = Field(default_factory=list)


class CartEstimateResponse(BaseModel):
    total: int
    item_count: int


class Detection(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None


class RecognitionRequest(BaseModel):
    detections: list[Detection] = Field(default_factory=list)
    confidence_threshold: float = Field(default=0.75, ge=0, le=1)


class RecognitionCandidate(BaseModel):
    product: Product
    confidence: float
    position: dict[str, float | None]


class RecognitionResponse(BaseModel):
    candidates: list[RecognitionCandidate]


class ConfirmCandidateRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class RecipeRecommendation(BaseModel):
    id: int
    name: str
    ingredients: list[str]
    matched: list[str]
    missing: list[str]
    time: str


def create_app(database: Database | None = None) -> FastAPI:
    db = database or Database(os.getenv("DATABASE_PATH", "data/app.db"))

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        db.initialize()
        try:
            yield
        finally:
            db.close()

    app = FastAPI(
        title="오늘 뭐 담지 API",
        description="AI 스마트 마트카트 MVP를 위한 상품·인식·장바구니·요리 추천 API",
        version="1.0.0",
        responses=ERRORS,
        openapi_tags=[{"name": name} for name in ["Health", "Products", "Cart", "Recipes", "Camera", "Recognition"]],
        lifespan=lifespan,
    )
    app.state.database = db
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8443", "http://127.0.0.1:8443"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health", tags=["Health"], summary="?? ?? ??")
    def health() -> dict[str, str | bool]:
        return {"ok": True, "service": "oneul-mwo-damji-backend"}

    @app.get("/api/products", response_model=list[Product], tags=["Products"], summary="?? ?? ? ?? ??")
    def get_products(q: str = Query(default="", max_length=100, description="??? ???")):
        return [Product(**row) for row in db.products() if q.casefold() in row["name"].casefold()]

    @app.post("/api/cart/estimate", response_model=CartEstimateResponse, tags=["Cart"], deprecated=True, summary="?? ?? ?? API (???? ??)")
    def estimate_cart(request: CartEstimateRequest) -> CartEstimateResponse:
        prices = db.product_prices()
        if any(item.product_id not in prices for item in request.items):
            raise HTTPException(status_code=404, detail="??? ?? ? ????.")
        return CartEstimateResponse(
            total=sum(prices.get(item.product_id, 0) * item.quantity for item in request.items),
            item_count=sum(item.quantity for item in request.items),
        )

    @app.post("/api/recognition/candidates", response_model=RecognitionResponse, tags=["Recognition"])
    def recognition_candidates(request: RecognitionRequest) -> RecognitionResponse:
        products = {row["ingredient"]: Product(id=row["id"], name=row["name"], price=row["price"], ingredients=[row["ingredient"]]) for row in db.products()}
        best_by_product: dict[int, tuple[Product, Detection]] = {}
        for detection in request.detections:
            product = products.get(detection.label)
            if product is None or detection.confidence < request.confidence_threshold:
                continue
            current = best_by_product.get(product.id)
            if current is None or detection.confidence > current[1].confidence:
                best_by_product[product.id] = (product, detection)
        return RecognitionResponse(
            candidates=[
                RecognitionCandidate(
                    product=product,
                    confidence=detection.confidence,
                    position={"x": detection.x, "y": detection.y, "width": detection.width, "height": detection.height},
                )
                for product, detection in best_by_product.values()
            ]
        )

    @app.post("/api/cart/items", response_model=CartEstimateResponse, tags=["Cart"], deprecated=True, summary="?? ?? ?? ?? API (???? ??)")
    def confirm_candidate(request: ConfirmCandidateRequest) -> CartEstimateResponse:
        prices = db.product_prices()
        if request.product_id not in prices:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
        return CartEstimateResponse(total=prices[request.product_id] * request.quantity, item_count=request.quantity)

    @app.get("/api/recipes", response_model=list[RecipeRecommendation], tags=["Recipes"])
    def get_recipes(
        ingredients: Annotated[list[str] | None, Query(description="보유 재료 목록")] = None,
    ) -> list[RecipeRecommendation]:
        owned = set(ingredients or [])
        recommendations = []
        for recipe in db.recipes():
            required = recipe["ingredients"].split(",")
            matched = [ingredient for ingredient in required if ingredient in owned]
            missing = [ingredient for ingredient in required if ingredient not in owned]
            recommendations.append(RecipeRecommendation(id=recipe["id"], name=recipe["name"], ingredients=required, matched=matched, missing=missing, time=recipe["cooking_time"]))
        return sorted(recommendations, key=lambda recipe: len(recipe.matched), reverse=True)

    return app


app = create_app()
