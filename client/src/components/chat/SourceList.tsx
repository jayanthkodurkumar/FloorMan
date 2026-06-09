import type { Source } from '../../types'

interface Props {
  sources: Source[]
}

export default function SourceList({ sources }: Props) {
  if (!sources.length) return null
  return (
    <details className="mt-2 text-xs">
      <summary className="cursor-pointer text-gray-400 hover:text-gray-600 select-none">
        {sources.length} source{sources.length > 1 ? 's' : ''}
      </summary>
      <ul className="mt-2 flex flex-col gap-1">
        {sources.map((s, i) => (
          <li key={i} className="flex items-center gap-2 text-gray-500">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0" />
            <span>{s.file}</span>
            <span className="text-gray-300">—</span>
            <span>Page {s.page}</span>
            <span className="ml-auto text-gray-400">{(s.score * 100).toFixed(0)}%</span>
          </li>
        ))}
      </ul>
    </details>
  )
}
