import { useEffect, useState } from 'react'
import { getIncident } from '../api/incidents'
import type { Incident } from '../types/incident'

interface Props {
  incidentId: string
  onBack: () => void
}

export function IncidentDetail({ incidentId, onBack }: Props) {
  const [incident, setIncident] = useState<Incident | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getIncident(incidentId)
      .then(setIncident)
      .catch((err) => setError(String(err.message ?? err)))
  }, [incidentId])

  if (error) return <p role="alert">Error: {error}</p>
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
      {/* Assignment control (S001), status workflow control (S002), and
          the audit timeline (S003) are intentionally not implemented yet -
          these are the workshop's hands-on slices. */}
    </div>
  )
}
