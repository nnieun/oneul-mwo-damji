# 오늘 뭐 담지 Backend

FastAPI 기반 REST API입니다.

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
- `GET /api/recipes?ingredients=계란&ingredients=대파`
