import { useResultsStore } from '../../store/resultsStore.js'

export default function ResultsPanel({ isLoading, error }) {
  const latest = useResultsStore((s) => s.latest)
  const fos = latest?.factorOfSafety ?? null

  let badgeColor = 'var(--status-green)'
  if (fos != null) {
    if (fos < 1.0) badgeColor = 'var(--status-red)'
    else if (fos < 1.25) badgeColor = 'var(--status-orange)'
    else if (fos < 1.5) badgeColor = 'var(--status-orange)'
    else badgeColor = 'var(--status-green)'
  }

  return (
    <div className="fos-display">
      <div className="fos-label">Factor of safety</div>
      <div className="fos-value">
        {fos != null ? fos.toFixed(3) : '--'}
      </div>
      <div
        className="status-badge"
        style={{ color: badgeColor, borderColor: badgeColor }}
      >
        {latest?.status || 'Not analyzed yet'}
      </div>
      {isLoading && (
        <div style={{ marginTop: 8, fontSize: 10 }}>Analyzing…</div>
      )}
      {error && (
        <div style={{ marginTop: 8, fontSize: 10, color: 'var(--status-red)' }}>
          Failed: {error.message}
        </div>
      )}
    </div>
  )
}

