function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v))
}

export function scalarToHeatColor(value, min, max) {
  if (!Number.isFinite(value) || !Number.isFinite(min) || !Number.isFinite(max) || max <= min) return '#777777'
  const t = clamp((value - min) / (max - min), 0, 1)
  const r = Math.round(255 * t)
  const g = Math.round(180 * (1 - Math.abs(t - 0.5) * 2))
  const b = Math.round(255 * (1 - t))
  return `rgb(${r},${g},${b})`
}

