import { afterEach, describe, expect, it, vi } from 'vitest'
import { createIncident, listIncidents } from './incidents'

describe('incidents API client', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('listIncidents fetches from /incidents', async () => {
    const fetchMock = vi.fn(async () => ({ ok: true, json: async () => [] }))
    vi.stubGlobal('fetch', fetchMock as unknown as typeof fetch)

    await listIncidents()

    expect(fetchMock).toHaveBeenCalledWith('/incidents')
  })

  it('createIncident throws with the server-provided detail message on failure', async () => {
    const fetchMock = vi.fn(async () => ({
      ok: false,
      status: 422,
      json: async () => ({ detail: 'title must not be empty' }),
    }))
    vi.stubGlobal('fetch', fetchMock as unknown as typeof fetch)

    await expect(
      createIncident({ title: '', description: '', severity: 'P3' }),
    ).rejects.toThrow('title must not be empty')
  })
})
