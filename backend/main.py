import io
import sys
from pathlib import Path

# Add project root so we can import slope_analyzer
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from slope_analyzer import SlopeStabilityAnalyzer

app = FastAPI()


# ---------------------------------------------------------------------------
# Pydantic models (match frontend payload)
# ---------------------------------------------------------------------------

class GeometryInput(BaseModel):
    height: Optional[float] = None
    angle: Optional[float] = None
    length: Optional[float] = None


class LayerInput(BaseModel):
    name: str = "Soil Layer"
    unit_weight: float
    friction_angle: float
    cohesion: float
    depth_to_bottom: Optional[float] = None


class UDLInput(BaseModel):
    magnitude: float
    offset: float
    length: float


class LineLoadInput(BaseModel):
    magnitude: float
    offset: float


class SettingsInput(BaseModel):
    num_slices: int = 50
    num_iterations: int = 2000
    tolerance: float = 0.001


class AnalysisPayload(BaseModel):
    geometry: GeometryInput
    layers: list[LayerInput]
    udls: list[UDLInput] = []
    line_loads: list[LineLoadInput] = []
    water_table_depth: Optional[float] = None
    water_unit_weight: float = 9.81
    settings: SettingsInput = SettingsInput()


# ---------------------------------------------------------------------------
# Build SlopeStabilityAnalyzer from payload
# ---------------------------------------------------------------------------

def build_analyzer(payload: AnalysisPayload) -> SlopeStabilityAnalyzer:
    g = payload.geometry
    height = g.height
    angle = g.angle
    length = g.length

    # Need at least 2 of height, angle, length
    if height is None and angle is None:
        raise HTTPException(400, "geometry must include height and/or angle")
    if height is None and length is None:
        raise HTTPException(400, "geometry must include height and/or length")
    if angle is None and length is None:
        raise HTTPException(400, "geometry must include angle and/or length")

    analyzer = SlopeStabilityAnalyzer(height=height, angle=angle, length=length)

    for layer in payload.layers:
        analyzer.add_material(
            unit_weight=layer.unit_weight,
            friction_angle=layer.friction_angle,
            cohesion=layer.cohesion,
            depth=layer.depth_to_bottom,
            name=layer.name,
        )

    for udl in payload.udls:
        analyzer.add_uniform_load(
            magnitude=udl.magnitude,
            offset=udl.offset,
            length=udl.length,
        )

    for ll in payload.line_loads:
        analyzer.add_line_load(
            magnitude=ll.magnitude,
            offset=ll.offset,
        )

    if payload.water_table_depth is not None:
        analyzer.set_water_table(
            depth=payload.water_table_depth,
            unit_weight=payload.water_unit_weight,
        )

    s = payload.settings
    analyzer.configure_analysis(
        num_slices=s.num_slices,
        num_iterations=s.num_iterations,
        tolerance=s.tolerance,
    )

    return analyzer


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {"message": "Slope Stability API running"}


@app.get("/health")
def health_check():
    return {"status": "Backend running"}


@app.get("/methods")
def get_methods():
    return {"methods": ["Bishop Method"]}


@app.post("/analyze")
def analyze_slope(data: AnalysisPayload):
    try:
        analyzer = build_analyzer(data)
        results = analyzer.run_analysis(gui_mode=False, show_warnings=False)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {
        "factor_of_safety": results.factor_of_safety,
        "status": results.status.value,
        "stability_status": results.status.value,
        "method": "Bishop Simplified",
        "warnings": [],
    }


@app.post("/analyze-image")
def analyze_slope_image(data: AnalysisPayload):
    try:
        analyzer = build_analyzer(data)
        results = analyzer.run_analysis(gui_mode=False, show_warnings=False)
        png_bytes = analyzer.generate_plot_bytes(results)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

    return StreamingResponse(
        io.BytesIO(png_bytes),
        media_type="image/png",
    )
