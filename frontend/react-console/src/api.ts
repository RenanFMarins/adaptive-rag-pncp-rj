const API_BASE = import.meta.env.VITE_API_URL ?? ''

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

export interface UserResponse {
  id: number
  username: string
  email: string
  role: 'user' | 'admin'
  is_active: boolean
}

export interface SourceResponse {
  rank: number
  chunk_id: string
  relevance_score: number
  metadata: Record<string, unknown>
}

export type CoverageState = 'covered' | 'partial' | 'unavailable' | 'unknown'

export interface CoverageResource {
  resource?: string
  dependency?: string
  available_records?: number
  state?: CoverageState
  [key: string]: unknown
}

export interface DataCoverage {
  state: CoverageState
  resources: CoverageResource[]
  messages: string[]
}

export interface StructuredWarning {
  code: string
  message: string
  affected_rows: number
}

export interface StructuredResult {
  entity: string
  columns: string[]
  rows: Record<string, unknown>[]
  row_count: number
  limit_applied: number
  warnings: StructuredWarning[]
  coverage: DataCoverage
}

export interface AskResponse {
  route?: string | null
  analysis?: Record<string, unknown> | null
  plan?: Record<string, unknown> | null
  structured_result?: StructuredResult | null
  answer?: string | null
  refused?: boolean
  trace_id?: string | null
  history_id?: number | null
  sources: SourceResponse[]
  external_documents?: Record<string, unknown>[]
  processing_tasks?: Record<string, unknown>[]
}

export interface FeedbackResponse {
  id: number
  history_id: number
  rating: -1 | 1
  reason_code: 'helpful' | 'incorrect' | 'incomplete' | 'outdated' | 'other' | null
  created_at: string
  updated_at: string
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = sessionStorage.getItem('rag-token')
  const headers = new Headers(options.headers)
  headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const contentType = response.headers.get('content-type') ?? ''
  const body = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const detail = typeof body === 'object' && body && 'detail' in body ? String(body.detail) : String(body)
    throw new Error(detail || `Erro HTTP ${response.status}`)
  }
  return body as T
}

export function login(username: string, password: string) {
  return request<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function register(username: string, email: string, password: string) {
  return request<UserResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  })
}

export function getCurrentUser() {
  return request<UserResponse>('/auth/me')
}

export function askQuestion(
  pergunta: string,
  topK: number,
  contexto?: Record<string, unknown>,
) {
  return request<AskResponse>('/query/ask', {
    method: 'POST',
    body: JSON.stringify({
      pergunta,
      top_k: topK,
      ...(contexto ? { contexto } : {}),
    }),
  })
}

export function submitFeedback(historyId: number, rating: -1 | 1) {
  return request<FeedbackResponse>('/feedback', {
    method: 'POST',
    body: JSON.stringify({
      history_id: historyId,
      rating,
      reason_code: rating === 1 ? 'helpful' : 'incorrect',
    }),
  })
}
