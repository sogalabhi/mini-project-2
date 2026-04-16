import { useForm3dStore } from '../../store/form3dStore.js'

const ALL_METHODS = [1, 2, 3, 4, 5, 6, 7]

export default function Method3DPanel() {
  const methodConfig = useForm3dStore((s) => s.methodConfig)
  const setMethodConfig = useForm3dStore((s) => s.setMethodConfig)
  const setMethodSolver = useForm3dStore((s) => s.setMethodSolver)
  const setMethodDirection = useForm3dStore((s) => s.setMethodDirection)

  return (
    <div className="prop-group">
      <div className="prop-group-title">3D method</div>
      <div className="input-row">
        <div className="input-label">Method ID</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="1"
            max="7"
            value={methodConfig.methodId}
            onChange={(e) => setMethodConfig({ methodId: Number(e.target.value) || 1 })}
          />
          <div className="input-unit">id</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Comparison</div>
        <input
          type="checkbox"
          checked={methodConfig.comparisonMode}
          onChange={(e) => setMethodConfig({ comparisonMode: e.target.checked })}
        />
      </div>

      {methodConfig.comparisonMode && (
        <div className="method-chip-row">
          {ALL_METHODS.map((id) => {
            const checked = methodConfig.comparisonMethodIds.includes(id)
            return (
              <label key={id} className="method-chip">
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={(e) => {
                    const prev = methodConfig.comparisonMethodIds
                    const next = e.target.checked ? [...new Set([...prev, id])] : prev.filter((v) => v !== id)
                    setMethodConfig({ comparisonMethodIds: next.length ? next : [methodConfig.methodId] })
                  }}
                />
                M{id}
              </label>
            )
          })}
        </div>
      )}

      <div className="prop-group-title">Solver</div>
      <div className="input-row">
        <div className="input-label">Iterations</div>
        <div className="input-wrapper">
          <input
            type="number"
            value={methodConfig.solver.maxIterations}
            onChange={(e) => setMethodSolver({ maxIterations: Number(e.target.value) || 1 })}
          />
          <div className="input-unit">n</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Tol FS</div>
        <div className="input-wrapper">
          <input
            type="number"
            step="0.0001"
            value={methodConfig.solver.tolFs}
            onChange={(e) => setMethodSolver({ tolFs: Number(e.target.value) || 0.0001 })}
          />
          <div className="input-unit">-</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Damping</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="0.01"
            max="1"
            step="0.01"
            value={methodConfig.solver.damping}
            onChange={(e) => setMethodSolver({ damping: Number(e.target.value) || 1 })}
          />
          <div className="input-unit">-</div>
        </div>
      </div>
      <div className="prop-group-title">Direction</div>
      <div className="input-row">
        <div className="input-label">Spacing</div>
        <div className="input-wrapper">
          <input
            type="number"
            step="0.1"
            value={methodConfig.direction.spacingDeg}
            onChange={(e) => setMethodDirection({ spacingDeg: Number(e.target.value) || 0.1 })}
          />
          <div className="input-unit">deg</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">Tolerance</div>
        <div className="input-wrapper">
          <input
            type="number"
            step="0.1"
            value={methodConfig.direction.toleranceDeg}
            onChange={(e) => setMethodDirection({ toleranceDeg: Number(e.target.value) || 0 })}
          />
          <div className="input-unit">deg</div>
        </div>
      </div>
      <div className="input-row">
        <div className="input-label">User Dir</div>
        <div className="input-wrapper">
          <input
            type="number"
            step="0.1"
            value={methodConfig.direction.userDirectionDeg ?? ''}
            onChange={(e) =>
              setMethodDirection({
                userDirectionDeg: e.target.value === '' ? null : Number(e.target.value),
              })
            }
          />
          <div className="input-unit">deg</div>
        </div>
      </div>
    </div>
  )
}

