import { useResults3dStore } from '../../store/results3dStore.js'

export default function PayloadPreview3DPanel() {
  const payload = useResults3dStore((s) => s.lastPayload)
  return (
    <div className="results-details">
      <div className="results-comparison-title">Payload preview</div>
      <pre className="json-preview">{payload ? JSON.stringify(payload, null, 2) : 'No payload sent yet.'}</pre>
    </div>
  )
}

