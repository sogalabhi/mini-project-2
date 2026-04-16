import { useMemo, useState } from 'react'
import { useForm3dStore } from '../../store/form3dStore.js'
import { useResults3dStore } from '../../store/results3dStore.js'
import { useUi3dStore } from '../../store/ui3dStore.js'
import { buildRender3dModel } from '../../utils/render3dAdapter.js'
import Scene3DCanvas from './Scene3DCanvas.jsx'
import SceneControls3D from './SceneControls3D.jsx'

export default function Preview3DPanel() {
  const formState = useForm3dStore((s) => s)
  const reinforcementEnabled = useForm3dStore((s) => s.reinforcement.enabled)
  const resultState = useResults3dStore((s) => s)
  const selectedColumnId = useUi3dStore((s) => s.selectedColumnId)
  const [cameraResetToken, setCameraResetToken] = useState(0)
  const [controls, setControls] = useState({
    showSurface: true,
    showSlip: true,
    showGrid: true,
    showAxes: true,
    pointSize: 0.06,
    overlayMode: 'none',
  })

  const model = useMemo(() => {
    if (resultState.lastPayload) {
      return buildRender3dModel({
        payload: resultState.lastPayload,
        fallbackFormState: null,
        result: resultState.latestSingle,
      })
    }
    return buildRender3dModel({
      payload: null,
      fallbackFormState: formState,
      result: resultState.latestSingle,
    })
  }, [resultState.lastPayload, resultState.latestSingle, formState])

  return (
    <div className="preview3d-layout">
      <SceneControls3D
        controls={controls}
        onToggle={(key) => setControls((s) => ({ ...s, [key]: !s[key] }))}
        onPointSize={(pointSize) => setControls((s) => ({ ...s, pointSize }))}
        onOverlayMode={(overlayMode) => setControls((s) => ({ ...s, overlayMode }))}
        onResetCamera={() => setCameraResetToken((v) => v + 1)}
        selectedColumnId={selectedColumnId}
        reinforcementEnabled={reinforcementEnabled}
      />
      <div className="preview3d-canvas-wrap">
        <Scene3DCanvas model={model} controls={controls} cameraResetToken={cameraResetToken} />
      </div>
    </div>
  )
}

