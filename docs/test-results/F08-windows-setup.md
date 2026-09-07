# F08 Windows 실행 환경 수정

- 원인: 사용자 PATH에 Node와 pnpm이 등록되어 있지 않음. 기존 개발 검증은 별도 런타임 경로 사용.
- 조치: 공식 Node.js ZIP의 SHA256 검증 후 사용자 Programs 폴더에 설치, pnpm 10.34.3 설치, 사용자 PATH 등록.
- Node: v24.20.0
- pnpm: 10.34.3
- PowerShell 실행 정책: Restricted 유지. pnpm.cmd로 실행.
- 의존성 검증: pnpm.cmd --dir frontend install --frozen-lockfile, 종료 코드 0. Lockfile is up to date / Already up to date.
- 타입 검증: pnpm.cmd --dir frontend typecheck, 종료 코드 0.
- 결과: PASS
- 백엔드 코드 변경 없음. pytest 재실행 대상 없음.
- 현재 열려 있는 터미널은 사용자·시스템 PATH를 다시 읽거나 VS Code를 완전히 재시작해야 함.

## 타입 검사 출력

 > oneul-mwo-damji-frontend@1.0.0 typecheck C:\worksapces\oneul-mwo-damji\frontend > tsc --noEmit 
