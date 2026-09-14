import { useEffect, useState } from 'react'
import { listIncidents } from '../api/incidents'
import type { Incident } from '../types/incident'

interface Props {
  onSelect: (id: string) => void
  refreshKey: number
}

export function IncidentList({ onSelect, refreshKey }: Props) {
  const [incidents, setIncidents] = useState<Incident[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    listIncidents()
      .then((data) => {
        if (!cancelled) {
          setIncidents(data)
          setError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(String(err.message ?? err))
      })
    return () => {
      cancelled = true
    }
  }, [refreshKey])

  if (error) return <p role="alert">Error: {error}</p>
  if (incidents === null) return <p>Loading incidents...</p>
  if (incidents.length === 0) return <p>No incidents yet.</p>

  return (
    <table className="incident-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Title</th>
          <th>Status</th>
          <th>Severity</th>
          <th>Owner</th>
        </tr>
      </thead>
      <tbody>
        {incidents.map((incident) => (
          <tr key={incident.id} onClick={() => onSelect(incident.id)} className="incident-row">
            <td>#{incident.id}</td>
            <td>{incident.title}</td>
            <td>
              <span className={`badge status-${incident.status.toLowerCase()}`}>
                {incident.status}
              </span>
            </td>
            <td>
              <span className={`badge severity-${incident.severity.toLowerCase()}`}>
                {incident.severity}
              </span>
            </td>
            <td>{incident.owner ?? '-'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
