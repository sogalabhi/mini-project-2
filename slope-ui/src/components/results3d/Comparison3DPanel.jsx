import { useResults3dStore } from '../../store/results3dStore.js'

export default function Comparison3DPanel() {
  const multi = useResults3dStore((s) => s.latestMulti)
  const loading = useResults3dStore((s) => s.loading)

  if (loading) return <div className="skeleton-panel">Loading comparison…</div>
  if (!multi?.results?.length) {
    return <div className="results-comparison-empty">Run comparison mode to view multi-method results.</div>
  }

  return (
    <div className="results-comparison-wrap">
      <div className="results-comparison-title">3D Method Comparison</div>
      <table className="results-comparison-table">
        <thead>
          <tr>
            <th>Method</th>
            <th>Status</th>
            <th>FS min</th>
            <th>Direction</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          {multi.results.map((row) => (
            <tr key={`m-${row.method_id}`}>
              <td>{row.method_id}</td>
              <td>{row.ok ? 'ok' : 'failed'}</td>
              <td>{row.fs_min != null ? Number(row.fs_min).toFixed(3) : '--'}</td>
              <td>{row.critical_direction_rad != null ? Number(row.critical_direction_rad).toFixed(4) : '--'}</td>
              <td>{row.error?.message || '--'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

