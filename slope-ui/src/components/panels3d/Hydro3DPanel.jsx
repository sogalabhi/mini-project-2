import { useForm3dStore } from '../../store/form3dStore.js'

export default function Hydro3DPanel() {
  const hydro = useForm3dStore((s) => s.hydro)
  const setHydro = useForm3dStore((s) => s.setHydro)

  return (
    <div className="prop-group">
      <div className="prop-group-title">Hydro</div>
      <div className="input-row">
        <div className="input-label">Water level z</div>
        <div className="input-wrapper">
          <input
            type="number"
            value={hydro.waterLevelZ ?? ''}
            onChange={(e) =>
              setHydro({
                waterLevelZ: e.target.value === '' ? null : Number(e.target.value),
              })
            }
          />
          <div className="input-unit">m</div>
        </div>
      </div>
    </div>
  )
}

