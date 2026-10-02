import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { Catalog, DecisionPage } from '../types/decision'
import { DecisionTable } from '../components/DecisionTable'
import { Pagination } from '../components/Pagination'

export function DecisionListPage({ navigate }: { navigate: (path: string) => void }) {
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [model, setModel] = useState('')
  const [status, setStatus] = useState('')
  const [search, setSearch] = useState('')
  const [data, setData] = useState<DecisionPage | null>(null)
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { api.catalog().then(setCatalog).catch(e => setError(e.message)) }, [])
  useEffect(() => {
    const query = new URLSearchParams({ page: String(page), page_size: '20' })
    if (category) query.set('category', category)
    if (model) query.set('model_id', model)
    if (status) query.set('status', status)
    if (search.trim()) query.set('search', search.trim())
    setData(null); setError('')
    api.decisions(query).then(setData).catch(e => setError(e.message))
  }, [page, category, model, status, search])
  return <section><div className="flex items-center justify-between"><div><p className="text-sm uppercase tracking-widest text-cyan-400">Decision ledger</p><h1 className="mt-2 text-3xl font-semibold">AI Security Decisions</h1></div><button onClick={() => navigate('/decisions/new')} className="rounded-lg bg-cyan-400 px-5 py-3 font-semibold text-slate-950 hover:bg-cyan-300">Capture Decision</button></div>
    <div className="mt-8 grid gap-3 sm:grid-cols-4"><input aria-label="Search decisions" className="rounded border border-slate-700 bg-slate-900 p-3" placeholder="Search decisions" value={search} onChange={e => { setPage(1); setSearch(e.target.value) }}/><select aria-label="Category filter" className="rounded border border-slate-700 bg-slate-900 p-3" value={category} onChange={e => { setPage(1); setCategory(e.target.value) }}><option value="">All categories</option>{['authentication','authorization','injection','container_security','dependency_security','IAM','network_configuration','cloud_security','IaC','secrets','cryptography','other'].map(c => <option key={c} value={c}>{c.replaceAll('_',' ')}</option>)}</select><select aria-label="Model filter" className="rounded border border-slate-700 bg-slate-900 p-3" value={model} onChange={e => { setPage(1); setModel(e.target.value) }}><option value="">All models</option>{catalog?.models.map(m => <option key={m.id} value={m.id}>{m.provider} · {m.name}</option>)}</select><select aria-label="Status filter" className="rounded border border-slate-700 bg-slate-900 p-3" value={status} onChange={e => { setPage(1); setStatus(e.target.value) }}><option value="">All stages</option><option value="captured">Captured</option></select></div>
    <div className="mt-6 rounded-xl border border-slate-700 bg-slate-900">{error ? <p role="alert" className="p-6 text-rose-400">{error}</p> : data ? <DecisionTable items={data.items} open={id => navigate(`/decisions/${id}`)}/> : <p className="p-6 text-slate-400">Loading decisions…</p>}</div>
    {data && <Pagination page={page} pageSize={data.page_size} total={data.total} onChange={setPage}/>}
  </section>
}
