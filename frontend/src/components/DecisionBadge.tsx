export function DecisionBadge({ status }: { status: string }) {
  return <span className="rounded-full border border-cyan-700 bg-cyan-950 px-3 py-1 text-xs font-medium text-cyan-300">{status === 'captured' ? 'Captured' : status}</span>
}
