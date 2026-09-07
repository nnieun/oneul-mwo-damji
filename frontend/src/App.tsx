import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, post, postImage, request, requestKey, type Candidate, type Cart, type Product, type Recipe, type RecognitionConfig, type Recommendations, type Scan } from './api'

type Tab = 'scan' | 'cart' | 'recipe'
type CameraState = { state: 'stopped' | 'starting' | 'running' | 'error'; message: string }
type PendingAdd = { product_id: number; quantity: number; candidate_id?: string; key: string }
const won = (amount: number) => `${amount.toLocaleString('ko-KR')}원`

export default function App() {
  const [started, setStarted] = useState(false)
  const [tab, setTab] = useState<Tab>('scan')
  const [cart, setCart] = useState<Cart | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [config, setConfig] = useState<RecognitionConfig>({ mode: 'live', message: '인식 모드를 확인해 주세요.' })
  const [camera, setCamera] = useState<CameraState>({ state: 'stopped', message: '카메라를 시작해 주세요.' })
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [recommendations, setRecommendations] = useState<Recommendations | null>(null)
  const [recipeError, setRecipeError] = useState('')
  const [recipeLoading, setRecipeLoading] = useState(false)
  const [recipeRefresh, setRecipeRefresh] = useState(0)
  const [busy, setBusy] = useState(false)
  const guard = useRef(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [selected, setSelected] = useState('1')
  const [pendingAdd, setPendingAdd] = useState<PendingAdd | null>(null)
  const blocked = busy || pendingAdd !== null

  const applyCart = useCallback((next: Cart) => {
    setCart(old => !old || old.id !== next.id || next.revision >= old.revision ? next : old)
  }, [])

  async function action(task: () => Promise<void>) {
    if (guard.current) return
    guard.current = true
    setBusy(true)
    setError('')
    try { await task() } catch (e) { setError(e instanceof Error ? e.message : '문제가 발생했습니다.') }
    finally { guard.current = false; setBusy(false) }
  }

  async function initialize() {
    await action(async () => {
      const [catalog, recognitionConfig] = await Promise.all([request<Product[]>('/api/products'), request<RecognitionConfig>('/api/recognition/config')])
      let active: Cart
      try { active = await request<Cart>('/api/carts/active') }
      catch (e) { if (!(e instanceof ApiError) || e.status !== 404) throw e; active = await post<Cart>('/api/carts') }
      setProducts(catalog)
      if (catalog.length) setSelected(String(catalog[0].id))
      setConfig(recognitionConfig)
      applyCart(active)
    })
  }

  useEffect(() => {
    if (!started) return
    void initialize()
    // Initialization runs when entering the shopping screen.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [started])

  useEffect(() => () => { streamRef.current?.getTracks().forEach(t => t.stop()) }, [])

  async function startCamera() {
    if (config.mode === 'demo') { setCamera({ state: 'running', message: '더미 모드입니다. 실제 카메라를 사용하지 않아요.' }); return }
    setCamera({ state: 'starting', message: '카메라 연결 중입니다.' })
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
      streamRef.current = stream
      stream.getVideoTracks()[0]?.addEventListener('ended', () => setCamera({ state: 'error', message: '카메라 연결이 끊겼습니다. 다시 시작해 주세요.' }))
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play() }
      setCamera({ state: 'running', message: '카메라 연결됨' })
    } catch {
      setCamera({ state: 'error', message: '카메라 접근 권한이 필요합니다. 브라우저에서 이 사이트의 카메라 사용을 허용해 주세요.' })
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
    if (videoRef.current) videoRef.current.srcObject = null
    setCamera({ state: 'stopped', message: '카메라가 종료되었습니다.' })
  }

  function captureFrame(): Promise<Blob> {
    const canvas = canvasRef.current
    if (!canvas) return Promise.reject(new Error('캡처를 사용할 수 없습니다.'))
    if (config.mode === 'demo' || !videoRef.current) {
      canvas.width = 320; canvas.height = 240
      const ctx = canvas.getContext('2d')
      if (ctx) { ctx.fillStyle = '#28211a'; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.fillStyle = '#fff'; ctx.font = '16px sans-serif'; ctx.fillText('DEMO', 130, 124) }
    } else {
      const video = videoRef.current
      canvas.width = video.videoWidth || 320
      canvas.height = video.videoHeight || 240
      canvas.getContext('2d')?.drawImage(video, 0, 0, canvas.width, canvas.height)
    }
    return new Promise((resolve, reject) => canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('캡처에 실패했습니다.')), 'image/jpeg', 0.85))
  }

  useEffect(() => {
    if (!cart) return
    let alive = true
    setRecipeLoading(true)
    setRecipeError('')
    setRecommendations(null)
    void request<Recommendations>(`/api/carts/${cart.id}/recommendations`).then(data => {
      if (alive && data.revision >= cart.revision) setRecommendations(data)
    }).catch(e => { if (alive) setRecipeError(e.message) }).finally(() => { if (alive) setRecipeLoading(false) })
    return () => { alive = false }
  }, [cart?.id, cart?.revision, recipeRefresh])

  async function submitAdd(pending: PendingAdd) {
    if (!cart) return
    const { key, ...body } = pending
    try {
      const result = await post<Cart>(`/api/carts/${cart.id}/items`, body, key)
      applyCart(result)
      setCandidates(old => old.filter(c => c.candidate_id !== body.candidate_id))
      setPendingAdd(null)
      setNotice('장바구니에 담았어요.')
      // A replay can return an earlier snapshot; always reconcile with current state.
      applyCart(await request<Cart>(`/api/carts/${cart.id}`))
    } catch (e) {
      if (e instanceof ApiError && e.status !== 0) setPendingAdd(null)
      throw e
    }
  }

  function add(productId: number, candidateId?: string) {
    if (blocked || !cart) return
    const pending = { product_id: productId, quantity: 1, candidate_id: candidateId, key: requestKey() }
    setPendingAdd(pending)
    void action(() => submitAdd(pending))
  }

  function scan() {
    void action(async () => {
      const frame = await captureFrame()
      const result = await postImage<Scan>('/api/recognition/scan', frame)
      setCandidates(result.candidates)
      setNotice(`${result.mode === 'demo' ? '더미 인식 · ' : ''}${result.message}`)
    })
  }

  const titles = { scan: '상품 스캔', cart: '장바구니', recipe: '요리 추천' }
  if (!started) return <div className="app-shell splash">
    <div className="brand-icon">🛒</div><h1>오늘 뭐 담지</h1><p className="muted">AI가 인식하는 스마트 카트</p>
    <div className="feature-list">{[['📸', '상품 인식', '카메라로 스캔하고 직접 확인해요'], ['💰', '예상 금액 확인', '담은 상품의 금액을 바로 확인해요'], ['🍽️', '요리 추천', '담은 재료로 만들 요리를 찾아요']].map(([icon, title, text]) => <div className="card feature" key={title}><span>{icon}</span><div><strong>{title}</strong><p className="muted">{text}</p></div></div>)}</div>
    <button className="primary full" onClick={() => setStarted(true)}>쇼핑 시작하기</button><small className="muted">접속 기기의 카메라 사용 · 시연용 프로토타입</small>
  </div>

  return <div className="app-shell">
    <header className="app-header"><div><h1>{titles[tab]}</h1><p className="muted">오늘 뭐 담지 · 시연용 스마트 카트</p></div><span className="brand-small">🛒</span></header>
    <main>
      {error && <div className="alert" role="alert"><p>{error}</p>{!cart && <button disabled={busy} onClick={() => void initialize()}>다시 연결</button>}</div>}
      {pendingAdd && !busy && <div className="alert"><p>담기 결과를 확인하지 못했어요. 같은 요청으로 다시 확인하면 중복으로 담기지 않아요.</p><button onClick={() => void action(() => submitAdd(pendingAdd))}>담기 결과 다시 확인</button></div>}
      <p className="notice" role="status" aria-live="polite">{busy ? '처리 중이에요…' : notice}</p>
      {!cart && !error && <div className="empty">쇼핑 데이터를 불러오고 있어요…</div>}
      {cart && <>
        {tab === 'scan' && <>
          <div className="camera-panel">
            <video ref={videoRef} autoPlay playsInline muted aria-label="카트 카메라 실시간 영상" hidden={!(camera.state === 'running' && config.mode === 'live')} />
            {camera.state === 'running' && config.mode === 'demo' && <div className="camera-placeholder"><span>🧪</span><p>더미 모드 · 실제 인식 아님</p></div>}
            {camera.state !== 'running' && <div className="camera-placeholder"><span>📷</span><p>{camera.message}</p></div>}
            <span className={`camera-badge ${camera.state === 'running' ? 'active' : ''}`}>{config.mode === 'demo' ? '더미 모드 · 실제 인식 아님' : '실제 카메라'} · {camera.state === 'running' ? '연결됨' : '연결 대기'}</span>
          </div>
          <canvas ref={canvasRef} hidden />
          <div className="button-row"><button disabled={blocked} onClick={() => void action(async () => { if (camera.state === 'running') stopCamera(); else await startCamera() })}>{camera.state === 'running' ? '카메라 종료' : '카메라 시작'}</button><button className="primary" disabled={blocked || camera.state !== 'running'} onClick={scan}>상품 스캔</button></div>
          <button className="summary compact" onClick={() => setTab('cart')}><span>예상 구매금액 · {cart.item_count}개</span><strong>{won(cart.total)} →</strong></button>
          <div className="section-heading"><h2>인식 후보</h2><span className="muted">{candidates.length}개 대기</span></div><p className="muted">확인 후 담거나 제외하세요. 잘못 인식하면 상품을 바꿀 수 있어요.</p>
          {candidates.length === 0 ? <div className="card empty"><span>🔍</span><p>상품을 스캔하면 후보가 나타나요.</p></div> : candidates.map(candidate => <CandidateCard key={candidate.candidate_id} candidate={candidate} products={products} disabled={blocked} onAdd={id => add(id, candidate.candidate_id)} onDismiss={() => void action(async () => { await post(`/api/recognition/candidates/${candidate.candidate_id}/dismiss`); setCandidates(old => old.filter(c => c.candidate_id !== candidate.candidate_id)) })} />)}
          <div className="card manual"><h2>상품 직접 선택</h2><p className="muted">카메라 없이도 장바구니를 사용할 수 있어요.</p><label htmlFor="manual-product">등록 상품</label><select id="manual-product" value={selected} onChange={e => setSelected(e.target.value)}>{products.map(p => <option key={p.id} value={p.id}>{p.name} · {won(p.price)}</option>)}</select><button className="primary full" disabled={blocked || !products.length} onClick={() => add(Number(selected))}>선택 상품 담기</button></div>
        </>}
        {tab === 'cart' && <>
          <div className="summary"><span>예상 구매금액 (시연용)</span><strong>{won(cart.total)}</strong><span>총 {cart.item_count}개 상품 · 실제 결제금액과 다를 수 있어요</span></div>
          {cart.items.length === 0 ? <div className="empty"><span>🛒</span><h2>장바구니가 비어있어요</h2><p className="muted">스캔 탭에서 상품을 담아주세요.</p><button onClick={() => setTab('scan')}>상품 담으러 가기</button></div> : cart.items.map(item => <div className="card cart-line" key={item.product_id}>
            <div className="line-top"><span className="product-emoji">{item.emoji}</span><div><strong>{item.name}</strong><p className="muted">단가 {won(item.unit_price)}</p></div><strong className="line-total">{won(item.subtotal)}</strong></div>
            <div className="quantity"><button aria-label={`${item.name} 삭제`} disabled={blocked} onClick={() => void action(async () => applyCart(await request<Cart>(`/api/carts/${cart.id}/items/${item.product_id}`, { method: 'DELETE' })))}>삭제</button><div><button aria-label={`${item.name} 수량 줄이기`} disabled={blocked || item.quantity <= 1} onClick={() => void action(async () => applyCart(await request<Cart>(`/api/carts/${cart.id}/items/${item.product_id}`, { method: 'PATCH', body: JSON.stringify({ quantity: item.quantity - 1 }) })))}>−</button><span aria-label="수량">{item.quantity}</span><button aria-label={`${item.name} 수량 늘리기`} disabled={blocked || item.quantity >= 999} onClick={() => void action(async () => applyCart(await request<Cart>(`/api/carts/${cart.id}/items/${item.product_id}`, { method: 'PATCH', body: JSON.stringify({ quantity: item.quantity + 1 }) })))}>+</button></div></div>
          </div>)}
          {cart.items.length > 0 && <button className="primary full" onClick={() => setNotice(`쇼핑 내역: ${cart.item_count}개 상품, 예상 ${won(cart.total)}. 실제 결제 기능은 제공하지 않습니다.`)}>쇼핑 내역 확인</button>}
        </>}
        {tab === 'recipe' && <>
          <h2>담은 재료로 만드는 한 끼</h2><p className="muted">물은 기본 제공해요. 양념은 담은 상품만 보유한 것으로 계산해요.</p>
          {recipeLoading && <p role="status">추천을 불러오는 중이에요…</p>}
          {recipeError && <div className="alert" role="alert"><p>{recipeError}</p><button onClick={() => setRecipeRefresh(n => n + 1)}>추천 다시 불러오기</button></div>}
          {recommendations && <><div className="chips">{recommendations.owned.map(name => <span key={name}>{name}</span>)}</div><p className="muted">{recommendations.note}</p>
            {recommendations.recipes.length === 0 && <div className="card empty"><span>🍽️</span><p>{cart.items.length ? '조건에 맞는 요리가 아직 없어요. 재료를 더 담아보세요.' : '재료를 담으면 요리를 추천해드려요.'}</p><button onClick={() => setTab('scan')}>재료 담으러 가기</button></div>}
            {(['ready', 'almost'] as const).map(category => { const list = recommendations.recipes.filter(r => r.category === category); return list.length > 0 && <section key={category}><h2>{category === 'ready' ? '재료 모두 보유' : '조금 더 담으면 가능'}</h2>{list.map(recipe => <RecipeCard key={recipe.id} recipe={recipe} />)}</section> })}
          </>}
        </>}
      </>}
    </main>
    <nav aria-label="쇼핑 메뉴">{(['scan', 'cart', 'recipe'] as const).map(t => <button key={t} className={tab === t ? 'selected' : ''} aria-current={tab === t ? 'page' : undefined} onClick={() => setTab(t)}><span>{t === 'scan' ? '📸' : t === 'cart' ? '🛒' : '🍽️'}</span>{titles[t]}{t === 'cart' && cart && cart.item_count > 0 && <b>{cart.item_count}</b>}</button>)}</nav>
  </div>
}

function CandidateCard({ candidate, products, disabled, onAdd, onDismiss }: { candidate: Candidate; products: Product[]; disabled: boolean; onAdd: (id: number) => void; onDismiss: () => void }) {
  const [productId, setProductId] = useState(candidate.product.id)
  return <div className="card candidate"><div className="line-top"><span className="product-emoji">{candidate.product.emoji}</span><div><strong>{candidate.product.name}</strong><p className="muted">{won(candidate.product.price)} · 신뢰도 {Math.round(candidate.confidence * 100)}%</p></div></div><label htmlFor={`candidate-${candidate.candidate_id}`}>확인할 상품</label><select id={`candidate-${candidate.candidate_id}`} value={productId} disabled={disabled} onChange={e => setProductId(Number(e.target.value))}>{products.map(p => <option key={p.id} value={p.id}>{p.name} · {won(p.price)}</option>)}</select><div className="button-row"><button disabled={disabled} onClick={onDismiss}>제외</button><button className="primary" disabled={disabled} onClick={() => onAdd(productId)}>확인 후 담기</button></div></div>
}

function RecipeCard({ recipe }: { recipe: Recipe }) {
  return <details className="card recipe"><summary><strong>{recipe.name}</strong><span className="muted">{recipe.cooking_time_minutes}분 · {recipe.servings}인분 · 보유 {recipe.matched.length}/{recipe.matched.length + recipe.missing.length}</span></summary><h3>보유 재료</h3><div className="chips">{recipe.matched.map(i => <span key={i}>{i}</span>)}</div>{recipe.missing.length > 0 && <><h3>추가로 필요한 재료</h3><div className="chips missing">{recipe.missing.map(i => <span key={i}>{i}</span>)}</div></>}<h3>재료와 분량</h3><ul>{recipe.ingredients.map(i => <li key={i.id}>{i.name} {i.amount}{!i.required && ' (선택)'}</li>)}</ul><h3>만드는 순서</h3><ol>{recipe.steps.map((step, i) => <li key={i}>{step}</li>)}</ol><small className="muted">시연용 더미 레시피 · 실제 분량은 직접 확인해 주세요.</small></details>
}
