import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .db import Database
from .schemas import Product, ERRORS
from .camera import Camera, router as camera_router
from .recognition import RoboflowModel, configure_labels, router as recognition_router
from .cart import router as cart_router
from .recipes import router as recipe_router

class CartItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=0,le=999,strict=True)

class CartEstimateRequest(BaseModel):
    items: list[CartItem] = Field(default_factory=list,max_length=1000)

class CartEstimateResponse(BaseModel):
    total: int
    item_count: int

class ConfirmCandidateRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1,ge=1,le=999,strict=True)

class RecipeRecommendation(BaseModel):
    id: int
    name: str
    ingredients: list[str]
    matched: list[str]
    missing: list[str]
    time: str


def create_app(database: Database | None = None, camera=None, model=None) -> FastAPI:
    db=database or Database(os.getenv('DATABASE_PATH','data/app.db'))
    camera=camera or Camera(demo=os.getenv('DEMO_MODE','false').lower()=='true',device=int(os.getenv('CAMERA_DEVICE','0')))
    model=model or RoboflowModel(demo=camera.demo)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            db.initialize()
            configure_labels(db,model)
            yield
        finally:
            camera.stop()
            db.close()

    app=FastAPI(
        title='오늘 뭐 담지 API',
        description='SQLite 장바구니, OpenCV 카메라, Roboflow 상품 인식 및 재료 기반 요리 추천. 금액과 레시피는 시연용입니다.',
        version='1.0.0',responses=ERRORS,lifespan=lifespan,
        openapi_tags=[{'name':name,'description':description} for name,description in [
            ('Health','서버 상태'),('Products','시연 상품과 가격'),('Cart','저장된 장바구니와 예상 금액'),
            ('Recipes','레시피 상세 및 장바구니 재료 추천'),('Camera','백엔드 PC 카메라 제어 및 미리보기'),('Recognition','사용자 확인 전 인식 후보'),
        ]],
    )
    app.state.database=db
    app.state.camera=camera
    app.state.model=model
    origins=os.getenv('CORS_ORIGINS','http://localhost:8443,http://127.0.0.1:8443')
    app.add_middleware(CORSMiddleware,allow_origins=[s.strip() for s in origins.split(',') if s.strip()],allow_credentials=False,allow_methods=['GET','POST','PATCH','DELETE'],allow_headers=['Content-Type','Idempotency-Key'])

    @app.get('/api/health',tags=['Health'],summary='서버 상태 확인')
    def health() -> dict[str,str | bool]:
        return {'ok':True,'service':'oneul-mwo-damji-backend'}

    @app.get('/api/products',response_model=list[Product],tags=['Products'],summary='상품 목록 및 이름 검색')
    def get_products(q: str = Query(default='',max_length=100,description='상품명 검색어')):
        return [Product(**row) for row in db.products() if q.casefold() in row['name'].casefold()]

    @app.post('/api/cart/estimate',response_model=CartEstimateResponse,tags=['Cart'],deprecated=True,summary='이전 금액 계산 API: 저장하지 않음')
    def estimate_cart(request: CartEstimateRequest):
        prices=db.product_prices()
        if any(item.product_id not in prices for item in request.items):
            raise HTTPException(404,'상품을 찾을 수 없습니다.')
        return dict(total=sum(prices[item.product_id]*item.quantity for item in request.items),item_count=sum(item.quantity for item in request.items))

    @app.post('/api/cart/items',response_model=CartEstimateResponse,tags=['Cart'],deprecated=True,summary='이전 단일 상품 견적: 저장하지 않음',description='저장하려면 POST /api/carts/{cart_id}/items를 사용하세요.')
    def legacy_item(request: ConfirmCandidateRequest):
        prices=db.product_prices()
        if request.product_id not in prices:
            raise HTTPException(404,'상품을 찾을 수 없습니다.')
        return dict(total=prices[request.product_id]*request.quantity,item_count=request.quantity)

    @app.get('/api/recipes/legacy',response_model=list[RecipeRecommendation],tags=['Recipes'],deprecated=True,summary='이전 재료 문자열 기반 추천')
    def legacy_recipes(ingredients: Annotated[list[str] | None,Query(description='보유 재료 목록')]=None):
        owned=set(ingredients or [])
        results=[]
        for recipe in db.recipes():
            required=recipe['ingredients'].split(',')
            results.append(dict(id=recipe['id'],name=recipe['name'],ingredients=required,matched=[i for i in required if i in owned],missing=[i for i in required if i not in owned],time=recipe['cooking_time']))
        return sorted(results,key=lambda r:len(r['matched']),reverse=True)

    app.include_router(cart_router(db))
    app.include_router(recipe_router(db))
    app.include_router(camera_router(camera))
    app.include_router(recognition_router(db,camera,model))
    return app

app=create_app()
