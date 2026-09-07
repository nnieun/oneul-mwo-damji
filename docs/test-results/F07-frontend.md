
# Frontend verification

- Started: 2026-09-07T11:25:07.975118+09:00
- Base commit: 4ecb0ee + working tree
- Runtime: v24.19.0

## TypeScript

- Command: `node node_modules/typescript/bin/tsc --noEmit`
- Exit code: 0
- Result: PASS
- Duration: 0.98s

```text

```

## Production build

- Command: `node node_modules/vite/bin/vite.js build`
- Exit code: 0
- Result: PASS
- Duration: 0.64s

```text
(!) Your Vite config uses features that are unsupported by `configLoader: 'native'`, which is planned to become the default in a future major version of Vite:
  - `__dirname` (vite.config.ts:31:27). Use `import.meta.dirname` instead
  - JSON import "./.figma/make/site.json" without import attributes (vite.config.ts:6:31). Add `with { type: 'json' }`
Set `VITE_CONFIG_NATIVE_IGNORE_WARNING=true` to suppress this warning.
vite v8.2.2 building client environment for production...
transforming...
✓ 17 modules transformed.
rendering chunks...
computing gzip size...
dist/robots.txt                   0.02 kB │ gzip:  0.04 kB
dist/index.html                   0.80 kB │ gzip:  0.44 kB
dist/assets/index-jCQSG_i4.css    9.44 kB │ gzip:  3.03 kB
dist/assets/index-DFoQF3bb.js   204.79 kB │ gzip: 64.68 kB

✓ built in 297ms

```

## 기록 도구 수정

타입 검사와 빌드는 통과했으나 Windows cp949 콘솔에서 빌드 로그의 체크 표시를 출력하는 중 기록 도구가 실패했습니다. 결과 MD는 저장되었으며, 도구 출력을 UTF-8로 고정하고 다시 실행했습니다.

# Frontend verification

- Started: 2026-09-07T11:25:39.472621+09:00
- Base commit: 4ecb0ee + working tree
- Runtime: v24.19.0

## TypeScript

- Command: `node node_modules/typescript/bin/tsc --noEmit`
- Exit code: 0
- Result: PASS
- Duration: 0.94s

```text

```

## Production build

- Command: `node node_modules/vite/bin/vite.js build`
- Exit code: 0
- Result: PASS
- Duration: 0.50s

```text
(!) Your Vite config uses features that are unsupported by `configLoader: 'native'`, which is planned to become the default in a future major version of Vite:
  - `__dirname` (vite.config.ts:31:27). Use `import.meta.dirname` instead
  - JSON import "./.figma/make/site.json" without import attributes (vite.config.ts:6:31). Add `with { type: 'json' }`
Set `VITE_CONFIG_NATIVE_IGNORE_WARNING=true` to suppress this warning.
vite v8.2.2 building client environment for production...
transforming...
✓ 17 modules transformed.
rendering chunks...
computing gzip size...
dist/robots.txt                   0.02 kB │ gzip:  0.04 kB
dist/index.html                   0.80 kB │ gzip:  0.44 kB
dist/assets/index-jCQSG_i4.css    9.44 kB │ gzip:  3.03 kB
dist/assets/index-DFoQF3bb.js   204.79 kB │ gzip: 64.68 kB

✓ built in 152ms

```
