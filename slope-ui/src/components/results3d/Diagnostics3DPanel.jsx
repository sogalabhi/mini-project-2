import { useResults3dStore } from '../../store/results3dStore.js'
import { useUi3dStore } from '../../store/ui3dStore.js'

export default function Diagnostics3DPanel() {
  const result = useResults3dStore((s) => s.latestSingle)
  const payload = useResults3dStore((s) => s.lastPayload)
  const loading = useResults3dStore((s) => s.loading)
  const selectedColumnId = useUi3dStore((s) => s.selectedColumnId)
  const setSelectedColumnId = useUi3dStore((s) => s.setSelectedColumnId)

  if (loading) return <div className="skeleton-panel">Loading diagnostics…</div>
  if (!result?.diagnostics) return <div className="results-comparison-empty">Diagnostics appear after analysis.</div>
  const reinforcementEnabled = Boolean(payload?.reinforcement?.enabled)
  const methodDiag = result.diagnostics.method ?? {}
  const renderData = result.render_data ?? null

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
      {reinforcementEnabled && (
        <>
          <div className="results-comparison-title">Reinforcement assumptions (phase2 simplified)</div>
          <div className="results-comparison-meta">- direction-independent per-column addition</div>
          <div className="results-comparison-meta">- optional vertical component coupling</div>
          <div className="results-comparison-meta">- no explicit per-nail slip intersection</div>
          <div className="results-comparison-meta">
            Assumptions shown are a concise summary. See model docs for full details.
          </div>
          <pre className="json-preview">
            {JSON.stringify(
              {
                t_y: methodDiag.t_y ?? null,
                t_bond: methodDiag.t_bond ?? null,
                t_max: methodDiag.t_max ?? null,
                q_nail: methodDiag.q_nail ?? null,
                total_added_resistance: methodDiag.total_added_resistance ?? null,
              },
              null,
              2,
            )}
          </pre>
        </>
      )}
      <div className="results-comparison-title">Method diagnostics</div>
      <pre className="json-preview">{JSON.stringify(result.diagnostics.method, null, 2)}</pre>
      {renderData && (
        <>
          <div className="results-comparison-title">Render diagnostics</div>
          <pre className="json-preview">
            {JSON.stringify(
              {
                column_count: renderData.columns?.length ?? 0,
                fs_field_range: [renderData.fs_field?.min ?? null, renderData.fs_field?.max ?? null],
                morphology_method: renderData.morphology?.method ?? null,
              },
              null,
              2,
            )}
          </pre>
        </>
      )}
    </div>
  )
}

