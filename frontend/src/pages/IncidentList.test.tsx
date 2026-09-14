import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { IncidentList } from '../pages/IncidentList'
import type { Incident } from '../types/incident'

const sample: Incident = {
  id: 'abc123',
  title: 'Payment API failing',
  description: '5xx spike',
  severity: 'P1',
  status: 'OPEN',
  owner: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('IncidentList', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({
        ok: true,
        json: async () => [sample],
      })) as unknown as typeof fetch,
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders incidents returned by the API', async () => {
    render(<IncidentList refreshKey={0} onSelect={() => {}} />)

    await waitFor(() => expect(screen.getByText('Payment API failing')).toBeInTheDocument())
    expect(screen.getByText('OPEN')).toBeInTheDocument()
    expect(screen.getByText('P1')).toBeInTheDocument()
  })

  it('shows an empty state when there are no incidents', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({ ok: true, json: async () => [] })) as unknown as typeof fetch,
    )

    render(<IncidentList refreshKey={0} onSelect={() => {}} />)

    await waitFor(() => expect(screen.getByText('No incidents yet.')).toBeInTheDocument())
  })
})
