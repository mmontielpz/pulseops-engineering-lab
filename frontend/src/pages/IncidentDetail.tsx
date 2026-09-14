import { useEffect, useState } from 'react'
import { assignOwner, changeStatus, getIncident, listEvents } from '../api/incidents'
import type { Incident, IncidentEvent, Status } from '../types/incident'

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

function describeEvent(event: IncidentEvent): string {
  if (event.event_type === 'ASSIGNED') {
    return event.previous_value
      ? `Reassigned from ${event.previous_value} to ${event.new_value}`
      : `Assigned to ${event.new_value}`
  }
  return `Status changed from ${event.previous_value} to ${event.new_value}`
}

export function IncidentDetail({ incidentId, onBack }: Props) {
  const [incident, setIncident] = useState<Incident | null>(null)
  const [events, setEvents] = useState<IncidentEvent[]>([])
  const [error, setError] = useState<string | null>(null)
  const [ownerInput, setOwnerInput] = useState('')
  const [assigning, setAssigning] = useState(false)
  const [advancing, setAdvancing] = useState(false)

  function reload() {
    getIncident(incidentId)
      .then((data) => {
        setIncident(data)
        setOwnerInput(data.owner ?? '')
      })
      .catch((err) => setError(String(err.message ?? err)))
    listEvents(incidentId)
      .then(setEvents)
      .catch(() => {
        /* timeline is supplementary - don't block the page on it */
      })
  }

  useEffect(reload, [incidentId])

  async function handleAssign(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setAssigning(true)
    try {
      const updated = await assignOwner(incidentId, ownerInput)
      setIncident(updated)
      listEvents(incidentId).then(setEvents)
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
      listEvents(incidentId).then(setEvents)
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

      <div className="timeline">
        <h3>Timeline</h3>
        {events.length === 0 ? (
          <p>No events yet.</p>
        ) : (
          <ul>
            {events.map((event) => (
              <li key={event.id}>
                <span className="timeline-time">
                  {new Date(event.created_at).toLocaleTimeString()}
                </span>{' '}
                {describeEvent(event)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
