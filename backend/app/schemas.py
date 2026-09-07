from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class Product(BaseModel):
    id: int
    name: str
    price: int = Field(ge=0, description='시연용 원화 가격')
    ingredients: list[str]
    emoji: str = '🛒'

class ErrorResponse(BaseModel):
    detail: str = Field(examples=['상품을 찾을 수 없습니다.'])

ERRORS = {code: {'model': ErrorResponse, 'description': message} for code, message in [(404,'대상을 찾을 수 없음'), (409,'상태 충돌 또는 중복 요청 내용 불일치'), (413,'업로드 용량 초과'), (503,'장치 또는 서비스 사용 불가'), (504,'모델 응답 시간 초과'), (502,'모델 응답 오류')]}

class CartLine(BaseModel):
    product_id: int
    name: str
    emoji: str
    ingredients: list[str]
    quantity: int
    unit_price: int
    subtotal: int

class Cart(BaseModel):
    id: str
    status: str
    revision: int
    items: list[CartLine]
    total: int
    item_count: int

class AddItem(BaseModel):
    model_config = ConfigDict(json_schema_extra={'example': {'product_id':1,'quantity':1}})
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1,ge=1,le=999,strict=True)
    candidate_id: str | None = Field(default=None, description='인식 후보 확인 시 지정. 상품 수정 시 product_id를 변경 가능')

class Quantity(BaseModel):
    quantity: int = Field(ge=1,le=999,strict=True,examples=[2],description='최종 수량. 삭제는 DELETE API 사용')

class Ingredient(BaseModel):
    id: int
    name: str
    amount: str
    required: bool

class Recipe(BaseModel):
    id: int
    name: str
    cooking_time_minutes: int
    servings: int
    ingredients: list[Ingredient]
    steps: list[str]
    is_dummy: bool

class Recommendation(Recipe):
    matched: list[str]
    missing: list[str]
    optional_missing: list[str]
    match_ratio: float
    category: Literal['ready','almost']

class Recommendations(BaseModel):
    cart_id: str
    revision: int
    owned: list[str]
    recipes: list[Recommendation]
    note: str = '재료 종류 기준 추천입니다. 물은 기본 제공하며 실제 조리 분량은 확인해 주세요.'
