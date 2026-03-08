import { useMaterialsStore } from '../../store/materialsStore.js'

export default function MaterialsPanel() {
  const { layers, addLayer, updateLayer, removeLayer } = useMaterialsStore()

  return (
    <div className="prop-group">
      <div className="prop-group-title">Soil profile</div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>γ (kN/m³)</th>
            <th>φ (°)</th>
            <th>c (kPa)</th>
            <th>Depth (m)</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {layers.map((layer) => (
            <tr key={layer.id}>
              <td>
                <input
                  type="text"
                  value={layer.name}
                  onChange={(e) =>
                    updateLayer(layer.id, { name: e.target.value })
                  }
                />
              </td>
              <td>
                <input
                  type="number"
                  step="0.1"
                  value={layer.unitWeight}
                  onChange={(e) =>
                    updateLayer(layer.id, {
                      unitWeight: Number(e.target.value) || 0,
                    })
                  }
                />
              </td>
              <td>
                <input
                  type="number"
                  step="0.5"
                  value={layer.frictionAngle}
                  onChange={(e) =>
                    updateLayer(layer.id, {
                      frictionAngle: Number(e.target.value) || 0,
                    })
                  }
                />
              </td>
              <td>
                <input
                  type="number"
                  step="0.5"
                  value={layer.cohesion}
                  onChange={(e) =>
                    updateLayer(layer.id, {
                      cohesion: Number(e.target.value) || 0,
                    })
                  }
                />
              </td>
              <td>
                <input
                  type="number"
                  step="0.5"
                  value={layer.depthToBottom ?? ''}
                  onChange={(e) =>
                    updateLayer(layer.id, {
                      depthToBottom: e.target.value
                        ? Number(e.target.value)
                        : null,
                    })
                  }
                />
              </td>
              <td>
                <button
                  type="button"
                  onClick={() => removeLayer(layer.id)}
                  className="action-btn"
                >
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="table-action-row">
        <button
          type="button"
          onClick={addLayer}
          className="action-btn"
        >
          Add layer
        </button>
      </div>
    </div>
  )
}

