import { useSettingsStore } from '../../store/settingsStore.js'

export default function SettingsPanel() {
  const { numSlices, numIterations, tolerance, setNumSlices, setNumIterations, setTolerance } =
    useSettingsStore()

  return (
    <div className="prop-group">
      <div className="prop-group-title">Analysis settings</div>

      <div className="input-row">
        <div className="input-label">Number of slices</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="10"
            step="1"
            value={numSlices}
            onChange={(e) => setNumSlices(Number(e.target.value) || 10)}
          />
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Iterations</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="100"
            step="100"
            value={numIterations}
            onChange={(e) => setNumIterations(Number(e.target.value) || 100)}
          />
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Tolerance</div>
        <div className="input-wrapper">
          <input
            type="number"
            step="0.0001"
            value={tolerance}
            onChange={(e) => setTolerance(Number(e.target.value) || 0.001)}
          />
        </div>
      </div>
    </div>
  )
}

