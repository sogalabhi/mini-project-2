import { useGeometryStore } from '../../store/geometryStore.js'

export default function GeometryPanel() {
  const { height, angle, length, setHeight, setAngle, setLength } =
    useGeometryStore()

  return (
    <div className="prop-group">
      <div className="prop-group-title">Slope geometry</div>

      <div className="input-row">
        <div className="input-label">Height</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={height ?? ''}
            onChange={(e) => setHeight(Number(e.target.value) || 0)}
          />
          <div className="input-unit">m</div>
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Angle</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="1"
            max="89"
            step="0.5"
            value={angle ?? ''}
            onChange={(e) => setAngle(Number(e.target.value) || 0)}
          />
          <div className="input-unit">°</div>
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Length</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={length ?? ''}
            onChange={(e) =>
              setLength(e.target.value ? Number(e.target.value) : null)
            }
          />
          <div className="input-unit">m</div>
        </div>
      </div>
    </div>
  )
}

