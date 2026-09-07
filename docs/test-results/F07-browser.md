
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
