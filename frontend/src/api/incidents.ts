import type { Incident, IncidentCreateInput, IncidentEvent } from '../types/incident'

const BASE = '/incidents'

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `Request failed with status ${res.status}`)
  }
  return res.json() as Promise<T>
}

export async function listIncidents(): Promise<Incident[]> {
  const res = await fetch(BASE)
  return handle<Incident[]>(res)
}

export async function getIncident(id: string): Promise<Incident> {
  const res = await fetch(`${BASE}/${id}`)
  return handle<Incident>(res)
}

export async function createIncident(input: IncidentCreateInput): Promise<Incident> {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  return handle<Incident>(res)
}

export async function assignOwner(id: string, owner: string): Promise<Incident> {
  const res = await fetch(`${BASE}/${id}/assign`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ owner }),
  })
  return handle<Incident>(res)
}

export async function changeStatus(id: string, status: string): Promise<Incident> {
  const res = await fetch(`${BASE}/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
  return handle<Incident>(res)
}

export async function listEvents(id: string): Promise<IncidentEvent[]> {
  const res = await fetch(`${BASE}/${id}/events`)
  return handle<IncidentEvent[]>(res)
}
