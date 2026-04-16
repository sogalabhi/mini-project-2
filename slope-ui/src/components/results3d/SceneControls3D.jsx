export default function SceneControls3D({
  controls,
  onToggle,
  onPointSize,
  onResetCamera,
  onOverlayMode,
  selectedColumnId,
  reinforcementEnabled,
}) {
  return (
    <div className="scene-controls">
      <div className="results-comparison-title">Scene controls</div>
      <div className="method-chip-row">
        <label className="method-chip">
          <input type="checkbox" checked={controls.showSurface} onChange={() => onToggle('showSurface')} />
          surface
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showSlip} onChange={() => onToggle('showSlip')} />
          slip
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showGrid} onChange={() => onToggle('showGrid')} />
          bounds
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showAxes} onChange={() => onToggle('showAxes')} />
          axes
        </label>
      </div>
      <div className="input-row">
        <div className="input-label">Point size</div>
        <div className="input-wrapper">
          <input
            type="range"
            min="0.02"
            max="0.2"
            step="0.01"
            value={controls.pointSize}
            onChange={(e) => onPointSize(Number(e.target.value))}
          />
          <div className="input-unit">{controls.pointSize.toFixed(2)}</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Overlay</div>
        <select value={controls.overlayMode} onChange={(e) => onOverlayMode(e.target.value)}>
          <option value="none">none</option>
          <option value="convergence">convergence</option>
        </select>
      </div>
      <div className="table-action-row">
        <button type="button" className="action-btn" onClick={onResetCamera}>
          Reset camera
        </button>
      </div>
      <div className="results-comparison-meta">
        Selected from diagnostics: {selectedColumnId != null ? selectedColumnId : 'none'}
      </div>
      {reinforcementEnabled && (
        <div className="assumption-banner">
          Reinforcement overlay uses a simplified approximation (phase2), not full direction-aware intersection.
        </div>
      )}
    </div>
  )
}

