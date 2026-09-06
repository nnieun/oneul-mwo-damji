import { useState } from "react";

// ── Types ──────────────────────────────────────────────────
type Screen = "splash" | "main";
type Tab = "scan" | "cart" | "recipe";

interface CartItem {
  id: number;
  name: string;
  price: number;
  qty: number;
  emoji: string;
  ingredients: string[];
}

interface RecognizedCandidate {
  id: number;
  name: string;
  confidence: number;
  price: number;
  emoji: string;
  ingredients: string[];
}

interface Recipe {
  id: number;
  name: string;
  emoji: string;
  matched: string[];
  missing: string[];
  time: string;
}

// ── Mock Data ──────────────────────────────────────────────
const INITIAL_CANDIDATES: RecognizedCandidate[] = [
  { id: 1, name: "계란 (10구)", confidence: 96, price: 3200, emoji: "🥚", ingredients: ["계란"] },
  { id: 2, name: "두부 (300g)", confidence: 91, price: 1800, emoji: "🫘", ingredients: ["두부"] },
  { id: 3, name: "대파 (1단)", confidence: 87, price: 2500, emoji: "🌱", ingredients: ["대파"] },
];

const ALL_RECIPES: Recipe[] = [
  { id: 1, name: "계란볶음밥", emoji: "🍳", matched: ["계란", "대파"], missing: ["밥", "간장"], time: "10분" },
  { id: 2, name: "순두부찌개", emoji: "🥘", matched: ["두부", "계란"], missing: ["고춧가루", "멸치육수", "애호박"], time: "20분" },
  { id: 3, name: "파계란탕", emoji: "🍲", matched: ["계란", "대파"], missing: ["소금", "참기름"], time: "8분" },
  { id: 4, name: "두부조림", emoji: "🫕", matched: ["두부", "대파"], missing: ["간장", "고추", "참기름"], time: "15분" },
  { id: 5, name: "된장찌개", emoji: "🫙", matched: ["두부", "대파"], missing: ["된장", "감자", "애호박"], time: "25분" },
];

// ── Splash Screen ─────────────────────────────────────────
function SplashScreen({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 flex flex-col items-center justify-center px-6 gap-8">
        {/* Logo area */}
        <div className="flex flex-col items-center gap-4">
          <div className="w-20 h-20 rounded-3xl bg-[#3182F6] flex items-center justify-center shadow-lg">
            <span className="text-4xl">🛒</span>
          </div>
          <div className="text-center">
            <h1 className="text-[28px] font-black text-[#191F28] tracking-tight">오늘 뭐 담지</h1>
            <p className="text-[15px] text-[#6B7684] mt-1 font-medium">AI가 인식하는 스마트 카트</p>

          </div>
        </div>

        {/* Feature cards */}
        <div className="w-full flex flex-col gap-3">
          {[
            { icon: "📸", title: "AI 상품 인식", desc: "카메라로 상품을 보여주면 자동으로 인식해요" },
            { icon: "💰", title: "실시간 금액 확인", desc: "담는 순간 예상 구매금액을 바로 확인해요" },
            { icon: "🍽️", title: "요리 추천", desc: "담은 재료로 만들 수 있는 요리를 제안해요" },
          ].map((f) => (
            <div key={f.title} className="flex items-center gap-4 bg-[#F2F4F6] rounded-2xl px-4 py-3">
              <span className="text-2xl">{f.icon}</span>
              <div>
                <p className="text-[14px] font-bold text-[#191F28]">{f.title}</p>
                <p className="text-[12px] text-[#6B7684] mt-0.5">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="px-5 pb-10 pt-4">
        <button
          onClick={onStart}
          className="w-full h-[54px] bg-[#3182F6] text-white rounded-2xl font-bold text-[17px] active:scale-[0.98] transition-transform"
        >
          쇼핑 시작하기
        </button>
        <p className="text-center text-[12px] text-[#8B95A1] mt-3">
          카메라 권한이 필요해요 · 시연용 프로토타입
        </p>
      </div>
    </div>
  );
}

// ── Scan Tab ──────────────────────────────────────────────
function ScanTab({
  candidates,
  onAdd,
  onDismiss,
}: {
  candidates: RecognizedCandidate[];
  onAdd: (c: RecognizedCandidate) => void;
  onDismiss: (id: number) => void;
}) {
  const [scanning, setScanning] = useState(false);
  const [scanned, setScanned] = useState(false);

  const handleScan = () => {
    setScanning(true);
    setScanned(false);
    setTimeout(() => {
      setScanning(false);
      setScanned(true);
    }, 2000);
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto bg-[#F2F4F6]">
      {/* Camera area */}
      <div className="mx-4 mt-4 rounded-3xl overflow-hidden relative bg-[#191F28] aspect-[4/3]">
        <img
          src="https://images.unsplash.com/photo-1588964895597-cfccd6e2dbf9?w=600&h=450&fit=crop&auto=format"
          alt="카트 카메라 영상"
          className="w-full h-full object-cover opacity-80"
        />
        {/* Overlay grid */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-40 h-40 border-2 border-white/60 rounded-2xl relative">
            <span className="absolute -top-0.5 -left-0.5 w-5 h-5 border-t-2 border-l-2 border-[#3182F6] rounded-tl-lg" />
            <span className="absolute -top-0.5 -right-0.5 w-5 h-5 border-t-2 border-r-2 border-[#3182F6] rounded-tr-lg" />
            <span className="absolute -bottom-0.5 -left-0.5 w-5 h-5 border-b-2 border-l-2 border-[#3182F6] rounded-bl-lg" />
            <span className="absolute -bottom-0.5 -right-0.5 w-5 h-5 border-b-2 border-r-2 border-[#3182F6] rounded-br-lg" />
          </div>
        </div>
        {/* Status badge */}
        <div className="absolute top-3 left-3">
          <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-bold ${scanning ? "bg-[#FF8B00] text-white" : "bg-[#00B252] text-white"}`}>
            <span className={`w-1.5 h-1.5 rounded-full bg-white ${scanning ? "animate-pulse" : ""}`} />
            {scanning ? "인식 중..." : "카메라 활성"}
          </span>
        </div>
        {/* Scan button */}
        <button
          onClick={handleScan}
          className="absolute bottom-3 right-3 h-9 px-4 bg-white/90 backdrop-blur-sm rounded-xl text-[13px] font-bold text-[#3182F6] active:scale-95 transition-transform"
        >
          상품 스캔
        </button>
      </div>

      {/* Candidates */}
      <div className="px-4 mt-4 mb-2">
        <div className="flex items-center justify-between">
          <h2 className="text-[16px] font-bold text-[#191F28]">인식 후보</h2>
          {candidates.length > 0 && (
            <span className="text-[13px] text-[#6B7684] font-medium">{candidates.length}개 대기 중</span>
          )}
        </div>
        <p className="text-[12px] text-[#8B95A1] mt-0.5">확인 후 장바구니에 담거나 제외하세요</p>
      </div>

      {candidates.length === 0 ? (
        <div className="mx-4 bg-white rounded-3xl p-8 flex flex-col items-center gap-3">
          <span className="text-4xl">🔍</span>
          <p className="text-[15px] font-bold text-[#191F28]">인식된 상품이 없어요</p>
          <p className="text-[13px] text-[#8B95A1] text-center">상품을 카메라 앞에 보여주고<br />스캔 버튼을 눌러보세요</p>
        </div>
      ) : (
        <div className="px-4 flex flex-col gap-3 pb-6">
          {candidates.map((c) => (
            <CandidateCard key={c.id} candidate={c} onAdd={onAdd} onDismiss={onDismiss} />
          ))}
        </div>
      )}

      {/* Demo notice */}
      {scanned && candidates.length > 0 && (
        <div className="mx-4 mb-4 bg-[#EEF4FF] rounded-2xl px-4 py-3 flex items-start gap-3">
          <span className="text-lg mt-0.5">✨</span>
          <div>
            <p className="text-[13px] font-bold text-[#3182F6]">3개 상품을 인식했어요</p>
            <p className="text-[12px] text-[#6B7684] mt-0.5">신뢰도가 낮은 항목은 직접 확인해 주세요</p>
          </div>
        </div>
      )}
    </div>
  );
}

function CandidateCard({
  candidate,
  onAdd,
  onDismiss,
}: {
  candidate: RecognizedCandidate;
  onAdd: (c: RecognizedCandidate) => void;
  onDismiss: (id: number) => void;
}) {
  const confColor =
    candidate.confidence >= 90 ? "#00B252" : candidate.confidence >= 75 ? "#FF8B00" : "#F04452";

  return (
    <div className="bg-white rounded-3xl p-4 flex items-center gap-3 shadow-sm">
      <div className="w-12 h-12 rounded-2xl bg-[#F2F4F6] flex items-center justify-center text-2xl flex-shrink-0">
        {candidate.emoji}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[15px] font-bold text-[#191F28] truncate">{candidate.name}</p>
        <p className="text-[14px] font-medium text-[#6B7684] mt-0.5">{candidate.price.toLocaleString()}원</p>
        <div className="flex items-center gap-1 mt-1">
          <div className="h-1.5 w-20 bg-[#F2F4F6] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{ width: `${candidate.confidence}%`, backgroundColor: confColor }}
            />
          </div>
          <span className="text-[11px] font-bold" style={{ color: confColor }}>
            {candidate.confidence}%
          </span>
        </div>
      </div>
      <div className="flex flex-col gap-2 flex-shrink-0">
        <button
          onClick={() => onAdd(candidate)}
          className="h-8 px-3 bg-[#3182F6] text-white rounded-xl text-[13px] font-bold active:scale-95 transition-transform"
        >
          담기
        </button>
        <button
          onClick={() => onDismiss(candidate.id)}
          className="h-8 px-3 bg-[#F2F4F6] text-[#6B7684] rounded-xl text-[13px] font-bold active:scale-95 transition-transform"
        >
          제외
        </button>
      </div>
    </div>
  );
}

// ── Cart Tab ──────────────────────────────────────────────
function CartTab({
  items,
  onQtyChange,
  onRemove,
}: {
  items: CartItem[];
  onQtyChange: (id: number, delta: number) => void;
  onRemove: (id: number) => void;
}) {
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);

  return (
    <div className="flex flex-col h-full bg-[#F2F4F6]">
      <div className="flex-1 overflow-y-auto">
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <span className="text-6xl">🛒</span>
            <div className="text-center">
              <p className="text-[17px] font-bold text-[#191F28]">장바구니가 비어있어요</p>
              <p className="text-[14px] text-[#8B95A1] mt-1">스캔 탭에서 상품을 담아보세요</p>
            </div>
          </div>
        ) : (
          <>
            {/* Header summary */}
            <div className="mx-4 mt-4 bg-[#3182F6] rounded-3xl px-5 py-4">
              <p className="text-[13px] text-blue-200 font-medium">예상 구매금액 (시연용)</p>
              <p className="text-[32px] font-black text-white mt-1">{total.toLocaleString()}<span className="text-[20px] font-bold ml-1">원</span></p>
              <p className="text-[12px] text-blue-200 mt-1">총 {items.reduce((s, i) => s + i.qty, 0)}개 상품 · 실제 결제금액과 다를 수 있어요</p>
            </div>

            {/* Item list */}
            <div className="px-4 mt-4 mb-2">
              <h2 className="text-[16px] font-bold text-[#191F28]">담은 상품</h2>
            </div>
            <div className="px-4 flex flex-col gap-2 pb-4">
              {items.map((item) => (
                <CartItemRow key={item.id} item={item} onQtyChange={onQtyChange} onRemove={onRemove} />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Checkout bar */}
      {items.length > 0 && (
        <div className="px-4 pb-8 pt-3 bg-white border-t border-[#E5E8EB]">
          <button className="w-full h-[54px] bg-[#3182F6] text-white rounded-2xl font-bold text-[17px] active:scale-[0.98] transition-transform">
            결제하기 · {total.toLocaleString()}원
          </button>
        </div>
      )}
    </div>
  );
}

function CartItemRow({
  item,
  onQtyChange,
  onRemove,
}: {
  item: CartItem;
  onQtyChange: (id: number, delta: number) => void;
  onRemove: (id: number) => void;
}) {
  return (
    <div className="bg-white rounded-3xl px-4 py-3 flex items-center gap-3 shadow-sm">
      <div className="w-11 h-11 rounded-xl bg-[#F2F4F6] flex items-center justify-center text-xl flex-shrink-0">
        {item.emoji}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[14px] font-bold text-[#191F28] truncate">{item.name}</p>
        <p className="text-[13px] text-[#6B7684] mt-0.5">{item.price.toLocaleString()}원</p>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        <button
          onClick={() => item.qty === 1 ? onRemove(item.id) : onQtyChange(item.id, -1)}
          className="w-7 h-7 rounded-full bg-[#F2F4F6] flex items-center justify-center text-[16px] font-bold text-[#6B7684] active:scale-90 transition-transform"
        >
          {item.qty === 1 ? "×" : "−"}
        </button>
        <span className="text-[15px] font-bold text-[#191F28] w-5 text-center">{item.qty}</span>
        <button
          onClick={() => onQtyChange(item.id, 1)}
          className="w-7 h-7 rounded-full bg-[#3182F6] flex items-center justify-center text-[16px] font-bold text-white active:scale-90 transition-transform"
        >
          +
        </button>
      </div>
      <div className="flex-shrink-0 text-right">
        <p className="text-[14px] font-bold text-[#191F28]">{(item.price * item.qty).toLocaleString()}</p>
        <p className="text-[11px] text-[#8B95A1]">원</p>
      </div>
    </div>
  );
}

// ── Recipe Tab ────────────────────────────────────────────
function RecipeTab({ cartItems }: { cartItems: CartItem[] }) {
  const [expanded, setExpanded] = useState<number | null>(null);
  const allIngredients = Array.from(new Set(cartItems.flatMap((i) => i.ingredients)));

  const recipes = ALL_RECIPES.map((r) => ({
    ...r,
    matchCount: r.matched.filter((m) => allIngredients.includes(m)).length,
    totalNeeded: r.matched.length,
  })).sort((a, b) => b.matchCount - a.matchCount);

  const canMake = recipes.filter((r) => r.missing.length <= 1);
  const canExtend = recipes.filter((r) => r.missing.length > 1);

  return (
    <div className="flex flex-col h-full overflow-y-auto bg-[#F2F4F6] pb-6">
      {cartItems.length === 0 ? (
        <div className="flex flex-col items-center justify-center flex-1 gap-4 px-8 text-center mt-20">
          <span className="text-5xl">🍽️</span>
          <p className="text-[17px] font-bold text-[#191F28]">재료를 담으면 요리를 추천해드려요</p>
          <p className="text-[14px] text-[#8B95A1]">스캔 탭에서 식재료를 장바구니에 담아주세요</p>
        </div>
      ) : (
        <>
          {/* Ingredient chips */}
          <div className="px-4 mt-4">
            <p className="text-[13px] text-[#6B7684] font-medium mb-2">보유 재료</p>
            <div className="flex flex-wrap gap-2">
              {allIngredients.map((ing) => (
                <span key={ing} className="px-3 py-1 bg-[#EEF4FF] text-[#3182F6] text-[13px] font-bold rounded-full">
                  {ing}
                </span>
              ))}
            </div>
          </div>

          {/* Can make now */}
          {canMake.length > 0 && (
            <div className="px-4 mt-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2 h-2 rounded-full bg-[#00B252]" />
                <h2 className="text-[15px] font-bold text-[#191F28]">지금 바로 만들 수 있어요</h2>
              </div>
              <div className="flex flex-col gap-2">
                {canMake.map((r) => (
                  <RecipeCard key={r.id} recipe={r} expanded={expanded === r.id} onToggle={() => setExpanded(expanded === r.id ? null : r.id)} />
                ))}
              </div>
            </div>
          )}

          {/* Need more */}
          {canExtend.length > 0 && (
            <div className="px-4 mt-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2 h-2 rounded-full bg-[#FF8B00]" />
                <h2 className="text-[15px] font-bold text-[#191F28]">재료를 조금 더 사면 돼요</h2>
              </div>
              <div className="flex flex-col gap-2">
                {canExtend.map((r) => (
                  <RecipeCard key={r.id} recipe={r} expanded={expanded === r.id} onToggle={() => setExpanded(expanded === r.id ? null : r.id)} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function RecipeCard({
  recipe,
  expanded,
  onToggle,
}: {
  recipe: Recipe & { matchCount: number; totalNeeded: number };
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="bg-white rounded-3xl overflow-hidden shadow-sm">
      <button onClick={onToggle} className="w-full px-4 py-3 flex items-center gap-3 text-left">
        <div className="w-11 h-11 rounded-xl bg-[#F2F4F6] flex items-center justify-center text-xl flex-shrink-0">
          {recipe.emoji}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[15px] font-bold text-[#191F28]">{recipe.name}</p>
          <p className="text-[12px] text-[#8B95A1] mt-0.5">⏱ {recipe.time} · 보유 재료 {recipe.matchCount}/{recipe.matched.length + recipe.missing.length}개</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {recipe.missing.length === 0 && (
            <span className="px-2 py-0.5 bg-[#E8F9EE] text-[#00B252] text-[11px] font-bold rounded-full">바로 가능</span>
          )}
          <span className="text-[#8B95A1] text-[18px]">{expanded ? "∧" : "∨"}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-[#F2F4F6]">
          <div className="mt-3 flex flex-col gap-2">
            <div>
              <p className="text-[12px] font-bold text-[#6B7684] mb-1.5">✅ 이미 있는 재료</p>
              <div className="flex flex-wrap gap-1.5">
                {recipe.matched.map((m) => (
                  <span key={m} className="px-2.5 py-1 bg-[#E8F9EE] text-[#00B252] text-[12px] font-bold rounded-xl">{m}</span>
                ))}
              </div>
            </div>
            {recipe.missing.length > 0 && (
              <div className="mt-1">
                <p className="text-[12px] font-bold text-[#6B7684] mb-1.5">🛒 추가로 필요한 재료</p>
                <div className="flex flex-wrap gap-1.5">
                  {recipe.missing.map((m) => (
                    <span key={m} className="px-2.5 py-1 bg-[#FFF4E5] text-[#FF8B00] text-[12px] font-bold rounded-xl">{m}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Bottom Nav ────────────────────────────────────────────
function BottomNav({ tab, onTab, cartCount }: { tab: Tab; onTab: (t: Tab) => void; cartCount: number }) {
  const tabs: { key: Tab; icon: string; label: string }[] = [
    { key: "scan", icon: "📸", label: "스캔" },
    { key: "cart", icon: "🛒", label: "장바구니" },
    { key: "recipe", icon: "🍽️", label: "요리 추천" },
  ];

  return (
    <div className="bg-white border-t border-[#E5E8EB] flex">
      {tabs.map((t) => (
        <button
          key={t.key}
          onClick={() => onTab(t.key)}
          className="flex-1 flex flex-col items-center justify-center py-2.5 gap-0.5 relative active:opacity-70 transition-opacity"
        >
          <span className="text-xl">{t.icon}</span>
          <span className={`text-[11px] font-bold ${tab === t.key ? "text-[#3182F6]" : "text-[#8B95A1]"}`}>
            {t.label}
          </span>
          {t.key === "cart" && cartCount > 0 && (
            <span className="absolute top-2 right-1/2 translate-x-4 -translate-y-0.5 w-4 h-4 bg-[#F04452] text-white text-[10px] font-black rounded-full flex items-center justify-center">
              {cartCount}
            </span>
          )}
          {tab === t.key && (
            <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-6 h-0.5 bg-[#3182F6] rounded-full" />
          )}
        </button>
      ))}
    </div>
  );
}

// ── Main Screen ───────────────────────────────────────────
function MainScreen() {
  const [tab, setTab] = useState<Tab>("scan");
  const [candidates, setCandidates] = useState<RecognizedCandidate[]>(INITIAL_CANDIDATES);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  const addToCart = (c: RecognizedCandidate) => {
    setCandidates((prev) => prev.filter((p) => p.id !== c.id));
    setCartItems((prev) => {
      const existing = prev.find((i) => i.id === c.id);
      if (existing) return prev.map((i) => i.id === c.id ? { ...i, qty: i.qty + 1 } : i);
      return [...prev, { id: c.id, name: c.name, price: c.price, qty: 1, emoji: c.emoji, ingredients: c.ingredients }];
    });
  };

  const dismissCandidate = (id: number) => setCandidates((prev) => prev.filter((p) => p.id !== id));

  const changeQty = (id: number, delta: number) => {
    setCartItems((prev) => prev.map((i) => i.id === id ? { ...i, qty: Math.max(0, i.qty + delta) } : i).filter((i) => i.qty > 0));
  };

  const removeItem = (id: number) => setCartItems((prev) => prev.filter((i) => i.id !== id));

  const tabTitles: Record<Tab, string> = {
    scan: "상품 스캔",
    cart: "장바구니",
    recipe: "요리 추천",
  };

  return (
    <div className="flex flex-col h-full bg-[#F2F4F6]">
      {/* Top bar */}
      <div className="bg-white px-5 pt-12 pb-4 flex items-center justify-between border-b border-[#E5E8EB]">
        <div>
          <h1 className="text-[19px] font-black text-[#191F28]">{tabTitles[tab]}</h1>
          {tab === "scan" && <p className="text-[12px] text-[#8B95A1] mt-0.5">AI 상품 인식 활성</p>}
          {tab === "cart" && <p className="text-[12px] text-[#8B95A1] mt-0.5">{cartItems.length > 0 ? `${cartItems.reduce((s, i) => s + i.qty, 0)}개 상품` : "비어있음"}</p>}
          {tab === "recipe" && <p className="text-[12px] text-[#8B95A1] mt-0.5">장바구니 재료 기반 추천</p>}
        </div>
        <div className="w-9 h-9 rounded-full bg-[#F2F4F6] flex items-center justify-center text-lg">🛒</div>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {tab === "scan" && <ScanTab candidates={candidates} onAdd={addToCart} onDismiss={dismissCandidate} />}
        {tab === "cart" && <CartTab items={cartItems} onQtyChange={changeQty} onRemove={removeItem} />}
        {tab === "recipe" && <RecipeTab cartItems={cartItems} />}
      </div>

      {/* Bottom nav */}
      <BottomNav tab={tab} onTab={setTab} cartCount={cartItems.length} />
    </div>
  );
}

// ── App ───────────────────────────────────────────────────
export default function App() {
  const [screen, setScreen] = useState<Screen>("splash");

  return (
    <div className="size-full flex justify-center bg-[#F2F4F6]">
      <div
        className="relative flex flex-col overflow-hidden w-full"
        style={{ maxWidth: "430px", fontFamily: "'Noto Sans KR', sans-serif" }}
      >
        {screen === "splash" && <SplashScreen onStart={() => setScreen("main")} />}
        {screen === "main" && <MainScreen />}
      </div>
    </div>
  );
}
