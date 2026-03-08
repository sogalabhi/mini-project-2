import { useResultsStore } from '../../store/resultsStore.js'

export default function DiagramViewer() {
  const latest = useResultsStore((s) => s.latest)

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#fff',
      }}
    >
      {latest?.imageUrl ? (
        <img
          src={latest.imageUrl}
          alt="Slope analysis diagram"
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
          }}
        />
      ) : (
        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
          No diagram yet
        </span>
      )}
    </div>
  )
}

