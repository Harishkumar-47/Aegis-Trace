import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

type Status = { api: string; database: string; phase: number }

function App() {
  const [status, setStatus] = useState<Status | null>(null)
  const [error, setError] = useState('')
  useEffect(() => {
    fetch('/api/status').then(async response => {
      if (!response.ok) throw new Error(`API returned ${response.status}`)
      return response.json() as Promise<Status>
    }).then(setStatus).catch((reason: Error) => setError(reason.message))
  }, [])
  return <main className="mx-auto max-w-5xl px-6 py-16">
    <p className="text-sm font-bold tracking-[.3em] text-cyan-400">AEGIS TRACE</p>
    <h1 className="mt-4 text-4xl font-semibold">AI Security Decision Auditor</h1>
    <p className="mt-4 max-w-2xl text-slate-400">Track whether an AI security fix remains safe as new evidence arrives.</p>
    <section className="mt-10 rounded-xl border border-slate-700 bg-slate-900 p-6">
      <h2 className="text-xl font-semibold">System connection</h2>
      {!status && !error && <p className="mt-3 text-slate-400">Checking API and database…</p>}
      {error && <p role="alert" className="mt-3 text-rose-400">Connection failed: {error}</p>}
      {status && <p className="mt-3 text-emerald-400">API {status.api} · PostgreSQL {status.database} · Phase {status.phase}</p>}
    </section>
  </main>
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
