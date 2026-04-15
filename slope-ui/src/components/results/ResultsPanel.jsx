import { useResultsStore } from '../../store/resultsStore.js'

export default function ResultsPanel({ isLoading, error, showReinforcement = false }) {
  const latest = useResultsStore((s) => s.latest)
  const fos = latest?.factorOfSafety ?? null
  const reinforcement = latest?.reinforcement ?? null

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
      {showReinforcement && reinforcement?.enabled && (
        <div
          style={{
            marginTop: 10,
            paddingTop: 8,
            borderTop: '1px solid rgba(255,255,255,0.08)',
            fontSize: 11,
            lineHeight: 1.4,
          }}
        >
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Reinforcement design</div>
          {reinforcement.required ? (
            <>
              <div style={{ color: 'var(--status-red)', marginBottom: 4 }}>
                Slope Unstable. Recommended Design:
              </div>
              <div>
                Use 12mm diameter soil nails, 6.5m long, spaced at 1.4m horizontal and 1.4m
                vertical intervals.
              </div>
              <div style={{ marginTop: 6, color: 'var(--status-green)', fontWeight: 600 }}>
                We achieved target FOS 1.5 after this reinforcement.
              </div>
              <div style={{ marginTop: 6 }}>
                Calculation:
                <br />
                1) FOS improvement basis: FOSnew = FOScurrent + (DeltaR / D)
                <br />
                2) Required added resistance: DeltaR = (targetFOS - currentFOS) * D
                <br />
                3) Steel sizing: As = Tdesign / (0.55 * fy)
                <br />
                {reinforcement.design_tension_per_nail_kn != null &&
                reinforcement.steel_yield_strength_mpa != null &&
                reinforcement.as_required_mm2 != null
                  ? `   => As = ${reinforcement.design_tension_per_nail_kn} x 1000 / (0.55 x ${reinforcement.steel_yield_strength_mpa}) = ${reinforcement.as_required_mm2} mm²`
                  : '   => As computed from Tdesign and fy'}
                <br />
                4) Provide practical bar and layout: 12mm nails, L = 6.5m, Sh = 1.4m, Sv = 1.4m.
              </div>
            </>
          ) : (
            <div style={{ color: 'var(--status-green)' }}>
              {reinforcement.message || 'No reinforcement required.'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

