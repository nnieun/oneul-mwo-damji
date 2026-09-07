# FastAPI 백엔드

실행 방법은 [프로젝트 README](../README.md)를 참고하세요. 단일 프로세스·단일 활성 장바구니를 대상으로 합니다. 카메라 촬영은 브라우저(접속 기기)에서 이루어지며, 백엔드는 업로드된 프레임을 Roboflow로 전달하는 역할만 합니다.

## API 문서

- Swagger UI: <http://localhost:4000/docs>
- OpenAPI JSON: <http://localhost:4000/openapi.json>
- 저장된 명세: [docs/openapi.json](../docs/openapi.json)
- 명세 갱신: 루트에서 `backend\.venv\Scripts\python.exe scripts/export_openapi.py`

각 경로의 요청·응답 모델, 설명, 오류는 Swagger에 포함됩니다.

## 핵심 계약

- `POST /api/carts`는 활성 장바구니가 없으면 만들고, 있으면 기존 장바구니를 반환합니다.
- `POST /api/carts/{cart_id}/items`에는 8~128자 `Idempotency-Key` 헤더가 필수입니다.
- 같은 키와 같은 본문을 재전송하면 최초 응답을 반환합니다. 내용이 달라지면 409입니다. 재전송 응답 뒤 GET으로 최신 장바구니를 다시 조회하세요.
- `POST /api/recognition/scan`은 `multipart/form-data`로 `image` 필드(브라우저 카메라로 촬영한 JPEG)를 받습니다. 더미 모드에서는 내용을 사용하지 않지만 필드는 여전히 필요합니다.
- `candidate_id`를 지정하면 후보가 미처리·유효한지 확인하고 장바구니 저장과 함께 확정합니다. 다른 `product_id`를 보내 오인식을 수정할 수 있습니다.
- 후보는 120초 동안 유효합니다. 확정·제외·만료 후보는 다시 사용할 수 없습니다.
- 수량은 1~999의 정수입니다. PATCH는 최종 수량을 설정하고 삭제는 DELETE를 사용합니다.
- 금액은 최초 담을 때 저장한 단가 × 수량으로 서버에서 계산합니다.
- 추천은 식재료 ID를 기준으로 계산하며 부족한 필수 재료가 0종이면 ready, 1~2종이고 일치 재료가 있으면 almost입니다.
- 추천 응답의 revision은 장바구니 revision과 함께 사용하여 오래된 화면 갱신을 방지합니다.
- 모델 라벨 기본값은 [seed.py](app/seed.py)의 영문 라벨과 한국어 식재료명입니다. 실제 모델의 라벨은 모델 버전별로 재정의할 수 있습니다.

## 이전 API 전환

- `/api/cart/items`: 종전처럼 단일 상품 견적만 반환합니다. 저장하지 않으며 Swagger에서 deprecated입니다.
- `/api/cart/estimate`: 종전 견적 기능을 유지하되 미등록 상품을 404로 거부합니다.
- `/api/recipes`: 정규화된 레시피 상세 목록으로 전환했습니다. 이전 `ingredients` 쿼리 방식은 `/api/recipes/legacy`로 이동했으며 deprecated입니다.
- `/api/recognition/candidates`: 외부 탐지 결과 입력을 유지하면서 후보 ID·유효기간·상태를 추가했습니다. mode=supplied로 구분합니다.

## DB와 마이그레이션

SQLite 파일은 기본 `data/app.db`입니다. 기존 파일이 있으면 스키마 버전 0에서 1로 올리고 기존 상품명·가격과 사용자 레시피를 보존합니다. 기본 시드 레시피는 기획서 기준으로 갱신됩니다. 스키마·시드·버전 갱신은 하나의 트랜잭션으로 처리합니다. 연결은 작업마다 열고 닫으며 외래 키 검사를 활성화합니다. 장바구니와 요청 키는 서버 재시작 후에도 유지됩니다.

시연 DB를 초기화하려면 서버를 종료하고 기존 DB를 별도 백업 위치에 보관한 뒤 새 `DATABASE_PATH`를 지정하세요. 앱 시작이 기존 장바구니를 자동으로 삭제하지 않습니다.

## 실제 장치 테스트

카메라 촬영은 브라우저에서 이루어지므로, 실제 카메라 자체는 `pnpm test:e2e`(브라우저 카메라 시작·종료 UI 확인)와 실제 기기로 앱을 열어보는 수동 시연으로 확인합니다. 백엔드에서 확인할 대상은 Roboflow 추론 하나뿐입니다.

브라우저 카메라 미리보기로 촬영한 JPEG 파일을 준비한 뒤, 프로젝트 루트 PowerShell에서:

```powershell
$env:RUN_LIVE_MODEL_TESTS = '1'
$env:SAMPLE_IMAGE_PATH = 'C:\path\to\captured-frame.jpg'
backend\.venv\Scripts\python.exe scripts/test_report.py H02-model tests/test_hardware.py -k live_roboflow_inference
```

실제 모델 검증은 `ROBOFLOW_MODEL_ID`, `ROBOFLOW_API_KEY`를 테스트 프로세스 환경변수로 설정하고 실행합니다. pytest는 `.env`를 자동으로 읽지 않습니다.

기본 전체 테스트에서 이 항목은 SKIP입니다. 하드웨어 테스트는 연결·응답 형식 검증이며 인식 정확도나 mAP 측정을 대신하지 않습니다.

## 기술 참고

- [FastAPI Swagger 설정](https://fastapi.tiangolo.com/tutorial/metadata/)
- [FastAPI 테스트 수명 주기](https://fastapi.tiangolo.com/advanced/testing-events/)
- [MDN MediaDevices.getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [Roboflow Hosted Object Detection 요청 형식](https://docs.roboflow.com/deploy/serverless/object-detection)
