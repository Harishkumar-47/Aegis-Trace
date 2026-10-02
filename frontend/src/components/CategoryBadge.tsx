export function CategoryBadge({ category }: { category: string }) {
  return <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">{category.replaceAll('_', ' ')}</span>
}
