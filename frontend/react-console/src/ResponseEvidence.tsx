import { AlertTriangle, Database, ExternalLink, FileText, ShieldCheck } from 'lucide-react'
import type {
  AskResponse,
  CoverageResource,
  CoverageState,
  SourceResponse,
} from './api'

interface ResponseEvidenceProps {
  response: AskResponse
  topK: number
}

const routeLabels: Record<string, string> = {
  structured: 'Dados estruturados',
  rag: 'Documentos',
  hybrid: 'Dados + documentos',
  catalog: 'Catálogo documental',
}

const coverageLabels: Record<CoverageState, string> = {
  covered: 'Coberta no inventário',
  partial: 'Cobertura parcial',
  unavailable: 'Dados indisponíveis',
  unknown: 'Cobertura não comprovada',
}

function metadataText(metadata: Record<string, unknown>, ...keys: string[]) {
  for (const key of keys) {
    const value = metadata[key]
    if (typeof value === 'string' && value.trim()) return value.trim()
    if (typeof value === 'number') return String(value)
  }
  return null
}

function sourceUrl(metadata: Record<string, unknown>) {
  const candidate = metadataText(metadata, 'source_url', 'urlFontePncp', 'url')
  if (!candidate) return null
  try {
    const parsed = new URL(candidate)
    return parsed.protocol === 'https:' || parsed.protocol === 'http:' ? parsed.href : null
  } catch {
    return null
  }
}

function sourceTitle(source: SourceResponse) {
  const title = metadataText(
    source.metadata,
    'title',
    'titulo',
    'documento',
  )
  if (title) return title
  const sourceFile = metadataText(source.metadata, 'source_file')
  return sourceFile?.split(/[\\/]/).at(-1) || source.chunk_id
}

function humanize(value: string) {
  return value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function CoverageResourceItem({ item }: { item: CoverageResource }) {
  const name = item.resource ?? item.dependency ?? 'recurso relacionado'
  const count = typeof item.available_records === 'number'
    ? item.available_records.toLocaleString('pt-BR')
    : null
  return (
    <li>
      <strong>{humanize(name)}</strong>
      {count && <span>{count} registros disponíveis</span>}
      {item.state && <small>{coverageLabels[item.state]}</small>}
    </li>
  )
}

export function ResponseEvidence({ response, topK }: ResponseEvidenceProps) {
  const route = response.route ?? null
  const sources = response.sources ?? []
  const coverage = response.structured_result?.coverage
  const warnings = response.structured_result?.warnings ?? []
  const requiresDocuments = route === 'rag' || route === 'hybrid'

  return (
    <div className="evidence-panel">
      <div className="response-meta" aria-label="Metadados da resposta">
        <span className="route-badge">
          {route === 'structured' ? <Database size={13} /> : <FileText size={13} />}
          {route ? routeLabels[route] ?? humanize(route) : 'Interação social'}
        </span>
        {sources.length > 0 && <span>{sources.length} fonte(s) documental(is)</span>}
        {response.structured_result && <span>{response.structured_result.row_count} linha(s)</span>}
        <span>Top K: {topK}</span>
      </div>

      {coverage && (
        <section className={`coverage-card coverage-${coverage.state}`} aria-label="Cobertura dos dados">
          <header>
            {coverage.state === 'covered' ? <ShieldCheck size={17} /> : <AlertTriangle size={17} />}
            <strong>{coverageLabels[coverage.state]}</strong>
          </header>
          <ul className="coverage-messages">
            {coverage.messages.map((message) => <li key={message}>{message}</li>)}
          </ul>
          {coverage.resources.length > 0 && (
            <ul className="coverage-resources">
              {coverage.resources.map((item, index) => (
                <CoverageResourceItem item={item} key={`${item.resource ?? item.dependency}-${index}`} />
              ))}
            </ul>
          )}
        </section>
      )}

      {warnings.length > 0 && (
        <section className="data-warnings" aria-label="Alertas de qualidade">
          <strong><AlertTriangle size={16} /> Alertas de qualidade</strong>
          <ul>{warnings.map((warning) => (
            <li key={`${warning.code}-${warning.message}`}>
              {warning.message} ({warning.affected_rows.toLocaleString('pt-BR')} registro(s))
            </li>
          ))}</ul>
        </section>
      )}

      {requiresDocuments && sources.length === 0 && (
        <p className="evidence-limitation">
          <AlertTriangle size={16} /> Nenhuma evidência documental foi recuperada nesta resposta.
        </p>
      )}

      {sources.length > 0 && (
        <details className="sources-details">
          <summary>Fontes documentais recuperadas</summary>
          <div className="sources-list">
            {sources.map((source) => {
              const url = sourceUrl(source.metadata)
              const base = metadataText(source.metadata, 'base_id', 'doc_type', 'tipoDocumento')
              return (
                <article className="source" key={`${source.chunk_id}-${source.rank}`}>
                  <div className="source-heading">
                    <span>{source.rank}</span>
                    <strong>{sourceTitle(source)}</strong>
                  </div>
                  <small>Chunk: {source.chunk_id} · relevância: {source.relevance_score.toFixed(4)}</small>
                  {base && <small>Base/tipo: {base}</small>}
                  {url && <a href={url} target="_blank" rel="noreferrer">Abrir fonte original <ExternalLink size={13} /></a>}
                </article>
              )
            })}
          </div>
        </details>
      )}
    </div>
  )
}
