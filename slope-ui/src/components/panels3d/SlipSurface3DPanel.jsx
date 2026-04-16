import { useForm3dStore } from '../../store/form3dStore.js'

export default function SlipSurface3DPanel() {
  const slip = useForm3dStore((s) => s.slipSurfaceConfig)
  const setSlip = useForm3dStore((s) => s.setSlipSurfaceConfig)

  return (
    <div className="prop-group">
      <div className="prop-group-title">Slip surface</div>
      <div className="input-row">
        <div className="input-label">Mode</div>
        <select value={slip.mode} onChange={(e) => setSlip({ mode: e.target.value })}>
          <option value="ellipsoid">ellipsoid</option>
          <option value="user_defined">user_defined</option>
        </select>
      </div>

      {slip.mode === 'ellipsoid' ? (
        <>
          {['Xc', 'Yc', 'Zc'].map((label, idx) => (
            <div className="input-row" key={label}>
              <div className="input-label">{label}</div>
              <div className="input-wrapper">
                <input
                  type="number"
                  step="0.1"
                  value={slip.ellipsoidCenter[idx]}
                  onChange={(e) => {
                    const arr = [...slip.ellipsoidCenter]
                    arr[idx] = Number(e.target.value) || 0
                    setSlip({ ellipsoidCenter: arr })
                  }}
                />
                <div className="input-unit">m</div>
              </div>
            </div>
          ))}
          {['Rx', 'Ry', 'Rz'].map((label, idx) => (
            <div className="input-row" key={label}>
              <div className="input-label">{label}</div>
              <div className="input-wrapper">
                <input
                  type="number"
                  step="0.1"
                  min="0.01"
                  value={slip.ellipsoidRadii[idx]}
                  onChange={(e) => {
                    const arr = [...slip.ellipsoidRadii]
                    arr[idx] = Number(e.target.value) || 0.01
                    setSlip({ ellipsoidRadii: arr })
                  }}
                />
                <div className="input-unit">m</div>
              </div>
            </div>
          ))}
        </>
      ) : (
        <>
          <div className="input-row">
            <div className="input-label">Surface Path</div>
            <div className="input-wrapper">
              <input
                type="text"
                value={slip.userDefinedSurfacePath}
                onChange={(e) => setSlip({ userDefinedSurfacePath: e.target.value })}
              />
              <div className="input-unit">path</div>
            </div>
          </div>
          <div className="input-row">
            <div className="input-label">Interpolation</div>
            <div className="input-wrapper">
              <input
                type="text"
                value={slip.userDefinedInterpolation}
                onChange={(e) => setSlip({ userDefinedInterpolation: e.target.value })}
              />
              <div className="input-unit">mode</div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

