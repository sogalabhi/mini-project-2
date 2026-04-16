import { Link } from 'react-router-dom'
import { useAnalysis3d } from '../../hooks/useAnalysis3d.js'
import { useUi3dStore } from '../../store/ui3dStore.js'
import { useForm3dStore } from '../../store/form3dStore.js'
import { useValidation3dStore } from '../../store/validation3dStore.js'
import Summary3DPanel from '../results3d/Summary3DPanel.jsx'
import Comparison3DPanel from '../results3d/Comparison3DPanel.jsx'
import Diagnostics3DPanel from '../results3d/Diagnostics3DPanel.jsx'
import PayloadPreview3DPanel from '../results3d/PayloadPreview3DPanel.jsx'
import Preview3DPanel from '../results3d/Preview3DPanel.jsx'
import TabPanel3D from './TabPanel3D.jsx'

const OUT_TABS = [
  { id: 'summary', label: 'Summary' },
  { id: 'preview', label: 'Preview' },
  { id: 'comparison', label: 'Comparison' },
  { id: 'diagnostics', label: 'Diagnostics' },
  { id: 'payload', label: 'Payload' },
]

export default function AppShell3D() {
  const { validate, runSingle, runMulti, isRunning, isValidating, canRun } = useAnalysis3d()
  const activeOutputTab = useUi3dStore((s) => s.activeOutputTab)
  const setActiveOutputTab = useUi3dStore((s) => s.setActiveOutputTab)
  const comparisonMode = useForm3dStore((s) => s.methodConfig.comparisonMode)
  const serverErrors = useValidation3dStore((s) => s.serverErrors)

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="branding">
          <span>3D Slope Analysis</span>
          <Link to="/" className="mode-link">
            Switch to 2D
          </Link>
        </div>
        <div className="header-actions">
          <button type="button" className="action-btn" onClick={validate} disabled={isValidating}>
            {isValidating ? 'Validating…' : 'Validate 3D Input'}
          </button>
          {comparisonMode ? (
            <button type="button" className="run-btn" onClick={runMulti} disabled={!canRun || isRunning}>
              {isRunning ? 'Running…' : 'Run Multi-Method'}
            </button>
          ) : (
            <button type="button" className="run-btn" onClick={runSingle} disabled={!canRun || isRunning}>
              {isRunning ? 'Running…' : 'Run 3D Analysis'}
            </button>
          )}
        </div>
      </header>
      <div className="main-workspace">
        <div className="left-column">
          <div className="viewer-tabs-wrapper">
            <div className="viewer-tabs-header">
              {OUT_TABS.map((tab) => (
                <button
                  type="button"
                  key={tab.id}
                  className={`viewer-tab${activeOutputTab === tab.id ? ' active' : ''}`}
                  onClick={() => setActiveOutputTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <div className="canvas-container three-d-results">
              {activeOutputTab === 'summary' && <Summary3DPanel />}
              {activeOutputTab === 'preview' && <Preview3DPanel />}
              {activeOutputTab === 'comparison' && <Comparison3DPanel />}
              {activeOutputTab === 'diagnostics' && <Diagnostics3DPanel />}
              {activeOutputTab === 'payload' && <PayloadPreview3DPanel />}
              {serverErrors?.length > 0 && (
                <div className="error-banner">{serverErrors.join(' | ')}</div>
              )}
            </div>
          </div>
        </div>
        <div className="right-column">
          <TabPanel3D />
        </div>
      </div>
    </div>
  )
}

