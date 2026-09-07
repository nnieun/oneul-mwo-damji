export interface Product { id: number; name: string; price: number; ingredients: string[]; emoji: string }
export interface CartLine { product_id: number; name: string; emoji: string; ingredients: string[]; quantity: number; unit_price: number; subtotal: number }
export interface Cart { id: string; status: string; revision: number; items: CartLine[]; total: number; item_count: number }
export interface Candidate { candidate_id: string; product: Product; confidence: number; status: string; expires_at: number }
export interface Scan { scan_id: string; candidates: Candidate[]; mode: string; message: string }
export interface RecognitionConfig { mode: string; message: string }
export interface Recipe { id: number; name: string; cooking_time_minutes: number; servings: number; steps: string[]; ingredients: { id: number; name: string; amount: string; required: boolean }[]; matched: string[]; missing: string[]; optional_missing: string[]; category: 'ready' | 'almost' }
export interface Recommendations { cart_id: string; revision: number; owned: string[]; recipes: Recipe[]; note: string }

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message) }
}
export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 20000)
  try {
    const response = await fetch(`${API_BASE}${path}`, { ...options, signal: controller.signal, headers: { 'Content-Type': 'application/json', ...options.headers } })
    const body = await response.json().catch(() => null)
    if (!response.ok) {
      throw new ApiError(typeof body?.detail === 'string' ? body.detail : `요청을 처리하지 못했습니다 (${response.status}).`, response.status)
    }
    if (body === null) throw new ApiError('서버 응답을 읽지 못했습니다. 연결 설정을 확인해 주세요.', 0)
    return body as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError('서버 연결이 끊겼거나 응답 시간이 초과되었습니다. 다시 시도해 주세요.', 0)
  } finally { clearTimeout(timeout) }
}
export const post = <T,>(path: string, body?: unknown, key?: string) => request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body), headers: key ? { 'Idempotency-Key': key } : {} })
export async function postImage<T>(path: string, image: Blob): Promise<T> {
  const form = new FormData()
  form.append('image', image, 'frame.jpg')
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 20000)
  try {
    const response = await fetch(`${API_BASE}${path}`, { method: 'POST', body: form, signal: controller.signal })
    const body = await response.json().catch(() => null)
    if (!response.ok) throw new ApiError(typeof body?.detail === 'string' ? body.detail : `요청을 처리하지 못했습니다 (${response.status}).`, response.status)
    if (body === null) throw new ApiError('서버 응답을 읽지 못했습니다. 연결 설정을 확인해 주세요.', 0)
    return body as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError('서버 연결이 끊겼거나 응답 시간이 초과되었습니다. 다시 시도해 주세요.', 0)
  } finally { clearTimeout(timeout) }
}
export const requestKey = () => globalThis.crypto.randomUUID?.() || Array.from(globalThis.crypto.getRandomValues(new Uint8Array(16)), n => n.toString(16).padStart(2, '0')).join('')
