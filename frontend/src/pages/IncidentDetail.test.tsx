import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { IncidentDetail } from './IncidentDetail'
import type { Incident } from '../types/incident'

const sample: Incident = {
  id: 'abc123',
  title: 'Login latency',
  description: 'p95 above 3s',
  severity: 'P2',
  status: 'OPEN',
  owner: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('IncidentDetail', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (_url: string, init?: RequestInit) => {
        if (init?.method === 'PATCH') {
          return { ok: true, json: async () => ({ ...sample, owner: 'steven' }) }
        }
        return { ok: true, json: async () => sample }
      }) as unknown as typeof fetch,
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('assigns an owner and reflects the update', async () => {
    render(<IncidentDetail incidentId="abc123" onBack={() => {}} />)

    await waitFor(() => expect(screen.getByText(/Login latency/)).toBeInTheDocument())
    expect(screen.getByText('Unassigned')).toBeInTheDocument()

    const input = screen.getByPlaceholderText('e.g. steven')
    fireEvent.change(input, { target: { value: 'steven' } })
    fireEvent.click(screen.getByRole('button', { name: 'Assign' }))

    await waitFor(() => expect(screen.getByText('steven')).toBeInTheDocument())
  })
})
