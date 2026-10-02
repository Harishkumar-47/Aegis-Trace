// @vitest-environment jsdom
import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { DecisionListPage } from './DecisionListPage'
import { CreateDecisionPage } from './CreateDecisionPage'
import { api } from '../services/api'

vi.mock('../services/api', () => ({ api: { catalog: vi.fn(), decisions: vi.fn(), create: vi.fn() } }))
afterEach(() => { cleanup(); vi.clearAllMocks() })

const catalog = { users: [{ id: 'user-1', email: 'demo@aegis.local' }], models: [{ id: 'model-1', provider: 'Demo', name: 'Example model', version: '1' }] }

test('decision list renders API records and opens detail', async () => {
  vi.mocked(api.catalog).mockResolvedValue(catalog)
  vi.mocked(api.decisions).mockResolvedValue({ items: [{ id: 'decision-1', title: 'Authentication fix', category: 'authentication', model_name: 'Example model', created_at: '2026-10-02T00:00:00Z', status: 'captured' } as never], page: 1, page_size: 20, total: 1 })
  const navigate = vi.fn()
  render(<DecisionListPage navigate={navigate}/> )
  expect(await screen.findByText('Authentication fix')).toBeTruthy()
  expect(screen.getByText('Not Tested')).toBeTruthy()
  fireEvent.click(screen.getByText('Authentication fix'))
  expect(navigate).toHaveBeenCalledWith('/decisions/decision-1')
})

test('capture form sends typed fields and opens stored decision', async () => {
  vi.mocked(api.catalog).mockResolvedValue(catalog)
  vi.mocked(api.create).mockResolvedValue({ id: 'decision-2' } as never)
  const navigate = vi.fn()
  render(<CreateDecisionPage navigate={navigate}/> )
  await screen.findByText('demo@aegis.local')
  fireEvent.change(screen.getByLabelText('Title'), { target: { value: 'Fix SQL injection' } })
  fireEvent.change(screen.getByLabelText('Recommendation'), { target: { value: 'Use parameterized SQL queries.' } })
  fireEvent.change(screen.getByLabelText('Code / Config Diff'), { target: { value: '--- a/app.py\n+++ b/app.py' } })
  fireEvent.change(screen.getByLabelText(/Affected Files/), { target: { value: 'app.py' } })
  fireEvent.click(screen.getByRole('button', { name: 'Capture Decision' }))
  await waitFor(() => expect(api.create).toHaveBeenCalledWith(expect.objectContaining({ title: 'Fix SQL injection', affected_files: ['app.py'] })))
  await waitFor(() => expect(navigate).toHaveBeenCalledWith('/decisions/decision-2?captured=1'))
})
