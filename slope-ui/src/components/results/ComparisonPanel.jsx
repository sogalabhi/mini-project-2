import { useResultsStore } from '../../store/resultsStore.js'

export default function ComparisonPanel() {
  const comparison = useResultsStore((s) => s.latest?.comparison)

  if (!comparison?.bishop || !comparison?.fellenius) {
    return (
      <div className="results-comparison-empty">
        Comparison results will appear after analysis.
      </div>
    )
  }

  return (
    <div className="results-comparison-wrap">
      <div className="results-comparison-title">Method Comparison</div>
      <table className="results-comparison-table">
        <thead>
          <tr>
            <th>Method</th>
            <th>FOS</th>
            <th>Center (x,y)</th>
            <th>Radius</th>
          </tr>
        </thead>
        <tbody>
          {[comparison.bishop, comparison.fellenius].map((row) => (
            <tr key={row.method_name}>
              <td>{row.method_name}</td>
              <td>{row.fos != null ? Number(row.fos).toFixed(3) : '--'}</td>
              <td>
                {row.critical_circle_center
                  ? `(${Number(row.critical_circle_center[0]).toFixed(2)}, ${Number(
                      row.critical_circle_center[1],
                    ).toFixed(2)})`
                  : '--'}
              </td>
              <td>
                {row.critical_circle_radius != null
                  ? Number(row.critical_circle_radius).toFixed(2)
                  : '--'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="results-comparison-meta">
        circles: {comparison.circle_count} | seed: {comparison.seed}
      </div>
    </div>
  )
}
