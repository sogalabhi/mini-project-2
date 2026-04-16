import { useResults3dStore } from '../../store/results3dStore.js'
import { useUi3dStore } from '../../store/ui3dStore.js'

export default function Diagnostics3DPanel() {
  const result = useResults3dStore((s) => s.latestSingle)
  const loading = useResults3dStore((s) => s.loading)
  const selectedColumnId = useUi3dStore((s) => s.selectedColumnId)
  const setSelectedColumnId = useUi3dStore((s) => s.setSelectedColumnId)

  if (loading) return <div className="skeleton-panel">Loading diagnostics…</div>
  if (!result?.diagnostics) return <div className="results-comparison-empty">Diagnostics appear after analysis.</div>

  return (
    <div className="results-details">
      <div className="input-row">
        <div className="input-label">Highlight column</div>
        <div className="input-wrapper">
          <input
            type="number"
            value={selectedColumnId ?? ''}
            onChange={(e) =>
              setSelectedColumnId(e.target.value === '' ? null : Number(e.target.value))
            }
          />
          <div className="input-unit">id</div>
        </div>
      </div>
      <div className="results-comparison-title">Pipeline diagnostics</div>
      <pre className="json-preview">{JSON.stringify(result.diagnostics.pipeline, null, 2)}</pre>
      <div className="results-comparison-title">Method diagnostics</div>
      <pre className="json-preview">{JSON.stringify(result.diagnostics.method, null, 2)}</pre>
    </div>
  )
}

