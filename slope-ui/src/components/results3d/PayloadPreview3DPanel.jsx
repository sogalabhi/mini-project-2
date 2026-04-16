import { useResults3dStore } from '../../store/results3dStore.js'

export default function PayloadPreview3DPanel() {
  const payload = useResults3dStore((s) => s.lastPayload)
  const reinforcementEnabled = Boolean(payload?.reinforcement?.enabled)
  return (
    <div className="results-details">
      <div className="results-comparison-title">Payload preview</div>
      {reinforcementEnabled && (
        <div className="results-comparison-meta">
          reinforcement model mode: <code>phase2_simplified</code> (Simplified phase-2 uniform column-based
          reinforcement approximation.)
        </div>
      )}
      <pre className="json-preview">{payload ? JSON.stringify(payload, null, 2) : 'No payload sent yet.'}</pre>
    </div>
  )
}

