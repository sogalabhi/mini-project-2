import Method3DPanel from '../panels3d/Method3DPanel.jsx'
import Grid3DPanel from '../panels3d/Grid3DPanel.jsx'
import SlipSurface3DPanel from '../panels3d/SlipSurface3DPanel.jsx'
import Surfaces3DPanel from '../panels3d/Surfaces3DPanel.jsx'
import Materials3DPanel from '../panels3d/Materials3DPanel.jsx'
import Hydro3DPanel from '../panels3d/Hydro3DPanel.jsx'
import Advanced3DPanel from '../panels3d/Advanced3DPanel.jsx'
import { useUi3dStore } from '../../store/ui3dStore.js'
import { useValidation3dStore } from '../../store/validation3dStore.js'

const TABS = [
  { id: 'method', label: 'Method' },
  { id: 'grid', label: 'Grid' },
  { id: 'slip', label: 'Slip Surface' },
  { id: 'surfaces', label: 'Surfaces' },
  { id: 'materials', label: 'Materials' },
  { id: 'hydro', label: 'Hydro' },
  { id: 'advanced', label: 'Advanced' },
]

export default function TabPanel3D() {
  const active = useUi3dStore((s) => s.activeInputTab)
  const setActive = useUi3dStore((s) => s.setActiveInputTab)
  const tabErrors = useValidation3dStore((s) => s.tabErrors)

  return (
    <div className="flex h-full flex-col">
      <div className="tabs-header">
        {TABS.map((tab) => {
          const isActive = active === tab.id
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActive(tab.id)}
              className={`tab${isActive ? ' active' : ''}${tabErrors[tab.id] ? ' tab-error' : ''}`}
            >
              {tab.label}
            </button>
          )
        })}
      </div>
      <div className="tab-content">
        {active === 'method' && <Method3DPanel />}
        {active === 'grid' && <Grid3DPanel />}
        {active === 'slip' && <SlipSurface3DPanel />}
        {active === 'surfaces' && <Surfaces3DPanel />}
        {active === 'materials' && <Materials3DPanel />}
        {active === 'hydro' && <Hydro3DPanel />}
        {active === 'advanced' && <Advanced3DPanel />}
      </div>
    </div>
  )
}

