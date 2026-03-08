import { useLoadsStore } from '../../store/loadsStore.js'

export default function LoadsPanel() {
  const {
    udls,
    lineLoads,
    addUdl,
    updateUdl,
    removeUdl,
    addLineLoad,
    updateLineLoad,
    removeLineLoad,
  } = useLoadsStore()

  return (
    <div className="prop-group">
      <div className="prop-group-title">External loads</div>

      <div style={{ marginBottom: '10px' }}>
        <div className="prop-group-title" style={{ borderBottom: 'none' }}>
          Uniform distributed loads (kPa)
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Magnitude</th>
              <th>Offset (m)</th>
              <th>Length (m)</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {udls.map((load) => (
              <tr key={load.id}>
                <td>
                  <input
                    type="number"
                    step="0.5"
                    value={load.magnitude}
                    onChange={(e) =>
                      updateUdl(load.id, {
                        magnitude: Number(e.target.value) || 0,
                      })
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step="0.5"
                    value={load.offset}
                    onChange={(e) =>
                      updateUdl(load.id, {
                        offset: Number(e.target.value) || 0,
                      })
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step="0.5"
                    value={load.length}
                    onChange={(e) =>
                      updateUdl(load.id, {
                        length: Number(e.target.value) || 0,
                      })
                    }
                  />
                </td>
                <td>
                  <button
                    type="button"
                    onClick={() => removeUdl(load.id)}
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
            onClick={addUdl}
            className="action-btn"
          >
            Add UDL
          </button>
        </div>
      </div>

      <div>
        <div className="prop-group-title" style={{ borderBottom: 'none' }}>
          Line loads (kN/m)
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Magnitude</th>
              <th>Offset (m)</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {lineLoads.map((load) => (
              <tr key={load.id}>
                <td>
                  <input
                    type="number"
                    step="0.5"
                    value={load.magnitude}
                    onChange={(e) =>
                      updateLineLoad(load.id, {
                        magnitude: Number(e.target.value) || 0,
                      })
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step="0.5"
                    value={load.offset}
                    onChange={(e) =>
                      updateLineLoad(load.id, {
                        offset: Number(e.target.value) || 0,
                      })
                    }
                  />
                </td>
                <td>
                  <button
                    type="button"
                    onClick={() => removeLineLoad(load.id)}
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
            onClick={addLineLoad}
            className="action-btn"
          >
            Add line load
          </button>
        </div>
      </div>
    </div>
  )
}

