import type { Catalog, Decision, DecisionCreate, DecisionPage } from '../types/decision'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } })
  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try { const body = await response.json(); message = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail) } catch { /* keep status */ }
    throw new Error(message)
  }
  return response.json() as Promise<T>
}

export const api = {
  catalog: () => request<Catalog>('/catalog'),
  decisions: (query: URLSearchParams) => request<DecisionPage>(`/decisions?${query}`),
  decision: (id: string) => request<Decision>(`/decisions/${encodeURIComponent(id)}`),
  create: (payload: DecisionCreate) => request<Decision>('/decisions', { method: 'POST', body: JSON.stringify(payload) }),
  ledger: () => request<{ valid: boolean; checked: number; broken_at: string | null }>('/ledger/verify'),
}
