import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { mkdtemp, mkdir, appendFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontend=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..')
const root=path.resolve(frontend,'..')
const temp=await mkdtemp(path.join(tmpdir(),'cart-e2e-'))
const python=process.env.BACKEND_PYTHON || path.join(root,'backend','.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python')
const report=path.join(root,'docs/test-results/F07-browser.md')
const screenshots=path.join(root,'docs/test-results/images')
await mkdir(screenshots,{recursive:true})
const results=[]
const errors=[]
const processes=[]
let browser
let failure
const started=new Date().toISOString()
const base=execFileSync('git',['rev-parse','--short','HEAD'],{cwd:root,encoding:'utf8'}).trim()
function run(command,args,cwd,env){
  const child=spawn(command,args,{cwd,env:{...process.env,...env},windowsHide:true,stdio:['ignore','pipe','pipe']})
  child.output=''
  child.stdout.on('data',data=>child.output+=data)
  child.stderr.on('data',data=>child.output+=data)
  processes.push(child)
  return child
}
async function ready(url,child){
  for(let i=0;i<100;i++){
    if(child.exitCode!==null) throw new Error(`Server exited: ${child.output}`)
    try{if((await fetch(url)).ok) return}catch{}
    await new Promise(resolve=>setTimeout(resolve,200))
  }
  throw new Error(`Server startup timeout: ${child.output}`)
}
try {
  const backend=run(python,['-m','uvicorn','app.main:app','--host','127.0.0.1','--port','4011'],path.join(root,'backend'),{DEMO_MODE:'true',DATABASE_PATH:path.join(temp,'e2e.db'),PYTHONIOENCODING:'utf-8',ROBOFLOW_LABEL_MAP:'{}',CONFIDENCE_THRESHOLD:'0.75'})
  await ready('http://127.0.0.1:4011/api/health',backend)
  const vite=run(process.execPath,[path.join(frontend,'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port','8445'],frontend,{BACKEND_URL:'http://127.0.0.1:4011',VITE_API_BASE_URL:''})
  await ready('http://127.0.0.1:8445',vite)
  browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL?{channel:process.env.BROWSER_CHANNEL}:{})})
  const page=await browser.newPage({viewport:{width:390,height:844}})
  page.on('pageerror',error=>errors.push(error.message))
  await page.goto('http://127.0.0.1:8445')
  await page.getByRole('button',{name:'쇼핑 시작하기'}).click()
  await page.getByRole('button',{name:'카메라 시작',exact:true}).waitFor()
  assert.equal(await page.locator('.summary').innerText(),'예상 구매금액 · 0개\n0원 →')
  await page.getByRole('button',{name:'카메라 시작',exact:true}).click()
  await page.getByText('더미 모드 · 실제 인식 아님 · 연결됨',{exact:true}).waitFor()
  await page.getByRole('button',{name:'상품 스캔',exact:true}).click()
  await page.locator('.candidate').nth(2).waitFor()
  assert.equal(await page.locator('.candidate').count(),3)
  await page.locator('.candidate').first().getByRole('button',{name:'확인 후 담기'}).click()
  await page.getByText('3,200원 →',{exact:true}).waitFor()
  await page.locator('.candidate').first().getByRole('button',{name:'제외',exact:true}).click()
  await page.waitForFunction(()=>document.querySelectorAll('.candidate').length===1)
  results.push('PASS: demo camera preview, scan, confirm and dismiss')

  // Simulate a committed POST whose response is lost. Retry must use the same key.
  let lost=false
  await page.route('**/api/carts/*/items',async route=>{
    if(!lost && route.request().method()==='POST'){
      lost=true
      await route.fetch()
      await route.abort('failed')
    }else await route.continue()
  })
  await page.getByLabel('등록 상품',{exact:true}).selectOption('17')
  await page.getByRole('button',{name:'선택 상품 담기'}).click()
  await page.getByRole('button',{name:'담기 결과 다시 확인'}).click()
  await page.getByText('5,000원 →',{exact:true}).waitFor()
  const active=await (await fetch('http://127.0.0.1:4011/api/carts/active')).json()
  assert.equal(active.item_count,2)
  await page.unroute('**/api/carts/*/items')
  results.push('PASS: lost response retry does not duplicate cart item')
  await page.getByLabel('등록 상품',{exact:true}).selectOption('3')
  await page.getByRole('button',{name:'선택 상품 담기'}).click()
  await page.getByText('7,500원 →',{exact:true}).waitFor()
  await page.getByRole('navigation').getByRole('button',{name:'요리 추천'}).click()
  await page.getByRole('heading',{name:'재료 모두 보유',exact:true}).waitFor()
  await page.locator('summary').filter({hasText:'파계란탕'}).click()
  await page.getByRole('heading',{name:'만드는 순서'}).waitFor()
  await page.screenshot({path:path.join(screenshots,'recipes.png'),fullPage:true})
  results.push('PASS: required/optional ingredients and recipe detail rendered from API')
  await page.getByRole('navigation').getByRole('button',{name:/장바구니/}).click()
  await page.getByRole('button',{name:'계란 (10구) 수량 늘리기',exact:true}).click()
  await page.getByText('10,700원',{exact:true}).waitFor()
  await page.getByRole('button',{name:'소금 (500g) 삭제',exact:true}).click()
  await page.getByText('8,900원',{exact:true}).waitFor()
  await page.getByRole('button',{name:'쇼핑 내역 확인'}).click()
  await page.getByRole('status').filter({hasText:'실제 결제 기능은 제공하지 않습니다.'}).waitFor()
  await page.screenshot({path:path.join(screenshots,'cart.png'),fullPage:true})
  results.push('PASS: quantity, delete, server total and shopping summary')
  await page.reload()
  await page.getByRole('button',{name:'쇼핑 시작하기'}).click()
  await page.getByText('8,900원 →',{exact:true}).waitFor()
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true)
  await page.getByRole('button',{name:'카메라 종료',exact:true}).click()
  await page.getByRole('button',{name:'카메라 시작',exact:true}).waitFor()
  assert.equal((await (await fetch('http://127.0.0.1:4011/api/camera/status')).json()).state,'stopped')
  assert.deepEqual(errors,[])
  results.push('PASS: reload persistence, mobile overflow, camera shutdown, no browser runtime errors')
} catch(error){ failure=error; results.push(`FAIL: ${error.stack}`) }
finally {
  if(browser) await browser.close()
  for(const child of processes.reverse()){
    if(child.exitCode===null){
      child.kill()
      await Promise.race([new Promise(resolve=>child.once('exit',resolve)),new Promise(resolve=>setTimeout(resolve,3000))])
    }
  }
  await appendFile(report,`\n# Browser integration run\n\n- Started: ${started}\n- Base commit: ${base} + working tree\n- Command: pnpm --dir frontend test:e2e\n- Runtime: Node ${process.version}, ${process.platform}\n- Browser: ${process.env.BROWSER_CHANNEL || 'Playwright Chromium'}\n- Backend: isolated temporary SQLite, DEMO_MODE=true\n- Result: ${failure?'FAIL':'PASS'}\n- Real camera / Roboflow: NOT RUN (demo test)\n\n${results.map(r=>'- '+r).join('\n')}\n`,'utf8')
  console.log(results.join('\n'))
  console.log(`Report: ${report}`)
}
if(failure) process.exitCode=1
