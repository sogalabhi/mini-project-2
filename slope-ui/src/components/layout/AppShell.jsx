import { useState } from 'react'
import SlopeCanvas from '../canvas/SlopeCanvas.jsx'
import TabPanel from './TabPanel.jsx'
import ResultsPanel from '../results/ResultsPanel.jsx'
import ComparisonPanel from '../results/ComparisonPanel.jsx'
import DiagramViewer from '../results/DiagramViewer.jsx'
import { useAnalysis } from '../../hooks/useAnalysis.js'
import { useResultsStore } from '../../store/resultsStore.js'

function Header({ onRun, isLoading }) {
  return (
    <header className="app-header">
      <div className="branding">
        <span>Slope Stability Analyzer</span>
      </div>
      <button
        type="button"
        onClick={onRun}
        disabled={isLoading}
        className="run-btn"
      >
        {isLoading ? 'Analyzing…' : 'Run Analysis'}
      </button>
    </header>
  )
}

function ViewerTabs() {
  const [active, setActive] = useState('visualizer')
  const hasImage = !!useResultsStore((s) => s.latest?.imageUrl)

  return (
    <div className="viewer-tabs-wrapper">
      <div className="viewer-tabs-header">
        <button
          type="button"
          className={`viewer-tab${active === 'visualizer' ? ' active' : ''}`}
          onClick={() => setActive('visualizer')}
        >
          Visualizer
        </button>
        <button
          type="button"
          className={`viewer-tab${active === 'image' ? ' active' : ''}${!hasImage ? ' disabled' : ''}`}
          onClick={() => hasImage && setActive('image')}
          disabled={!hasImage}
        >
          Image
        </button>
      </div>
      <div className="canvas-container">
        {active === 'visualizer' && <SlopeCanvas />}
        {active === 'image' && <DiagramViewer />}
      </div>
    </div>
  )
}

export default function AppShell() {
  const { mutate: runAnalysis, isPending, error } = useAnalysis()

  return (
    <div className="app-root">
      <Header onRun={runAnalysis} isLoading={isPending} />

      <div className="main-workspace">
        <div className="left-column">
          <ViewerTabs />

          <div className="results-panel">
            <ResultsPanel isLoading={isPending} error={error} />
            <div className="results-details">
              <ComparisonPanel />
            </div>
          </div>
        </div>

        <div className="right-column">
          <TabPanel />
        </div>
      </div>
    </div>
  )
}

