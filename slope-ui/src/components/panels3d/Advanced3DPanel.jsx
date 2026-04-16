import { useForm3dStore } from '../../store/form3dStore.js'

export default function Advanced3DPanel() {
  const advanced = useForm3dStore((s) => s.advanced)
  const grid = useForm3dStore((s) => s.gridConfig)
  const setAdvanced = useForm3dStore((s) => s.setAdvanced)
  const projectedRows = grid.colXMax * grid.colYMax

  return (
    <div className="prop-group">
      <div className="prop-group-title">Advanced</div>
      <div className="input-row">
        <div className="input-label">Include rows</div>
        <input
          type="checkbox"
          checked={advanced.includeAnalysisRows}
          onChange={(e) => setAdvanced({ includeAnalysisRows: e.target.checked })}
        />
      </div>
      {projectedRows > 20000 && (
        <div style={{ color: 'var(--status-red)' }}>
          Warning: projected rows {projectedRows} exceed safe debug threshold.
        </div>
      )}
      <div className="results-comparison-meta">
        Visualizer is deferred in MVP. Diagnostics and payload views are primary.
      </div>
    </div>
  )
}

