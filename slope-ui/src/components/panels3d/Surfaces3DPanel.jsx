import { useForm3dStore } from '../../store/form3dStore.js'

export default function Surfaces3DPanel() {
  const top = useForm3dStore((s) => s.surfaces.topSurface)
  const setTopSurfaceMeta = useForm3dStore((s) => s.setTopSurfaceMeta)
  const addPoint = useForm3dStore((s) => s.addTopSurfacePoint)
  const updatePoint = useForm3dStore((s) => s.updateTopSurfacePoint)
  const removePoint = useForm3dStore((s) => s.removeTopSurfacePoint)
  const useDemoSurface = useForm3dStore((s) => s.useDemoSurface)

  return (
    <div className="prop-group">
      <div className="prop-group-title">Top surface metadata</div>
      <div className="input-row">
        <div className="input-label">Label</div>
        <div className="input-wrapper">
          <input type="text" value={top.label} onChange={(e) => setTopSurfaceMeta({ label: e.target.value })} />
          <div className="input-unit">id</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Path</div>
        <div className="input-wrapper">
          <input type="text" value={top.path} onChange={(e) => setTopSurfaceMeta({ path: e.target.value })} />
          <div className="input-unit">path</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Interp</div>
        <div className="input-wrapper">
          <input
            type="text"
            value={top.interpolationMode}
            onChange={(e) => setTopSurfaceMeta({ interpolationMode: e.target.value })}
          />
          <div className="input-unit">mode</div>
        </div>
      </div>

      <div className="table-action-row">
        <button type="button" className="action-btn" onClick={addPoint}>
          Add point
        </button>
        <button type="button" className="action-btn" onClick={useDemoSurface}>
          Use demo surface
        </button>
      </div>
      <div className="results-comparison-meta">CSV upload is deferred in MVP.</div>

      <table className="data-table">
        <thead>
          <tr>
            <th>X</th>
            <th>Y</th>
            <th>Z</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {top.points.map((pt, i) => (
            <tr key={`${pt.x}-${pt.y}-${i}`}>
              <td>
                <input type="number" value={pt.x} onChange={(e) => updatePoint(i, { x: Number(e.target.value) || 0 })} />
              </td>
              <td>
                <input type="number" value={pt.y} onChange={(e) => updatePoint(i, { y: Number(e.target.value) || 0 })} />
              </td>
              <td>
                <input type="number" value={pt.z} onChange={(e) => updatePoint(i, { z: Number(e.target.value) || 0 })} />
              </td>
              <td>
                <button type="button" className="action-btn" onClick={() => removePoint(i)}>
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

