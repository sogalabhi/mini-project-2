import { useState } from 'react'
import GeometryPanel from '../panels/GeometryPanel.jsx'
import MaterialsPanel from '../panels/MaterialsPanel.jsx'
import LoadsPanel from '../panels/LoadsPanel.jsx'
import WaterPanel from '../panels/WaterPanel.jsx'
import SettingsPanel from '../panels/SettingsPanel.jsx'
import ReinforcementPanel from '../panels/ReinforcementPanel.jsx'

const TABS = [
  { id: 'geometry', label: 'Geometry' },
  { id: 'materials', label: 'Materials' },
  { id: 'loads', label: 'Loads' },
  { id: 'water', label: 'Water' },
  { id: 'settings', label: 'Settings' },
  { id: 'reinforcement', label: 'Results' },
]

export default function TabPanel() {
  const [active, setActive] = useState('geometry')

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
              className={`tab${isActive ? ' active' : ''}`}
            >
              {tab.label}
            </button>
          )
        })}
      </div>

      <div className="tab-content">
        {active === 'geometry' && <GeometryPanel />}
        {active === 'materials' && <MaterialsPanel />}
        {active === 'loads' && <LoadsPanel />}
        {active === 'water' && <WaterPanel />}
        {active === 'settings' && <SettingsPanel />}
        {active === 'reinforcement' && <ReinforcementPanel />}
      </div>
    </div>
  )
}

