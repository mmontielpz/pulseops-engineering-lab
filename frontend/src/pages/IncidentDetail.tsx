import { useEffect, useState } from 'react'
import { assignOwner, getIncident } from '../api/incidents'
import type { Incident } from '../types/incident'

interface Props {
  incidentId: string
  onBack: () => void
}

export function IncidentDetail({ incidentId, onBack }: Props) {
  const [incident, setIncident] = useState<Incident | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [ownerInput, setOwnerInput] = useState('')
  const [assigning, setAssigning] = useState(false)

  useEffect(() => {
    getIncident(incidentId)
      .then((data) => {
        setIncident(data)
        setOwnerInput(data.owner ?? '')
      })
      .catch((err) => setError(String(err.message ?? err)))
  }, [incidentId])

  async function handleAssign(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setAssigning(true)
    try {
      const updated = await assignOwner(incidentId, ownerInput)
      setIncident(updated)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setAssigning(false)
    }
  }

  if (error && !incident) return <p role="alert">Error: {error}</p>
  if (!incident) return <p>Loading...</p>

  return (
    <div className="incident-detail">
      <button onClick={onBack}>&larr; Back to incidents</button>
      <h2>
        Incident #{incident.id}: {incident.title}
      </h2>
      <dl>
        <dt>Severity</dt>
        <dd>{incident.severity}</dd>
        <dt>Status</dt>
        <dd>{incident.status}</dd>
        <dt>Owner</dt>
        <dd>{incident.owner ?? 'Unassigned'}</dd>
        <dt>Description</dt>
        <dd>{incident.description || 'No description provided.'}</dd>
      </dl>

      <form onSubmit={handleAssign} className="assign-form">
        <h3>Assign Owner</h3>
        {error && <p role="alert">{error}</p>}
        <label>
          Owner
          <input
            value={ownerInput}
            onChange={(e) => setOwnerInput(e.target.value)}
            placeholder="e.g. steven"
          />
        </label>
        <button type="submit" disabled={assigning}>
          {assigning ? 'Assigning...' : 'Assign'}
        </button>
      </form>

      {/* Status workflow control (S002) and the audit timeline (S003)
          are intentionally not implemented yet. */}
    </div>
  )
}
