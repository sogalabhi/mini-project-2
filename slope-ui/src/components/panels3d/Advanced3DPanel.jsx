import { useForm3dStore } from '../../store/form3dStore.js'

export default function Advanced3DPanel() {
  const advanced = useForm3dStore((s) => s.advanced)
  const reinforcement = useForm3dStore((s) => s.reinforcement)
  const grid = useForm3dStore((s) => s.gridConfig)
  const setAdvanced = useForm3dStore((s) => s.setAdvanced)
  const setReinforcement = useForm3dStore((s) => s.setReinforcement)
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
      <div className="prop-group-title">Reinforcement</div>
      <div className="input-row">
        <div className="input-label">Enabled</div>
        <input
          type="checkbox"
          checked={reinforcement.enabled}
          onChange={(e) => setReinforcement({ enabled: e.target.checked })}
        />
      </div>
      {reinforcement.enabled && (
        <>
          <div className="assumption-banner">
            <strong>Simplified model (phase2)</strong>: uniform column-based nail contribution is applied.
            Direction-aware nail-slip intersection is deferred. See docs for model fidelity details.
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Diameter
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="0.001"
                step="0.001"
                value={reinforcement.diameter}
                onChange={(e) => setReinforcement({ diameter: Number(e.target.value) || 0.001 })}
              />
              <div className="input-unit">m</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Embed length
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="0.01"
                step="0.1"
                value={reinforcement.lengthEmbed}
                onChange={(e) => setReinforcement({ lengthEmbed: Number(e.target.value) || 0.01 })}
              />
              <div className="input-unit">m</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Spacing X
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="0.01"
                step="0.1"
                value={reinforcement.spacingX}
                onChange={(e) => setReinforcement({ spacingX: Number(e.target.value) || 0.01 })}
              />
              <div className="input-unit">m</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Spacing Y
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="0.01"
                step="0.1"
                value={reinforcement.spacingY}
                onChange={(e) => setReinforcement({ spacingY: Number(e.target.value) || 0.01 })}
              />
              <div className="input-unit">m</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Steel area
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="0.000001"
                step="0.000001"
                value={reinforcement.steelArea}
                onChange={(e) => setReinforcement({ steelArea: Number(e.target.value) || 0.000001 })}
              />
              <div className="input-unit">m2</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Yield strength
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="0.01"
                step="1"
                value={reinforcement.yieldStrength}
                onChange={(e) => setReinforcement({ yieldStrength: Number(e.target.value) || 0.01 })}
              />
              <div className="input-unit">kN/m2</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Bond strength
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="0.01"
                step="1"
                value={reinforcement.bondStrength}
                onChange={(e) => setReinforcement({ bondStrength: Number(e.target.value) || 0.01 })}
              />
              <div className="input-unit">kN/m2</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label" title="Used in simplified uniform column-based model.">
              Inclination
            </div>
            <div className="input-wrapper">
              <input
                type="number"
                min="-90"
                max="90"
                step="0.1"
                value={reinforcement.inclinationDeg}
                onChange={(e) => setReinforcement({ inclinationDeg: Number(e.target.value) || 0 })}
              />
              <div className="input-unit">deg</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label">Vertical comp.</div>
            <input
              type="checkbox"
              checked={reinforcement.includeVerticalComponent}
              onChange={(e) => setReinforcement({ includeVerticalComponent: e.target.checked })}
            />
          </div>
        </>
      )}
      <div className="results-comparison-meta">
        Visualizer is deferred in MVP. Diagnostics and payload views are primary.
      </div>
    </div>
  )
}

