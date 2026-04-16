export default function SceneControls3D({
  controls,
  onToggle,
  onPointSize,
  onResetCamera,
  onOverlayMode,
  onOpacity,
  onPrismMaxColumns,
  selectedColumnId,
  reinforcementEnabled,
  warnings = [],
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
        <label className="method-chip">
          <input type="checkbox" checked={controls.showTerrainMesh} onChange={() => onToggle('showTerrainMesh')} />
          terrain mesh
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showSlipMesh} onChange={() => onToggle('showSlipMesh')} />
          slip mesh
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showColumnCenters} onChange={() => onToggle('showColumnCenters')} />
          centers
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showColumnLines} onChange={() => onToggle('showColumnLines')} />
          lines
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showColumnPrisms} onChange={() => onToggle('showColumnPrisms')} />
          prisms
        </label>
        <label className="method-chip">
          <input type="checkbox" checked={controls.showMorphology} onChange={() => onToggle('showMorphology')} />
          morphology
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
          <option value="fs_heatmap">fs heatmap</option>
        </select>
      </div>
      <div className="input-row">
        <div className="input-label">Mesh opacity</div>
        <div className="input-wrapper">
          <input
            type="range"
            min="0.05"
            max="1"
            step="0.05"
            value={controls.meshOpacity}
            onChange={(e) => onOpacity(Number(e.target.value))}
          />
          <div className="input-unit">{controls.meshOpacity.toFixed(2)}</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Prism cap</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="100"
            max="5000"
            step="100"
            value={controls.prismMaxColumns}
            onChange={(e) => onPrismMaxColumns(Number(e.target.value) || 1500)}
          />
          <div className="input-unit">cols</div>
        </div>
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
      {warnings.map((warning) => (
        <div key={warning} className="results-comparison-meta">{warning}</div>
      ))}
    </div>
  )
}

