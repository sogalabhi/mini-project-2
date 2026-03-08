import { useWaterStore } from '../../store/waterStore.js'

export default function WaterPanel() {
  const { enabled, depth, unitWeight, setEnabled, setDepth, setUnitWeight } =
    useWaterStore()

  return (
    <div className="prop-group">
      <div className="prop-group-title">Water table</div>

      <div className="input-row">
        <div className="input-label">Enabled</div>
        <div className="input-wrapper" style={{ border: 'none', background: 'transparent' }}>
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
          />
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Depth</div>
        <div className="input-wrapper">
          <input
            type="number"
            step="0.5"
            value={depth}
            disabled={!enabled}
            onChange={(e) => setDepth(Number(e.target.value) || 0)}
          />
          <div className="input-unit">m</div>
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Unit weight</div>
        <div className="input-wrapper">
          <input
            type="number"
            step="0.1"
            value={unitWeight}
            disabled={!enabled}
            onChange={(e) => setUnitWeight(Number(e.target.value) || 0)}
          />
          <div className="input-unit">kN/m³</div>
        </div>
      </div>
    </div>
  )
}

