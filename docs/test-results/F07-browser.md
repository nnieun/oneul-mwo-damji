
# Browser integration run

- Started: 2026-09-07T02:16:15.360Z
- Base commit: 51b6dea + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.19.0, win32
- Browser: chrome
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: FAIL
- Real camera / Roboflow: NOT RUN (demo test)

- FAIL: Error: Server exited: failed to load config from C:\worksapces\oneul-mwo-damji\frontend\vite.config.ts
error when starting dev server:
Error: Build failed with 1 error:

[31m[JSON_PARSE] [0mexpected value at line 1 column 1

    at aggregateBindingErrorsIntoJsError (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/rolldown@1.2.7/node_modules/rolldown/dist/shared/error-BP8lJHle.mjs:48:18)
    at unwrapBindingResult (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/rolldown@1.2.7/node_modules/rolldown/dist/shared/error-BP8lJHle.mjs:18:128)
    at #build (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/rolldown@1.2.7/node_modules/rolldown/dist/shared/rolldown-DfXO5K1m.mjs:133:34)
    at async bundleConfigFile (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/vite@8.2.2_@types+node@22.20.1_jiti@2.7.0/node_modules/vite/dist/node/chunks/node.js:37116:17)
    at async bundleAndLoadConfigFile (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/vite@8.2.2_@types+node@22.20.1_jiti@2.7.0/node_modules/vite/dist/node/chunks/node.js:37014:18)
    at async loadConfigFromFile (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/vite@8.2.2_@types+node@22.20.1_jiti@2.7.0/node_modules/vite/dist/node/chunks/node.js:36975:42)
    at async resolveConfig (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/vite@8.2.2_@types+node@22.20.1_jiti@2.7.0/node_modules/vite/dist/node/chunks/node.js:36581:22)
    at async _createServer (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/vite@8.2.2_@types+node@22.20.1_jiti@2.7.0/node_modules/vite/dist/node/chunks/node.js:26388:65)
    at async CAC.<anonymous> (file:///C:/worksapces/oneul-mwo-damji/frontend/node_modules/.pnpm/vite@8.2.2_@types+node@22.20.1_jiti@2.7.0/node_modules/vite/dist/node/cli.js:708:18) {
  errors: [Getter/Setter]
}

    at ready (file:///C:/worksapces/oneul-mwo-damji/frontend/tests/e2e.mjs:33:37)
    at async file:///C:/worksapces/oneul-mwo-damji/frontend/tests/e2e.mjs:43:3

# Browser integration run

- Started: 2026-09-07T02:17:16.113Z
- Base commit: 51b6dea + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.19.0, win32
- Browser: chrome
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, camera shutdown, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T02:25:41.217Z
- Base commit: 4ecb0ee + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.19.0, win32
- Browser: chrome
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, camera shutdown, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T02:42:13.455Z
- Base commit: f4f2f18 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: FAIL
- Real camera / Roboflow: NOT RUN (demo test)

- FAIL: browserType.launch: Executable doesn't exist at C:\Users\Admin\AppData\Local\ms-playwright\chromium_headless_shell-1234\chrome-headless-shell-win64\chrome-headless-shell.exe
╔════════════════════════════════════════════════════════════╗
║ Looks like Playwright was just installed or updated.       ║
║ Please run the following command to download new browsers: ║
║                                                            ║
║     pnpm exec playwright install                           ║
║                                                            ║
║ <3 Playwright Team                                         ║
╚════════════════════════════════════════════════════════════╝
    at C:\worksapces\oneul-mwo-damji\frontend\tests\e2e.mjs:44:26

# Browser integration run

- Started: 2026-09-07T02:42:47.881Z
- Base commit: f4f2f18 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: FAIL
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- FAIL: locator.click: Timeout 30000ms exceeded.
Call log:
[2m  - waiting for getByRole('button', { name: '카메라 종료', exact: true })[22m

    at C:\worksapces\oneul-mwo-damji\frontend\tests\e2e.mjs:101:61

# Browser integration run

- Started: 2026-09-07T02:44:26.764Z
- Base commit: f4f2f18 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T03:17:22.452Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: FAIL
- Real camera / Roboflow: NOT RUN (demo test)

- FAIL: AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:

6 !== 3

    at file:///C:/worksapces/oneul-mwo-damji/frontend/tests/e2e.mjs:55:10

# Browser integration run

- Started: 2026-09-07T03:17:49.705Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: FAIL
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- FAIL: locator.click: Error: strict mode violation: getByRole('button', { name: '선택 상품 담기' }) resolved to 4 elements:
    1) <button class="primary full">선택 상품 담기</button> aka getByRole('button', { name: '선택 상품 담기' }).first()
    2) <button class="primary full">선택 상품 담기</button> aka getByRole('button', { name: '선택 상품 담기' }).nth(1)
    3) <button class="primary full">선택 상품 담기</button> aka getByRole('button', { name: '선택 상품 담기' }).nth(2)
    4) <button class="primary full">선택 상품 담기</button> aka getByRole('button', { name: '선택 상품 담기' }).nth(3)

Call log:
[2m  - waiting for getByRole('button', { name: '선택 상품 담기' })[22m

    at C:\worksapces\oneul-mwo-damji\frontend\tests\e2e.mjs:72:52

# Browser integration run

- Started: 2026-09-07T03:18:22.700Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T04:22:26.306Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T04:31:37.608Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T04:38:10.138Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T04:44:21.788Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T04:52:22.392Z
- Base commit: fb71cf6 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors

# Browser integration run

- Started: 2026-09-07T04:59:21.243Z
- Base commit: ad660e8 + working tree
- Command: pnpm --dir frontend test:e2e
- Runtime: Node v24.20.0, win32
- Browser: Playwright Chromium
- Backend: isolated temporary SQLite, DEMO_MODE=true
- Result: PASS
- Real camera / Roboflow: NOT RUN (demo test)

- PASS: demo camera preview, scan, confirm and dismiss
- PASS: lost response retry does not duplicate cart item
- PASS: required/optional ingredients and recipe detail rendered from API
- PASS: quantity, delete, server total and shopping summary
- PASS: reload persistence, mobile overflow, browser camera start/stop, no browser runtime errors
