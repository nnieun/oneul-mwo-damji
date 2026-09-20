import { useEffect, useRef, useState } from 'react'

type Tab = 'scan' | 'cart' | 'recipe'
type Product = { id: number; name: string; price: number; ingredient: string; emoji: string }
type Line = Product & { quantity: number }
type Recipe = { name: string; minutes: number; needs: string[]; steps: string[] }
const raw = [['계란 (1개)',320,'계란','🥚'],['두부 (300g)',1800,'두부','🫘'],['대파 (1단)',2500,'대파','🌱'],['즉석밥 (210g)',1500,'밥','🍚'],['간장 (500ml)',3500,'간장','🧂'],['식용유 (500ml)',4200,'식용유','🫙'],['감자 (600g)',3000,'감자','🥔'],['김치 (500g)',5900,'김치','🥬'],['양파 (1개)',930,'양파','🧅'],['토마토 (500g)',4500,'토마토','🍅'],['소금 (500g)',1800,'소금','🧂'],['돼지고기 (300g)',6900,'돼지고기','🥩'],['새우 (냉동 200g)',7900,'새우','🦐']]
const products: Product[] = raw.map(([name,price,ingredient,emoji], i) => ({ id:i + 1, name:String(name), price:Number(price), ingredient:String(ingredient), emoji:String(emoji) }))
const recipes: Recipe[] = [
  ['계란볶음밥',10,['계란','대파','밥','간장','식용유'],['대파를 썰고 계란을 푼다.','식용유에 대파와 계란을 볶는다.','밥과 간장을 넣고 골고루 볶는다.']],
  ['두부계란국',15,['두부','계란','대파','소금'],['두부와 대파를 썬다.','물에 두부를 넣고 끓인다.','계란과 대파를 넣고 소금으로 간한다.']],
  ['김치볶음밥',12,['김치','밥','식용유'],['김치를 잘게 썬다.','식용유에 김치를 볶고 밥을 넣는다.']],
  ['감자양파볶음',15,['감자','양파','소금','식용유'],['감자와 양파를 채 썬다.','식용유에 볶고 소금으로 간한다.']],
  ['토마토계란볶음',10,['토마토','계란','소금','식용유'],['토마토와 계란을 준비한다.','식용유에 볶고 소금으로 간한다.']],
  ['제육볶음',20,['돼지고기','양파','대파','간장','식용유'],['채소를 썬다.','고기에 양념을 넣고 볶는다.','채소를 넣어 함께 익힌다.']],
  ['새우볶음밥',15,['새우','밥','양파','대파','식용유','간장'],['채소와 새우를 손질한다.','식용유에 볶고 밥과 간장을 넣는다.']]
].map(([name,minutes,needs,steps]) => ({ name:String(name), minutes:Number(minutes), needs:needs as string[], steps:steps as string[] }))
const won = (n:number) => `${n.toLocaleString('ko-KR')}원`

export default function App() {
  const [started,setStarted] = useState(false), [tab,setTab] = useState<Tab>('scan'), [cart,setCart] = useState<Line[]>([]), [candidates,setCandidates] = useState<Product[]>([]), [notice,setNotice] = useState(''), [camera,setCamera] = useState(false)
  const video = useRef<HTMLVideoElement>(null), stream = useRef<MediaStream | null>(null)
  const total=cart.reduce((s,x)=>s+x.price*x.quantity,0), count=cart.reduce((s,x)=>s+x.quantity,0), owned=new Set(cart.map(x=>x.ingredient))
  useEffect(()=>()=>stream.current?.getTracks().forEach(x=>x.stop()),[])
  async function scan(){
    const source=video.current
    if(!source || !source.videoWidth){setNotice('실제 인식을 위해 카메라를 시작하고 상품을 화면에 비춰 주세요.');return}
    const canvas=document.createElement('canvas');canvas.width=source.videoWidth;canvas.height=source.videoHeight
    canvas.getContext('2d')?.drawImage(source,0,0)
    const image=await new Promise<Blob | null>(resolve=>canvas.toBlob(resolve,'image/jpeg',.85))
    if(!image){setNotice('촬영에 실패했어요. 다시 시도해 주세요.');return}
    try{
      setNotice('Roboflow로 상품을 인식하고 있어요…')
      const body=new FormData();body.append('image',image,'frame.jpg')
      const response=await fetch('/api/recognition/scan',{method:'POST',body})
      const data=await response.json()
      if(!response.ok)throw new Error(typeof data?.detail==='string'?data.detail:'인식 요청에 실패했어요.')
      setCandidates((data.candidates??[]).map((item:{product:{id:number;name:string;price:number;ingredients?:string[];emoji:string}})=>({ ...item.product, ingredient:item.product.ingredients?.[0]??item.product.name })))
      setNotice(data.message??'인식 결과를 확인해 주세요.')
    }catch(error){setNotice(error instanceof Error?error.message:'인식 요청에 실패했어요.')}
  }
  async function cameraToggle(){ if(camera){stream.current?.getTracks().forEach(x=>x.stop());stream.current=null;setCamera(false);return}; try {const s=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});stream.current=s;if(video.current){video.current.srcObject=s;await video.current.play()};setCamera(true);setNotice('상품을 카메라에 비춘 뒤 “AI 인식하기”를 눌러 주세요.')} catch {setNotice('카메라 권한을 허용해 주세요.')} }
  function add(product:Product){setCart(old=>{const found=old.find(x=>x.id===product.id);return found?old.map(x=>x.id===product.id?{...x,quantity:x.quantity+1}:x):[...old,{...product,quantity:1}]});setCandidates(old=>old.filter(x=>x.id!==product.id));setNotice('장바구니에 담았어요.')}
  function change(id:number,quantity:number){setCart(old=>quantity<1?old.filter(x=>x.id!==id):old.map(x=>x.id===id?{...x,quantity}:x))}
  const titles={scan:'상품 스캔',cart:'장바구니',recipe:'요리 추천'}
  if(!started)return <div className="app-shell splash"><div className="brand-icon">🛒</div><h1>오늘 뭐 담지</h1><p className="muted">AI가 인식하는 스마트 카트</p><div className="feature-list">{[['📸','상품 인식','카메라로 스캔하고 직접 확인해요'],['💰','예상 금액 확인','담은 상품의 금액을 바로 확인해요'],['🍽️','요리 추천','담은 재료로 만들 요리를 찾아요']].map(([icon,title,text])=><div className="card feature" key={title}><span>{icon}</span><div><strong>{title}</strong><p className="muted">{text}</p></div></div>)}</div><button className="primary full" onClick={()=>setStarted(true)}>쇼핑 시작하기</button><small className="muted">로그인 없는 체험용 데모 · 새로고침 시 장바구니가 초기화됩니다</small></div>
  const suggested=recipes.filter(r=>r.needs.some(x=>owned.has(x))&&r.needs.filter(x=>!owned.has(x)).length<=2)
  return <div className="app-shell"><header className="app-header"><div><h1>{titles[tab]}</h1><p className="muted">오늘 뭐 담지 · 시연용 스마트 카트</p></div><span className="brand-small">🛒</span></header><main><p className="notice">{notice}</p>{tab==='scan'&&<><div className="camera-panel"><video ref={video} autoPlay playsInline muted hidden={!camera}/><div className="camera-placeholder" hidden={camera}><span>📷</span><p>카메라를 시작해 주세요.</p></div><span className={`camera-badge ${camera?'active':''}`}>실제 Roboflow 인식 · {camera?'카메라 연결됨':'연결 대기'}</span></div><div className="button-row"><button className="primary full" onClick={()=>void cameraToggle()}>{camera?'카메라 종료':'카메라 시작'}</button><button disabled={!camera} onClick={()=>void scan()}>AI 인식하기</button></div><button className="summary compact" onClick={()=>setTab('cart')}><span>예상 구매금액 · {count}개</span><strong>{won(total)} →</strong></button><div className="section-heading"><h2>인식 후보</h2><span className="muted">{candidates.length}개 대기</span></div>{candidates.length===0?<div className="card empty"><span>🔍</span><p>카메라를 시작하고 AI 인식하기를 눌러주세요.</p></div>:candidates.map(p=><Candidate key={p.id} product={p} add={add} dismiss={()=>setCandidates(x=>x.filter(y=>y.id!==p.id))}/>)}</>}{tab==='cart'&&<><div className="summary"><span>예상 구매금액 (시연용)</span><strong>{won(total)}</strong><span>총 {count}개 상품 · 실제 결제금액과 다를 수 있어요</span></div>{cart.length===0?<div className="empty"><span>🛒</span><h2>장바구니가 비어있어요</h2><button onClick={()=>setTab('scan')}>상품 담으러 가기</button></div>:cart.map(x=><div className="card cart-line" key={x.id}><div className="line-top"><span className="product-emoji">{x.emoji}</span><div><strong>{x.name}</strong><p className="muted">단가 {won(x.price)}</p></div><strong className="line-total">{won(x.price*x.quantity)}</strong></div><div className="quantity"><button onClick={()=>change(x.id,0)}>삭제</button><div><button onClick={()=>change(x.id,x.quantity-1)}>−</button><span>{x.quantity}</span><button onClick={()=>change(x.id,x.quantity+1)}>+</button></div></div></div>)}</>}{tab==='recipe'&&<><h2>담은 재료로 만드는 한 끼</h2>{suggested.length===0?<div className="empty">재료를 담으면 요리를 추천해드려요.</div>:suggested.map(r=><RecipeCard key={r.name} recipe={r} owned={owned}/>)}</>}</main><nav>{(['scan','cart','recipe'] as Tab[]).map(x=><button key={x} className={tab===x?'selected':''} onClick={()=>setTab(x)}><span>{x==='scan'?'📸':x==='cart'?'🛒':'🍽️'}</span>{titles[x]}{x==='cart'&&count>0&&<b>{count}</b>}</button>)}</nav></div>
}
function Candidate({product,add,dismiss}:{product:Product;add:(p:Product)=>void;dismiss:()=>void}){const [id,setId]=useState(product.id);const selected=products.find(x=>x.id===id)??product;return <div className="card candidate"><div className="line-top"><span className="product-emoji">{product.emoji}</span><div><strong>{product.name}</strong><p className="muted">{won(product.price)} · 신뢰도 90%</p></div></div><label>확인할 상품</label><select value={id} onChange={e=>setId(Number(e.target.value))}>{products.map(x=><option key={x.id} value={x.id}>{x.name} · {won(x.price)}</option>)}</select><div className="button-row"><button onClick={dismiss}>제외</button><button className="primary" onClick={()=>add(selected)}>확인 후 담기</button></div></div>}
function RecipeCard({recipe,owned}:{recipe:Recipe;owned:Set<string>}){const yes=recipe.needs.filter(x=>owned.has(x)),no=recipe.needs.filter(x=>!owned.has(x));return <details className="card recipe"><summary><strong>{recipe.name}</strong><span className="muted">{recipe.minutes}분 · 보유 {yes.length}/{recipe.needs.length}</span></summary><h3>보유 재료</h3><div className="chips">{yes.map(x=><span key={x}>{x}</span>)}</div>{no.length>0&&<><h3>추가로 필요한 재료</h3><div className="chips missing">{no.map(x=><span key={x}>{x}</span>)}</div></>}<h3>만드는 순서</h3><ol>{recipe.steps.map(x=><li key={x}>{x}</li>)}</ol></details>}
