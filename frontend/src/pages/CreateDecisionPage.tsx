import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { Catalog } from '../types/decision'

const inputClass = 'w-full rounded border border-slate-700 bg-slate-950 p-3 text-slate-100'
export function CreateDecisionPage({ navigate }: { navigate: (path: string) => void }) {
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [title, setTitle] = useState('')
  const [userId, setUserId] = useState('')
  const [modelId, setModelId] = useState('')
  const [category, setCategory] = useState('authentication')
  const [prompt, setPrompt] = useState('')
  const [recommendation, setRecommendation] = useState('')
  const [diff, setDiff] = useState('')
  const [files, setFiles] = useState('')
  useEffect(() => { api.catalog().then(value => { setCatalog(value); setUserId(value.users[0]?.id || ''); setModelId(value.models[0]?.id || '') }).catch(e => setError(e.message)) }, [])
  async function submit(event: React.FormEvent) {
    event.preventDefault(); setError(''); setSaving(true)
    try {
      const decision = await api.create({ title, user_id: userId, model_id: modelId, category, prompt, recommendation_text: recommendation, diff_content: diff, affected_files: files.split(/\r?\n/).map(s => s.trim()).filter(Boolean) })
      navigate(`/decisions/${decision.id}?captured=1`)
    } catch (reason) { setError((reason as Error).message) } finally { setSaving(false) }
  }
  return <section className="max-w-3xl"><button className="text-sm text-cyan-400" onClick={() => navigate('/decisions')}>← Decisions</button><h1 className="mt-4 text-3xl font-semibold">New AI Security Decision</h1><p className="mt-2 text-slate-400">Capture the recommendation and exact code or configuration diff as immutable evidence.</p>
    <form onSubmit={submit} className="mt-8 space-y-5 rounded-xl border border-slate-700 bg-slate-900 p-6">
      <label className="block">Title<input required minLength={3} maxLength={200} className={inputClass} value={title} onChange={e => setTitle(e.target.value)}/></label>
      <div className="grid gap-5 sm:grid-cols-2"><label className="block">Developer<select required className={inputClass} value={userId} onChange={e => setUserId(e.target.value)}>{catalog?.users.map(u => <option key={u.id} value={u.id}>{u.email}</option>)}</select></label><label className="block">AI Provider / Model<select required className={inputClass} value={modelId} onChange={e => setModelId(e.target.value)}>{catalog?.models.map(m => <option key={m.id} value={m.id}>{m.provider} · {m.name}</option>)}</select></label></div>
      <label className="block">Category<select className={inputClass} value={category} onChange={e => setCategory(e.target.value)}>{['authentication','authorization','injection','container_security','dependency_security','IAM','network_configuration','cloud_security','IaC','secrets','cryptography','other'].map(c => <option key={c} value={c}>{c.replaceAll('_',' ')}</option>)}</select></label>
      <label className="block">Prompt (optional)<textarea className={inputClass} rows={3} value={prompt} onChange={e => setPrompt(e.target.value)}/></label>
      <label className="block">Recommendation<textarea required minLength={10} className={inputClass} rows={5} value={recommendation} onChange={e => setRecommendation(e.target.value)}/></label>
      <label className="block">Code / Config Diff<textarea required className={`${inputClass} font-mono text-sm`} rows={9} placeholder="--- a/app.py&#10;+++ b/app.py" value={diff} onChange={e => setDiff(e.target.value)}/></label>
      <label className="block">Affected Files <span className="text-slate-400">(one relative path per line)</span><textarea required className={inputClass} rows={3} placeholder="backend/app/auth.py" value={files} onChange={e => setFiles(e.target.value)}/></label>
      {error && <p role="alert" className="text-rose-400">{error}</p>}
      <button disabled={saving || !catalog || !userId || !modelId} className="rounded-lg bg-cyan-400 px-6 py-3 font-semibold text-slate-950 disabled:opacity-50">{saving ? 'Capturing…' : 'Capture Decision'}</button>
    </form>
  </section>
}
