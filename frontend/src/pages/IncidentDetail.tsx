import { useEffect, useState } from 'react'
import { assignOwner, changeStatus, getIncident } from '../api/incidents'
import type { Incident, Status } from '../types/incident'

interface Props {
  incidentId: string
  onBack: () => void
}

const NEXT_STATUS: Record<Status, Status | null> = {
  OPEN: 'INVESTIGATING',
  INVESTIGATING: 'RESOLVED',
  RESOLVED: 'CLOSED',
  CLOSED: null,
}

export function IncidentDetail({ incidentId, onBack }: Props) {
  const [incident, setIncident] = useState<Incident | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [ownerInput, setOwnerInput] = useState('')
  const [assigning, setAssigning] = useState(false)
  const [advancing, setAdvancing] = useState(false)

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

  async function handleAdvance() {
    if (!incident) return
    const next = NEXT_STATUS[incident.status]
    if (!next) return
    setError(null)
    setAdvancing(true)
    try {
      const updated = await changeStatus(incidentId, next)
      setIncident(updated)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setAdvancing(false)
    }
  }

  if (error && !incident) return <p role="alert">Error: {error}</p>
  if (!incident) return <p>Loading...</p>

  const next = NEXT_STATUS[incident.status]

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

      {error && <p role="alert">{error}</p>}

      <form onSubmit={handleAssign} className="assign-form">
        <h3>Assign Owner</h3>
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

      <div className="status-control">
        <h3>Status</h3>
        {next ? (
          <button onClick={handleAdvance} disabled={advancing}>
            {advancing ? 'Updating...' : `Advance to ${next}`}
          </button>
        ) : (
          <p>This incident is closed.</p>
        )}
      </div>

      {/* The audit timeline (S003) is intentionally not implemented yet. */}
    </div>
  )
}
