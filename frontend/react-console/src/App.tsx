import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Building2, Database, LogOut, MessageSquarePlus, Send, ShieldCheck } from 'lucide-react'
import { askQuestion, getCurrentUser, login, register, type AskResponse, type UserResponse } from './api'
import { ResponseEvidence } from './ResponseEvidence'

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  response?: AskResponse
  topK?: number
}

const suggestions = [
  'Quantas contratações existem por modalidade em 2026?',
  'Quais contratos da Fundação Oswaldo Cruz foram publicados em 2026?',
  'Quais documentos são exigidos na habilitação segundo a Lei 14.133?',
]

function App() {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(5)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [conversationContext, setConversationContext] = useState<Record<string, unknown> | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!sessionStorage.getItem('rag-token')) return
    getCurrentUser().then(setUser).catch(() => sessionStorage.removeItem('rag-token'))
  }, [])

  async function handleAuth(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      if (authMode === 'register') {
        await register(username, email, password)
        setAuthMode('login')
        setEmail('')
        setError('Conta criada. Faça login para continuar.')
      } else {
        const result = await login(username, password)
        sessionStorage.setItem('rag-token', result.access_token)
        setUser(await getCurrentUser())
        setPassword('')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha na autenticação')
    } finally {
      setBusy(false)
    }
  }

  async function submitQuestion(value = question) {
    const text = value.trim()
    if (!text || busy) return
    setQuestion('')
    setError('')
    setBusy(true)
    setMessages((current) => [...current, { id: Date.now(), role: 'user', content: text }])
    try {
      const response = await askQuestion(text, topK, conversationContext ?? undefined)
      if (response.analysis && !response.refused) {
        setConversationContext(response.analysis)
      }
      setMessages((current) => [...current, { id: Date.now() + 1, role: 'assistant', content: response.answer ?? 'Consulta concluída.', response, topK }])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao consultar a API')
      setMessages((current) => [...current, { id: Date.now() + 1, role: 'assistant', content: 'Não foi possível concluir a consulta.' }])
    } finally {
      setBusy(false)
    }
  }

  function logout() {
    sessionStorage.removeItem('rag-token')
    setUser(null)
    setMessages([])
    setConversationContext(null)
  }

  function startNewConversation() {
    setMessages([])
    setConversationContext(null)
    setQuestion('')
    setError('')
  }

  if (!user) {
    return (
      <main className="auth-shell">
        <section className="auth-brand" aria-label="Sobre o sistema">
          <div className="brand-mark"><Building2 size={22} /></div>
          <p className="eyebrow">PNCP · Rio de Janeiro</p>
          <h1>Consulta inteligente a contratações públicas</h1>
          <p className="brand-copy">Combine dados estruturados, documentos normativos e resultados homologados em uma única conversa.</p>
          <div className="brand-data"><span><Database size={17} /> Base normalizada</span><span><ShieldCheck size={17} /> Resposta fundamentada</span></div>
        </section>
        <section className="auth-panel">
          <div className="auth-card">
            <div className="auth-tabs">
              <button className={authMode === 'login' ? 'active' : ''} onClick={() => { setAuthMode('login'); setError('') }}>Entrar</button>
              <button className={authMode === 'register' ? 'active' : ''} onClick={() => { setAuthMode('register'); setError('') }}>Criar conta</button>
            </div>
            <form onSubmit={handleAuth}>
              <label>Usuário<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" required /></label>
              {authMode === 'register' && <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required /></label>}
              <label>Senha<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={authMode === 'login' ? 'current-password' : 'new-password'} minLength={authMode === 'login' ? 1 : 12} required /></label>
              {error && <p className={error.includes('Conta criada') ? 'notice success' : 'notice'}>{error}</p>}
              <button className="primary-button" disabled={busy} type="submit">{busy ? 'Aguarde...' : authMode === 'login' ? 'Entrar no sistema' : 'Criar conta'}</button>
            </form>
          </div>
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="side-brand"><div className="brand-mark small"><Building2 size={18} /></div><span>PNCP RAG</span></div>
          <button className="new-chat" onClick={startNewConversation} disabled={busy}><MessageSquarePlus size={17} /> Nova consulta</button>
          <nav aria-label="Fontes disponíveis">
            <p>Fontes</p>
            <span><Database size={16} /> Dados estruturados</span>
            <span><ShieldCheck size={16} /> Documentos normativos</span>
          </nav>
        </div>
        <div className="user-row"><div className="avatar">{user.username.slice(0, 2).toUpperCase()}</div><div><strong>{user.username}</strong><small>{user.role === 'admin' ? 'Administrador' : 'Usuário'}</small></div><button className="icon-button" onClick={logout} aria-label="Sair" disabled={busy}><LogOut size={17} /></button></div>
      </aside>

      <section className="conversation">
        <header><div><p className="eyebrow">Assistente de contratações</p><div className="conversation-heading"><h2>Conversa</h2>{conversationContext && <span className="context-status">Contexto validado ativo</span>}</div></div><label className="top-k">Top K <input type="number" min="1" max="100" value={topK} onChange={(event) => setTopK(Number(event.target.value))} /></label></header>
        <div className="messages">
          {messages.length === 0 ? <div className="empty-state"><span className="empty-icon"><Building2 size={28} /></span><h1>O que você precisa consultar?</h1><p>Faça uma pergunta sobre contratos, contratações, normas ou documentos públicos.</p><div className="suggestions">{suggestions.map((item) => <button key={item} onClick={() => submitQuestion(item)}>{item}</button>)}</div></div> : messages.map((message) => <article className={`message ${message.role}`} key={message.id}><div className="message-label">{message.role === 'user' ? user.username : 'Assistente'}</div><p>{message.content}</p>{message.response && <ResponseEvidence response={message.response} topK={message.topK ?? topK} />}</article>)}
          {busy && <article className="message assistant"><div className="message-label">Assistente</div><div className="thinking"><span /><span /><span /></div></article>}
        </div>
        <footer><form className="composer" onSubmit={(event) => { event.preventDefault(); void submitQuestion() }}><textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Digite sua pergunta sobre contratações públicas..." rows={1} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void submitQuestion() } }} /><button type="submit" disabled={busy || !question.trim()} aria-label="Enviar"><Send size={18} /></button></form>{error && <p className="composer-error">{error}</p>}</footer>
      </section>
    </main>
  )
}

export default App
