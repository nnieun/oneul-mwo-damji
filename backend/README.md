# 오늘 뭐 담지 Backend

FastAPI 기반 REST API입니다. 상품과 레시피 기본 데이터는 SQLite에 저장됩니다.

## 실행

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 4000
```

API 문서: <http://localhost:4000/docs>

## API

- `GET /api/health`
- `GET /api/products`
- `POST /api/cart/estimate`
- `POST /api/recognition/candidates`
- `POST /api/cart/items`
- `GET /api/recipes?ingredients=계란&ingredients=대파`

## 테스트

```powershell
pytest
```

`POST /api/recognition/candidates`는 Roboflow 객체 탐지 결과의 `label`, `confidence`, `x`, `y`, `width`, `height`를 서비스 상품 후보로 변환합니다. 낮은 신뢰도는 제외하고 동일 상품은 가장 높은 신뢰도의 후보 하나만 반환합니다.
