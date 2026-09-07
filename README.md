# 오늘 뭐 담지

카메라 인식 후보를 확인해 장바구니에 담고, 예상 금액과 재료 기반 요리를 확인하는 로컬 시연용 스마트 카트입니다.

- React + TypeScript + Vite
- FastAPI + SQLite
- 브라우저(접속 기기) 카메라 / Roboflow 객체 탐지
- 상품 18종, 더미 레시피 10종
- Swagger: 실행 후 <http://localhost:4000/docs>

## 실행 환경

검증 환경은 Windows, Python 3.12, Node 24, pnpm 10.34.3입니다. Node 22를 사용하는 경우 Vite 8이 지원하는 22.12 이상을 사용하세요. Python 및 Node/pnpm 실행 파일이 PATH에 있어야 합니다.

## Windows에서 Node·pnpm 준비

`node` 또는 `pnpm`이 인식되지 않으면 먼저 [Node.js 공식 다운로드](https://nodejs.org/en/download)에서 Node 24 LTS를 설치하고 PATH 등록 옵션을 사용하세요. 설치 후 VS Code를 완전히 종료했다가 다시 실행하세요.

PowerShell에서 프로젝트 지정 버전의 pnpm을 설치합니다.

```powershell
node --version
npm.cmd install --global pnpm@10.34.3
pnpm.cmd --version
```

현재 터미널에서 새 사용자 PATH를 반영하려면 다음 명령을 실행하세요.

```powershell
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
```

Windows 안내에서는 `pnpm.cmd`를 사용합니다. PowerShell 실행 정책이 `Restricted`여도 실행 정책 변경 없이 CMD 실행 파일을 호출할 수 있습니다. macOS·Linux에서는 `pnpm`을 사용하세요. [pnpm 공식 설치 안내](https://pnpm.io/installation)

## 백엔드 실행

PowerShell 터미널에서:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --env-file .env --host 127.0.0.1 --port 4000
```

기존 `.env`가 있으면 복사하지 말고 필요한 설정만 반영하세요. 예제 환경은 `DEMO_MODE=true`로 외부 모델과 실제 카메라 없이 전체 흐름을 확인할 수 있습니다. `.env`를 로드하지 않은 기본 실행은 실제 인식 모드이며, 이 경우 브라우저에서 카메라 사용을 허용해야 스캔할 수 있습니다.

## 프론트 실행

다른 PowerShell 터미널에서:

```powershell
cd frontend
pnpm.cmd install --frozen-lockfile
pnpm.cmd dev
```

<http://localhost:8443>에서 쇼핑을 시작하세요. `/api`는 백엔드 4000번 포트로 프록시됩니다. 다른 서버를 사용하면 `VITE_API_BASE_URL`을 지정하고 백엔드 `CORS_ORIGINS`에 프론트 주소를 등록하세요.

## 시연 순서

1. 쇼핑 시작 → 카메라 시작 → 상품 스캔. 실제 모드에서는 브라우저가 카메라 사용 권한을 물어보며, 허용해야 접속 기기의 카메라 미리보기가 나타납니다.
2. 더미 모드에서는 계란·두부·대파 후보가 표시됩니다. 확인 후 담거나 제외하세요.
3. 상품 직접 선택으로 소금 등 추가 재료를 담으세요.
4. 장바구니에서 수량·삭제·예상 금액을 확인하세요.
5. 요리 추천에서 보유 재료, 부족 재료, 조리 순서를 확인하세요.
6. 새로고침 후 쇼핑 시작을 누르면 저장된 장바구니가 복원됩니다.
7. 시연이 끝나면 카메라 종료를 누르세요.

실제 결제는 제공하지 않습니다. 물만 기본 보유로 취급하며 양념은 장바구니에 담아야 보유 재료로 계산됩니다. 추천은 재료 종류 기준으로, 실제 조리 가능 분량을 계산하지 않습니다.

## 실제 카메라·Roboflow 연결

`backend/.env`에서 `DEMO_MODE=false`로 바꾸고 `ROBOFLOW_MODEL_ID`(예: `sang-rqj4u/ozm-4-yolov8n-t1`), `ROBOFLOW_API_KEY`를 설정한 뒤 서버를 재시작하세요. 모델 라벨이 기본 영문 라벨과 다르면 `ROBOFLOW_LABEL_MAP`에 정확한 라벨과 상품 ID를 JSON으로 지정하세요. 상품 ID는 Swagger 상품 목록에서 확인할 수 있습니다.

카메라는 브라우저로 접속한 기기의 카메라를 사용합니다(백엔드 PC의 카메라가 아닙니다). 실제 모드에서 카메라 시작을 누르면 브라우저가 카메라 권한을 요청하며, 허용하면 미리보기가 나타납니다. 상품 스캔을 누르면 그 순간의 프레임을 JPEG로 캡처해 백엔드로 업로드하고, 백엔드가 이를 Roboflow 추론 API로 전달합니다. 모델 키는 백엔드 환경변수에만 두고 프론트 환경변수에는 넣지 마세요. 모델 키가 없으면 설정 안내를 반환하며 더미 결과로 조용히 대체하지 않습니다. HTTPS가 아닌 주소에서는 브라우저가 카메라 권한을 막을 수 있으므로, 백엔드 PC가 아닌 다른 기기에서 접속할 때는 `localhost`가 아닌 실제 접속 주소가 브라우저의 보안 컨텍스트 요건(HTTPS 또는 신뢰할 수 있는 로컬 네트워크 설정)을 만족하는지 확인하세요.

본 구현에서 실제 장치·학습 모델 검증 및 mAP50 측정은 미실행입니다. 별도 하드웨어 테스트와 실제 상품 시연이 필요합니다.

## 테스트와 결과 기록

프로젝트 루트에서:

```powershell
backend\.venv\Scripts\python.exe scripts/test_report.py F07-integration
backend\.venv\Scripts\python.exe scripts/test_report.py F03-cart tests/test_cart.py
```

실제 결과가 `docs/test-results/<기능명>.md`에 누적됩니다. 실패 이력도 보존합니다. 기능 구현·pytest·결과 MD·Swagger 반영 후 기능 단위로 커밋합니다.

프론트 검사 및 브라우저 통합 테스트:

```powershell
cd frontend
pnpm.cmd typecheck
pnpm.cmd build
pnpm.cmd exec playwright install chromium
pnpm.cmd test:e2e
```

설치된 Chrome을 사용하려면 `BROWSER_CHANNEL=chrome`을 환경변수로 지정할 수 있습니다. 브라우저 테스트는 4011·8445 포트에 테스트 서버를 자동 실행하고 임시 SQLite와 더미 영상으로 검증한 후 서버를 종료합니다. 포트가 이미 사용 중이면 해당 테스트 서버를 시작할 수 없습니다. 기본 Python 경로는 `backend/.venv`이며 `BACKEND_PYTHON`으로 변경할 수 있습니다.

## 문서

- [구현 기획서](docs/implementation-plan.md)
- [백엔드 API 및 운영 안내](backend/README.md)
- [OpenAPI 명세](docs/openapi.json)
- [개발·검증 결과](docs/implementation-status.md)
- [pytest 전체 결과](docs/test-results/F07-integration.md)
- [브라우저 통합 결과](docs/test-results/F07-browser.md)

