import { useResults3dStore } from '../../store/results3dStore.js'

export default function Summary3DPanel() {
  const result = useResults3dStore((s) => s.latestSingle)
  const compareSnapshot = useResults3dStore((s) => s.compareSnapshot)
  const lastPayload = useResults3dStore((s) => s.lastPayload)
  const loading = useResults3dStore((s) => s.loading)
  const error = useResults3dStore((s) => s.error)
  const reinforcementEnabled = Boolean(lastPayload?.reinforcement?.enabled)

  if (loading) return <div className="skeleton-panel">Loading summary…</div>
  if (!result) return <div className="results-comparison-empty">Run 3D analysis to view summary.</div>

  return (
    <div className="fos-display">
      <div className="fos-label">FS min</div>
      <div className="fos-value">{result.fs_min != null ? Number(result.fs_min).toFixed(3) : '--'}</div>
      <div className="status-badge">{result.converged ? 'Converged' : 'Not converged'}</div>
      <div className="results-comparison-meta">
        direction: {result.critical_direction_rad != null ? Number(result.critical_direction_rad).toFixed(4) : '--'} rad
      </div>
      <div className="results-comparison-meta">method: {result.method_id ?? '--'} | columns: {result.column_count ?? '--'}</div>
      {reinforcementEnabled && <div className="fidelity-badge">Simplified reinforcement model</div>}
      {reinforcementEnabled && compareSnapshot && (
        <>
          <div className="results-comparison-meta">FS without nails: {compareSnapshot.baselineFs.toFixed(3)}</div>
          <div className="results-comparison-meta">FS with nails: {compareSnapshot.reinforcedFs.toFixed(3)}</div>
          <div className="results-comparison-meta">Delta FS: {compareSnapshot.deltaFs.toFixed(3)}</div>
        </>
      )}
      {reinforcementEnabled && !compareSnapshot && (
        <div className="results-comparison-meta">
          Delta FS appears after running compare with/without nails.
        </div>
      )}
      {error && <div style={{ color: 'var(--status-red)' }}>{error}</div>}
    </div>
  )
}

