import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { DecisionListPage } from './pages/DecisionListPage'
import { CreateDecisionPage } from './pages/CreateDecisionPage'
import { DecisionDetailPage } from './pages/DecisionDetailPage'
import './index.css'

function App() {
  const [path, setPath] = useState(location.pathname)
  useEffect(() => { const update = () => setPath(location.pathname); addEventListener('popstate', update); return () => removeEventListener('popstate', update) }, [])
  function navigate(target: string) { history.pushState({}, '', target); setPath(location.pathname); window.scrollTo(0, 0) }
  const detailId = path.startsWith('/decisions/') && path !== '/decisions/new' ? path.split('/')[2] : null
  return <div className="min-h-screen"><header className="border-b border-slate-800 bg-slate-950/80"><div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5"><button className="text-lg font-bold tracking-[.2em] text-cyan-400" onClick={() => navigate('/decisions')}>AEGIS TRACE</button><nav className="flex gap-6 text-sm text-slate-300"><button onClick={() => navigate('/decisions')} className="hover:text-white">Decisions</button><button onClick={() => navigate('/decisions/new')} className="hover:text-white">Capture</button></nav></div></header><main className="mx-auto max-w-6xl px-6 py-10">{path === '/decisions/new' ? <CreateDecisionPage navigate={navigate}/> : detailId ? <DecisionDetailPage id={detailId} navigate={navigate}/> : <DecisionListPage navigate={navigate}/>}</main></div>
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
