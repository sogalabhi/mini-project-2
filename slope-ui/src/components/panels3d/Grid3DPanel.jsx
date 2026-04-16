import { useForm3dStore } from '../../store/form3dStore.js'

export default function Grid3DPanel() {
  const grid = useForm3dStore((s) => s.gridConfig)
  const setGridConfig = useForm3dStore((s) => s.setGridConfig)
  const projectedRows = grid.colXMax * grid.colYMax

  const row = (label, key, unit = '-') => (
    <div className="input-row">
      <div className="input-label">{label}</div>
      <div className="input-wrapper">
        <input
          type="number"
          step="0.1"
          value={grid[key]}
          onChange={(e) => setGridConfig({ [key]: Number(e.target.value) || 0 })}
        />
        <div className="input-unit">{unit}</div>
      </div>
    </div>
  )

  return (
    <div className="prop-group">
      <div className="prop-group-title">Grid bounds</div>
      {row('X min', 'xMin', 'm')}
      {row('X max', 'xMax', 'm')}
      {row('Y min', 'yMin', 'm')}
      {row('Y max', 'yMax', 'm')}
      {row('Z min', 'zMin', 'm')}
      {row('Z max', 'zMax', 'm')}
      <div className="prop-group-title">Grid density</div>
      {row('Cols X', 'colXMax', 'n')}
      {row('Cols Y', 'colYMax', 'n')}
      <div className="results-comparison-meta">Projected rows: {projectedRows}</div>
    </div>
  )
}

