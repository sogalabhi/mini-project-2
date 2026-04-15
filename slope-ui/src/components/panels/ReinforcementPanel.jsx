import { useReinforcementStore } from '../../store/reinforcementStore.js'

export default function ReinforcementPanel() {
  const {
    enabled,
    targetFos,
    steelYieldStrength,
    soilGroutBondFriction,
    setEnabled,
    setTargetFos,
    setSteelYieldStrength,
    setSoilGroutBondFriction,
  } = useReinforcementStore()

  return (
    <div className="prop-group">
      <div className="prop-group-title">Reinforcement parameters</div>

      <div className="input-row">
        <div className="input-label">Enable design</div>
        <div className="input-wrapper" style={{ border: 'none', background: 'transparent' }}>
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
          />
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Target FOS</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="1.01"
            step="0.05"
            value={targetFos}
            disabled={!enabled}
            onChange={(e) => setTargetFos(Number(e.target.value) || 1.5)}
          />
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Steel yield strength</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="1"
            step="5"
            value={steelYieldStrength}
            disabled={!enabled}
            onChange={(e) => setSteelYieldStrength(Number(e.target.value) || 415)}
          />
          <div className="input-unit">MPa</div>
        </div>
      </div>

      <div className="input-row">
        <div className="input-label">Soil-grout bond friction</div>
        <div className="input-wrapper">
          <input
            type="number"
            min="1"
            step="5"
            value={soilGroutBondFriction}
            disabled={!enabled}
            onChange={(e) => setSoilGroutBondFriction(Number(e.target.value) || 100)}
          />
          <div className="input-unit">kPa</div>
        </div>
      </div>
    </div>
  )
}
