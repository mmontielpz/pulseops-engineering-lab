import { useState } from 'react'
import { createIncident } from '../api/incidents'
import type { Severity } from '../types/incident'

interface Props {
  onCreated: () => void
}

export function NewIncident({ onCreated }: Props) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [severity, setSeverity] = useState<Severity>('P3')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await createIncident({ title, description, severity })
      setTitle('')
      setDescription('')
      setSeverity('P3')
      onCreated()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="new-incident-form">
      <h3>New Incident</h3>
      {error && <p role="alert">{error}</p>}
      <label>
        Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label>
        Description
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
      </label>
      <label>
        Severity
        <select value={severity} onChange={(e) => setSeverity(e.target.value as Severity)}>
          <option value="P1">P1</option>
          <option value="P2">P2</option>
          <option value="P3">P3</option>
          <option value="P4">P4</option>
        </select>
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? 'Creating...' : 'Create Incident'}
      </button>
    </form>
  )
}
