import { useState } from 'react'
import { ThumbsDown, ThumbsUp } from 'lucide-react'
import { submitFeedback } from './api'


interface FeedbackControlsProps {
  historyId: number
}


export function FeedbackControls({ historyId }: FeedbackControlsProps) {
  const [rating, setRating] = useState<-1 | 1 | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function rate(value: -1 | 1) {
    if (busy) return
    setBusy(true)
    setError('')
    try {
      const result = await submitFeedback(historyId, value)
      setRating(result.rating)
    } catch {
      setError('Não foi possível registrar a avaliação.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="feedback-controls" aria-label="Avaliar resposta">
      <span>{rating === null ? 'Esta resposta foi útil?' : 'Avaliação registrada'}</span>
      <button
        type="button"
        aria-label="Resposta útil"
        aria-pressed={rating === 1}
        className={rating === 1 ? 'selected' : ''}
        disabled={busy}
        onClick={() => void rate(1)}
      >
        <ThumbsUp size={14} />
      </button>
      <button
        type="button"
        aria-label="Resposta não útil"
        aria-pressed={rating === -1}
        className={rating === -1 ? 'selected' : ''}
        disabled={busy}
        onClick={() => void rate(-1)}
      >
        <ThumbsDown size={14} />
      </button>
      {error && <small role="alert">{error}</small>}
    </section>
  )
}
