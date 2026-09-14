export type Severity = 'P1' | 'P2' | 'P3' | 'P4'
export type Status = 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'CLOSED'

export interface Incident {
  id: string
  title: string
  description: string
  severity: Severity
  status: Status
  owner: string | null
  created_at: string
  updated_at: string
}

export interface IncidentCreateInput {
  title: string
  description: string
  severity: Severity
}

export type EventType = 'ASSIGNED' | 'STATUS_CHANGED'

export interface IncidentEvent {
  id: string
  incident_id: string
  event_type: EventType
  previous_value: string | null
  new_value: string
  created_at: string
}
