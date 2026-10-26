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

export interface AskResponse {
  route?: string | null
  analysis?: Record<string, unknown> | null
  plan?: Record<string, unknown> | null
  structured_result?: Record<string, unknown> | null
  answer?: string | null
  refused?: boolean
  trace_id?: string | null
  sources: SourceResponse[]
  external_documents?: Record<string, unknown>[]
  processing_tasks?: Record<string, unknown>[]
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

export function askQuestion(pergunta: string, topK: number) {
  return request<AskResponse>('/query/ask', {
    method: 'POST',
    body: JSON.stringify({ pergunta, top_k: topK }),
  })
}
