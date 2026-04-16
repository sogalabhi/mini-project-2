import { useForm3dStore } from '../../store/form3dStore.js'

function MaterialParamFields({ material, updateParams }) {
  if (material.modelType === 1) {
    return (
      <>
        <td>
          <input
            type="number"
            value={material.params.phi ?? 30}
            onChange={(e) => updateParams({ phi: Number(e.target.value) || 0 })}
          />
        </td>
        <td>
          <input
            type="number"
            value={material.params.cohesion ?? 5}
            onChange={(e) => updateParams({ cohesion: Number(e.target.value) || 0 })}
          />
        </td>
      </>
    )
  }

  return (
    <>
      <td>
        <input
          type="number"
          value={material.params.suTop ?? 40}
          onChange={(e) => updateParams({ suTop: Number(e.target.value) || 0 })}
        />
      </td>
      <td>
        <input
          type="number"
          value={material.params.diffSu ?? 10}
          onChange={(e) => updateParams({ diffSu: Number(e.target.value) || 0 })}
        />
      </td>
    </>
  )
}

export default function Materials3DPanel() {
  const materials = useForm3dStore((s) => s.materials)
  const addMaterial = useForm3dStore((s) => s.addMaterial)
  const removeMaterial = useForm3dStore((s) => s.removeMaterial)
  const updateMaterial = useForm3dStore((s) => s.updateMaterial)
  const updateParams = useForm3dStore((s) => s.updateMaterialParams)

  return (
    <div className="prop-group">
      <div className="prop-group-title">Materials</div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>γ</th>
            <th>P1</th>
            <th>P2</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {materials.map((m) => (
            <tr key={m.key}>
              <td>
                <input type="text" value={m.name} onChange={(e) => updateMaterial(m.key, { name: e.target.value })} />
              </td>
              <td>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={m.modelType}
                  onChange={(e) => updateMaterial(m.key, { modelType: Number(e.target.value) || 1 })}
                />
              </td>
              <td>
                <input
                  type="number"
                  value={m.unitWeight}
                  onChange={(e) => updateMaterial(m.key, { unitWeight: Number(e.target.value) || 0 })}
                />
              </td>
              <MaterialParamFields material={m} updateParams={(patch) => updateParams(m.key, patch)} />
              <td>
                <button type="button" className="action-btn" onClick={() => removeMaterial(m.key)}>
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button type="button" className="action-btn" onClick={addMaterial}>
        Add material
      </button>
    </div>
  )
}

