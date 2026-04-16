from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class DEMPointInput(BaseModel):
    x: float
    y: float
    z: float


class SurfaceDatasetInput(BaseModel):
    label: str = Field(..., min_length=1, max_length=12)
    path: str = Field(..., min_length=1)
    interpolation_mode: str = "a1"
    points: List[DEMPointInput] = Field(..., min_length=1, max_length=20000)


class MaterialDefinitionInput(BaseModel):
    name: str = Field(..., min_length=1)
    model_type: int = Field(..., ge=1, le=5)
    model_parameters: List[float] = Field(..., min_length=1, max_length=16)
    unit_weight: float = Field(..., gt=0.0)


class SolverConfigInput(BaseModel):
    max_iterations: int = Field(200, gt=0, le=5000)
    tol_fs: float = Field(1e-3, gt=0.0)
    damping: float = Field(1.0, gt=0.0, le=1.0)


class DirectionSearchConfigInput(BaseModel):
    spacing_deg: float = Field(0.5, gt=0.0)
    tolerance_deg: float = Field(10.0, ge=0.0)
    user_direction_deg: Optional[float] = Field(None, ge=0.0, le=360.0)


class MethodRunConfigInput(BaseModel):
    method_id: int = Field(..., ge=1, le=7)
    solver: SolverConfigInput = Field(default_factory=SolverConfigInput)
    direction: DirectionSearchConfigInput = Field(default_factory=DirectionSearchConfigInput)
    use_side_resistance: bool = True


class GridConfigInput(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    col_x_max: int = Field(..., gt=0, le=5000)
    col_y_max: int = Field(..., gt=0, le=5000)

    @field_validator("x_max")
    @classmethod
    def _x_bounds(cls, value: float, values: Any) -> float:
        if values.data.get("x_min") is not None and values.data["x_min"] >= value:
            raise ValueError("x_min must be < x_max")
        return value

    @field_validator("y_max")
    @classmethod
    def _y_bounds(cls, value: float, values: Any) -> float:
        if values.data.get("y_min") is not None and values.data["y_min"] >= value:
            raise ValueError("y_min must be < y_max")
        return value

    @field_validator("z_max")
    @classmethod
    def _z_bounds(cls, value: float, values: Any) -> float:
        if values.data.get("z_min") is not None and values.data["z_min"] >= value:
            raise ValueError("z_min must be < z_max")
        return value


class SlipSurfaceConfigInput(BaseModel):
    mode: Literal["ellipsoid", "user_defined"]
    ellipsoid_center: Optional[List[float]] = None
    ellipsoid_radii: Optional[List[float]] = None
    user_defined_surface_path: Optional[str] = None
    user_defined_interpolation: str = "a1"

    @field_validator("ellipsoid_center")
    @classmethod
    def _center_len3(cls, value: Optional[List[float]]) -> Optional[List[float]]:
        if value is not None and len(value) != 3:
            raise ValueError("ellipsoid_center must have exactly 3 values")
        return value

    @field_validator("ellipsoid_radii")
    @classmethod
    def _radii_len3(cls, value: Optional[List[float]]) -> Optional[List[float]]:
        if value is not None and len(value) != 3:
            raise ValueError("ellipsoid_radii must have exactly 3 values")
        return value

    @field_validator("user_defined_surface_path")
    @classmethod
    def _validate_mode_requirements(cls, value: Optional[str], values: Any) -> Optional[str]:
        mode = values.data.get("mode")
        center = values.data.get("ellipsoid_center")
        radii = values.data.get("ellipsoid_radii")
        if mode == "ellipsoid":
            if center is None or radii is None:
                raise ValueError("ellipsoid mode requires ellipsoid_center and ellipsoid_radii")
            if any(r <= 0.0 for r in radii):
                raise ValueError("ellipsoid_radii values must be > 0")
        elif mode == "user_defined":
            if not value:
                raise ValueError("user_defined mode requires user_defined_surface_path")
        return value


class DebugOptionsInput(BaseModel):
    include_analysis_rows: bool = False


class Analyze3DRequest(BaseModel):
    method_config: MethodRunConfigInput
    grid_config: GridConfigInput
    slip_surface_config: SlipSurfaceConfigInput
    materials: Dict[str, MaterialDefinitionInput] = Field(..., min_length=1, max_length=64)
    top_surface: Optional[SurfaceDatasetInput] = None
    user_slip_surface: Optional[SurfaceDatasetInput] = None
    surface_paths: Optional[List[str]] = None
    surface_types: Optional[List[str]] = None
    interpolation_modes: Optional[List[str]] = None
    water_level_z: Optional[float] = None
    debug: DebugOptionsInput = Field(default_factory=DebugOptionsInput)


class Analyze3DMultiRequest(BaseModel):
    method_ids: List[int] = Field(..., min_length=1, max_length=7)
    base_request: Analyze3DRequest


class Validate3DResponse(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)

