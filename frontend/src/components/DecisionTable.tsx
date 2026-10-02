import type { Decision } from '../types/decision'
import { DecisionBadge } from './DecisionBadge'
import { CategoryBadge } from './CategoryBadge'

export function DecisionTable({ items, open }: { items: Decision[]; open: (id: string) => void }) {
  if (!items.length) return <p className="p-6 text-slate-400">No decisions match these filters.</p>
  return <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b border-slate-700 text-slate-400"><tr>{['Title', 'Category', 'AI Model', 'Created', 'Stage', 'Score'].map(label => <th className="p-4 font-medium" key={label}>{label}</th>)}</tr></thead><tbody>{items.map(item => <tr key={item.id} className="border-b border-slate-800 hover:bg-slate-800/50"><td className="p-4"><button className="font-semibold text-white hover:text-cyan-300" onClick={() => open(item.id)}>{item.title || 'Untitled decision'}</button></td><td className="p-4"><CategoryBadge category={item.category}/></td><td className="p-4 text-slate-300">{item.model_name || 'Unknown'}</td><td className="p-4 text-slate-400">{new Date(item.created_at).toLocaleDateString()}</td><td className="p-4"><DecisionBadge status={item.status}/></td><td className="p-4 text-slate-400">Not Tested</td></tr>)}</tbody></table></div>
}
