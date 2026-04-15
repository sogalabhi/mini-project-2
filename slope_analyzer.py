"""
Slope Stability Analysis Wrapper for PySlope Library
======================================================
Author: Based on PySlope by Jesse Bonanno
Description: Production-ready OOP wrapper for Bishop's Simplified Method of Slices

This module provides a clean, flexible interface for slope stability analysis
following SOLID and DRY principles. All inputs are optional except slope geometry
and at least one material layer.

Quick Start:
-----------
    from slope_analyzer import SlopeStabilityAnalyzer
    
    # Simple usage
    analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
    analyzer.add_material(unit_weight=18, friction_angle=30, cohesion=10)
    results = analyzer.run_analysis(gui_mode=False)
    print(f"Factor of Safety: {results.factor_of_safety}")
    
    # Advanced usage with method chaining
    results = (SlopeStabilityAnalyzer(height=15, angle=35)
              .add_material(17, 28, 8, depth=5, name="Topsoil")
              .add_material(19, 32, 12, depth=10, name="Clay")
              .add_uniform_load(50, 2, 5)
              .set_water_table(6)
              .run_analysis())
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum
import math
import warnings
import random


# ============================================================================
# ENUMERATIONS
# ============================================================================

class LoadType(Enum):
    """Types of external loads that can be applied to the slope."""
    UNIFORM_DISTRIBUTED = "udl"
    LINE = "line"


class StabilityStatus(Enum):
    """Slope stability classification based on Factor of Safety."""
    UNSTABLE = "unstable"  # FOS < 1.0
    MARGINALLY_STABLE = "marginally_stable"  # 1.0 <= FOS < 1.25
    STABLE = "stable"  # 1.25 <= FOS < 1.5
    VERY_STABLE = "very_stable"  # FOS >= 1.5


# ============================================================================
# DATA CLASSES (Value Objects)
# ============================================================================

@dataclass(frozen=True)
class Material:
    """
    Represents a soil material layer with geotechnical properties.
    
    Attributes:
        unit_weight: Soil unit weight in kN/m³
        friction_angle: Internal friction angle in degrees
        cohesion: Soil cohesion in kPa
        depth: Depth to bottom of layer in meters (None = infinite/bedrock)
        name: Optional descriptive name for the material
    """
    unit_weight: float
    friction_angle: float
    cohesion: float
    depth: Optional[float] = None
    name: str = "Soil Layer"
    
    def __post_init__(self):
        """Validate material properties."""
        if self.unit_weight <= 0:
            raise ValueError(f"Unit weight must be positive, got {self.unit_weight}")
        if not 0 <= self.friction_angle <= 90:
            raise ValueError(f"Friction angle must be between 0-90°, got {self.friction_angle}")
        if self.cohesion < 0:
            raise ValueError(f"Cohesion cannot be negative, got {self.cohesion}")
        if self.depth is not None and self.depth <= 0:
            raise ValueError(f"Depth must be positive or None, got {self.depth}")


@dataclass(frozen=True)
class UniformLoad:
    """
    Uniform Distributed Load (UDL) applied on the slope surface.
    
    Attributes:
        magnitude: Load magnitude in kPa
        offset: Distance from slope crest in meters
        length: Width of the load in meters
    """
    magnitude: float
    offset: float
    length: float
    
    def __post_init__(self):
        """Validate load properties."""
        if self.magnitude < 0:
            raise ValueError(f"Load magnitude cannot be negative, got {self.magnitude}")
        if self.offset < 0:
            raise ValueError(f"Offset cannot be negative, got {self.offset}")
        if self.length <= 0:
            raise ValueError(f"Load length must be positive, got {self.length}")


@dataclass(frozen=True)
class LineLoad:
    """
    Concentrated line load applied on the slope surface.
    
    Attributes:
        magnitude: Load magnitude in kN/m
        offset: Distance from slope crest in meters
    """
    magnitude: float
    offset: float
    
    def __post_init__(self):
        """Validate load properties."""
        if self.magnitude < 0:
            raise ValueError(f"Load magnitude cannot be negative, got {self.magnitude}")
        if self.offset < 0:
            raise ValueError(f"Offset cannot be negative, got {self.offset}")


@dataclass(frozen=True)
class WaterTable:
    """
    Water table configuration for the slope.
    
    Attributes:
        depth: Depth to water table from slope surface in meters
        unit_weight: Unit weight of water in kN/m³ (default 9.81)
    """
    depth: float
    unit_weight: float = 9.81
    
    def __post_init__(self):
        """Validate water table properties."""
        if self.depth < 0:
            raise ValueError(f"Water table depth cannot be negative, got {self.depth}")
        if self.unit_weight <= 0:
            raise ValueError(f"Water unit weight must be positive, got {self.unit_weight}")


@dataclass
class AnalysisSettings:
    """
    Configuration settings for the slope stability analysis.
    
    Attributes:
        num_slices: Number of slices for Bishop's method (default 50)
        num_iterations: Number of slip circle iterations (default 2000)
        tolerance: Convergence tolerance for iterative calculations
    """
    num_slices: int = 50
    num_iterations: int = 2000
    tolerance: float = 0.001
    
    def __post_init__(self):
        """Validate analysis settings."""
        if self.num_slices < 10:
            raise ValueError(f"Number of slices must be at least 10, got {self.num_slices}")
        if self.num_iterations < 100:
            raise ValueError(f"Number of iterations must be at least 100, got {self.num_iterations}")
        if self.tolerance <= 0:
            raise ValueError(f"Tolerance must be positive, got {self.tolerance}")


@dataclass
class AnalysisResults:
    """
    Results from slope stability analysis.
    
    Attributes:
        factor_of_safety: Critical factor of safety (FOS)
        status: Stability classification
        critical_circle_center: (x, y) coordinates of critical slip circle center
        critical_circle_radius: Radius of critical slip circle in meters
        slope_geometry: Dictionary with slope dimensions
        material_count: Number of soil layers analyzed
        load_count: Number of external loads applied
        has_water_table: Whether water table was included
        raw_results: Optional raw data from PySlope for advanced users
    """
    factor_of_safety: float
    status: StabilityStatus
    critical_circle_center: Optional[Tuple[float, float]] = None
    critical_circle_radius: Optional[float] = None
    slope_geometry: Dict[str, float] = field(default_factory=dict)
    material_count: int = 0
    load_count: int = 0
    has_water_table: bool = False
    raw_results: Optional[Any] = None
    reinforcement: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Classify stability status based on FOS."""
        if self.factor_of_safety < 1.0:
            object.__setattr__(self, 'status', StabilityStatus.UNSTABLE)
        elif self.factor_of_safety < 1.25:
            object.__setattr__(self, 'status', StabilityStatus.MARGINALLY_STABLE)
        elif self.factor_of_safety < 1.5:
            object.__setattr__(self, 'status', StabilityStatus.STABLE)
        else:
            object.__setattr__(self, 'status', StabilityStatus.VERY_STABLE)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            'factor_of_safety': self.factor_of_safety,
            'status': self.status.value,
            'critical_circle_center': self.critical_circle_center,
            'critical_circle_radius': self.critical_circle_radius,
            'slope_geometry': self.slope_geometry,
            'material_count': self.material_count,
            'load_count': self.load_count,
            'has_water_table': self.has_water_table,
            'reinforcement': self.reinforcement,
        }
    
    def is_stable(self, minimum_fos: float = 1.0) -> bool:
        """Check if slope is stable based on minimum FOS requirement."""
        return self.factor_of_safety >= minimum_fos
    
    def get_summary(self) -> str:
        """Generate human-readable summary of results."""
        summary = f"""
Slope Stability Analysis Results
{'=' * 50}
Factor of Safety (FOS): {self.factor_of_safety:.3f}
Stability Status: {self.status.value.replace('_', ' ').title()}

Slope Geometry:
  Height: {self.slope_geometry.get('height', 'N/A')} m
  Angle: {self.slope_geometry.get('angle', 'N/A')}°
  Length: {self.slope_geometry.get('length', 'N/A')} m

Configuration:
  Material Layers: {self.material_count}
  External Loads: {self.load_count}
  Water Table: {'Yes' if self.has_water_table else 'No'}

Critical Failure Surface:
  Circle Center: {self.critical_circle_center if self.critical_circle_center else 'N/A'}
  Circle Radius: {f'{self.critical_circle_radius:.2f} m' if self.critical_circle_radius else 'N/A'}
{'=' * 50}
"""
        return summary.strip()


@dataclass
class MethodResult:
    method_name: str
    fos: float
    critical_circle_center: Optional[Tuple[float, float]] = None
    critical_circle_radius: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method_name": self.method_name,
            "fos": self.fos,
            "critical_circle_center": self.critical_circle_center,
            "critical_circle_radius": self.critical_circle_radius,
        }


@dataclass
class ComparisonResults:
    bishop: MethodResult
    fellenius: MethodResult
    circle_count: int
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bishop": self.bishop.to_dict(),
            "fellenius": self.fellenius.to_dict(),
            "circle_count": self.circle_count,
            "seed": self.seed,
        }


@dataclass(frozen=True)
class ReinforcementConfig:
    """Configuration inputs for practical soil nail design recommendations."""
    enabled: bool = True
    target_fos: float = 1.5
    steel_yield_strength: float = 415.0
    soil_grout_bond_friction: float = 100.0

    def __post_init__(self):
        if self.target_fos <= 1.0:
            raise ValueError(f"Target FOS must be greater than 1.0, got {self.target_fos}")
        if self.steel_yield_strength <= 0:
            raise ValueError(
                f"Steel yield strength must be positive, got {self.steel_yield_strength}"
            )
        if self.soil_grout_bond_friction <= 0:
            raise ValueError(
                "Soil-grout bond friction must be positive, "
                f"got {self.soil_grout_bond_friction}"
            )


# ============================================================================
# VALIDATORS (Single Responsibility Principle)
# ============================================================================

class GeometryValidator:
    """Validates slope geometry inputs."""
    
    @staticmethod
    def validate_height(height: float) -> None:
        """Validate slope height."""
        if height <= 0:
            raise ValueError(f"Slope height must be positive, got {height}")
    
    @staticmethod
    def validate_angle(angle: float) -> None:
        """Validate slope angle."""
        if not 0 < angle < 90:
            raise ValueError(f"Slope angle must be between 0° and 90°, got {angle}")
    
    @staticmethod
    def validate_length(length: float) -> None:
        """Validate slope length."""
        if length <= 0:
            raise ValueError(f"Slope length must be positive, got {length}")
    
    @staticmethod
    def calculate_missing_dimension(height: Optional[float] = None,
                                   angle: Optional[float] = None,
                                   length: Optional[float] = None) -> Tuple[float, float, float]:
        """
        Calculate missing dimension from the two provided.
        
        Returns:
            Tuple of (height, angle, length)
        """
        if height is not None and angle is not None:
            # Calculate length from height and angle
            angle_rad = math.radians(angle)
            length = height / math.tan(angle_rad)
            return height, angle, length
        
        elif height is not None and length is not None:
            # Calculate angle from height and length
            angle_rad = math.atan(height / length)
            angle = math.degrees(angle_rad)
            return height, angle, length
        
        elif angle is not None and length is not None:
            # Calculate height from angle and length
            angle_rad = math.radians(angle)
            height = length * math.tan(angle_rad)
            return height, angle, length
        
        else:
            raise ValueError("Must provide at least two of: height, angle, or length")


# ============================================================================
# MAIN ANALYZER CLASS
# ============================================================================

class SlopeStabilityAnalyzer:
    """
    Main class for slope stability analysis using Bishop's Simplified Method.
    
    This class provides a clean interface to the PySlope library, handling
    input validation, data organization, and result formatting.
    
    Example:
        >>> analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
        >>> analyzer.add_material(unit_weight=18, friction_angle=30, cohesion=10)
        >>> results = analyzer.run_analysis()
        >>> print(results.factor_of_safety)
    """
    
    def __init__(self,
                 height: Optional[float] = None,
                 angle: Optional[float] = None,
                 length: Optional[float] = None):
        """
        Initialize slope geometry.
        
        Args:
            height: Slope height in meters
            angle: Slope angle in degrees
            length: Slope horizontal length in meters
            
        Note:
            Provide at least two of the three parameters. The third will be calculated.
        """
        # Validate and calculate complete geometry
        self._height, self._angle, self._length = GeometryValidator.calculate_missing_dimension(
            height, angle, length
        )
        
        # Validate all dimensions
        GeometryValidator.validate_height(self._height)
        GeometryValidator.validate_angle(self._angle)
        GeometryValidator.validate_length(self._length)
        
        # Initialize collections
        self._materials: List[Material] = []
        self._loads: List[Union[UniformLoad, LineLoad]] = []
        self._water_table: Optional[WaterTable] = None
        self._reinforcement: Optional[ReinforcementConfig] = None
        self._settings: AnalysisSettings = AnalysisSettings()
        
        # Analysis state
        self._analysis_complete: bool = False
        self._last_results: Optional[AnalysisResults] = None
    
    # ------------------------------------------------------------------------
    # Properties (Getters)
    # ------------------------------------------------------------------------
    
    @property
    def height(self) -> float:
        """Get slope height in meters."""
        return self._height
    
    @property
    def angle(self) -> float:
        """Get slope angle in degrees."""
        return self._angle
    
    @property
    def length(self) -> float:
        """Get slope horizontal length in meters."""
        return self._length
    
    @property
    def material_count(self) -> int:
        """Get number of material layers."""
        return len(self._materials)
    
    @property
    def load_count(self) -> int:
        """Get number of external loads."""
        return len(self._loads)
    
    @property
    def has_water_table(self) -> bool:
        """Check if water table is configured."""
        return self._water_table is not None
    
    # ------------------------------------------------------------------------
    # Material Management (Open/Closed Principle - open for extension)
    # ------------------------------------------------------------------------
    
    def add_material(self,
                    unit_weight: float,
                    friction_angle: float,
                    cohesion: float,
                    depth: Optional[float] = None,
                    name: str = "Soil Layer") -> 'SlopeStabilityAnalyzer':
        """
        Add a soil material layer to the slope model.
        
        Args:
            unit_weight: Soil unit weight in kN/m³
            friction_angle: Internal friction angle in degrees
            cohesion: Soil cohesion in kPa
            depth: Depth to bottom of layer in meters (None for infinite depth)
            name: Descriptive name for the layer
            
        Returns:
            Self for method chaining
            
        Example:
            >>> analyzer.add_material(18, 30, 10, depth=5, name="Topsoil")
            >>>          .add_material(20, 35, 15, name="Bedrock")
        """
        material = Material(
            unit_weight=unit_weight,
            friction_angle=friction_angle,
            cohesion=cohesion,
            depth=depth,
            name=name
        )
        self._materials.append(material)
        self._analysis_complete = False  # Invalidate previous results
        return self
    
    def clear_materials(self) -> 'SlopeStabilityAnalyzer':
        """Remove all material layers."""
        self._materials.clear()
        self._analysis_complete = False
        return self
    
    def get_materials(self) -> List[Material]:
        """Get copy of all material layers."""
        return self._materials.copy()
    
    # ------------------------------------------------------------------------
    # Load Management
    # ------------------------------------------------------------------------
    
    def add_uniform_load(self,
                        magnitude: float,
                        offset: float,
                        length: float) -> 'SlopeStabilityAnalyzer':
        """
        Add a uniform distributed load (UDL) to the slope.
        
        Args:
            magnitude: Load magnitude in kPa
            offset: Distance from slope crest in meters
            length: Width of the load in meters
            
        Returns:
            Self for method chaining
        """
        load = UniformLoad(magnitude=magnitude, offset=offset, length=length)
        self._loads.append(load)
        self._analysis_complete = False
        return self
    
    def add_line_load(self,
                     magnitude: float,
                     offset: float) -> 'SlopeStabilityAnalyzer':
        """
        Add a concentrated line load to the slope.
        
        Args:
            magnitude: Load magnitude in kN/m
            offset: Distance from slope crest in meters
            
        Returns:
            Self for method chaining
        """
        load = LineLoad(magnitude=magnitude, offset=offset)
        self._loads.append(load)
        self._analysis_complete = False
        return self
    
    def clear_loads(self) -> 'SlopeStabilityAnalyzer':
        """Remove all external loads."""
        self._loads.clear()
        self._analysis_complete = False
        return self
    
    def get_loads(self) -> List[Union[UniformLoad, LineLoad]]:
        """Get copy of all loads."""
        return self._loads.copy()
    
    # ------------------------------------------------------------------------
    # Water Table Management
    # ------------------------------------------------------------------------
    
    def set_water_table(self,
                       depth: float,
                       unit_weight: float = 9.81) -> 'SlopeStabilityAnalyzer':
        """
        Configure water table for the analysis.
        
        Args:
            depth: Depth to water table from slope surface in meters
            unit_weight: Unit weight of water in kN/m³
            
        Returns:
            Self for method chaining
        """
        self._water_table = WaterTable(depth=depth, unit_weight=unit_weight)
        self._analysis_complete = False
        return self
    
    def remove_water_table(self) -> 'SlopeStabilityAnalyzer':
        """Remove water table from analysis (assumes dry soil)."""
        self._water_table = None
        self._analysis_complete = False
        return self

    def configure_reinforcement(self,
                                enabled: bool = True,
                                target_fos: float = 1.5,
                                steel_yield_strength: float = 415.0,
                                soil_grout_bond_friction: float = 100.0
                                ) -> 'SlopeStabilityAnalyzer':
        """Configure reinforcement design settings for post-analysis recommendations."""
        self._reinforcement = ReinforcementConfig(
            enabled=enabled,
            target_fos=target_fos,
            steel_yield_strength=steel_yield_strength,
            soil_grout_bond_friction=soil_grout_bond_friction,
        )
        self._analysis_complete = False
        return self
    
    # ------------------------------------------------------------------------
    # Analysis Settings
    # ------------------------------------------------------------------------
    
    def configure_analysis(self,
                          num_slices: Optional[int] = None,
                          num_iterations: Optional[int] = None,
                          tolerance: Optional[float] = None) -> 'SlopeStabilityAnalyzer':
        """
        Configure analysis parameters.
        
        Args:
            num_slices: Number of slices for Bishop's method
            num_iterations: Number of slip circle iterations to try
            tolerance: Convergence tolerance
            
        Returns:
            Self for method chaining
        """
        if num_slices is not None:
            self._settings.num_slices = num_slices
        if num_iterations is not None:
            self._settings.num_iterations = num_iterations
        if tolerance is not None:
            self._settings.tolerance = tolerance
        
        self._analysis_complete = False
        return self
    
    # ------------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------------
    
    def validate_model(self) -> Tuple[bool, List[str]]:
        """
        Validate the current model configuration.
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings_list = []
        
        # Check mandatory requirements
        if len(self._materials) == 0:
            return False, ["At least one material layer must be defined"]
        
        # Check for reasonable configurations
        if self._height > 50:
            warnings_list.append(f"Slope height ({self._height}m) is very large")
        
        if self._angle < 15:
            warnings_list.append(f"Slope angle ({self._angle}°) is very shallow")
        elif self._angle > 60:
            warnings_list.append(f"Slope angle ({self._angle}°) is very steep")
        
        # Check material properties
        for i, mat in enumerate(self._materials):
            if mat.friction_angle < 10:
                warnings_list.append(f"Material {i+1} has very low friction angle")
            if mat.cohesion < 1:
                warnings_list.append(f"Material {i+1} has very low cohesion")
        
        return True, warnings_list
    
    # ------------------------------------------------------------------------
    # Analysis Execution
    # ------------------------------------------------------------------------
    
    def run_analysis(self,
                    gui_mode: bool = False,
                    show_warnings: bool = True) -> AnalysisResults:
        """
        Execute the slope stability analysis.
        
        Args:
            gui_mode: If True, display plots; if False, return data only
            show_warnings: Whether to print validation warnings
            
        Returns:
            AnalysisResults object with factor of safety and details
            
        Raises:
            ValueError: If model configuration is invalid
            ImportError: If PySlope library is not installed
        """
        # Validate model
        is_valid, warnings_list = self.validate_model()
        if not is_valid:
            raise ValueError(f"Invalid model configuration: {warnings_list[0]}")
        
        if show_warnings and warnings_list:
            for warning in warnings_list:
                warnings.warn(warning, UserWarning)
        
        # Import PySlope (lazy import to avoid dependency errors until needed)
        try:
            import pyslope  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "PySlope library not found. Install PySlope for analysis: pip install pyslope"
            ) from exc

        results = self._run_pyslope_analysis()
        
        # Handle GUI mode
        if gui_mode:
            self._generate_plots(results)
        
        self._analysis_complete = True
        self._last_results = results
        
        return results

    def _run_pyslope_analysis(self) -> AnalysisResults:
        """Build and execute a PySlope model from current wrapper state."""
        slope = self._build_pyslope_model()
        slope.analyse_slope()
        fos = float(slope.get_min_FOS())
        circle = slope.get_min_FOS_circle()
        circle_center = None
        circle_radius = None
        if circle and len(circle) >= 3:
            circle_center = (float(circle[0]), float(circle[1]))
            circle_radius = float(circle[2])

        reinforcement_design = self._design_reinforcement(fos)

        return AnalysisResults(
            factor_of_safety=fos,
            status=StabilityStatus.STABLE,
            critical_circle_center=circle_center,
            critical_circle_radius=circle_radius,
            slope_geometry={
                'height': self._height,
                'angle': self._angle,
                'length': self._length
            },
            material_count=len(self._materials),
            load_count=len(self._loads),
            has_water_table=self._water_table is not None,
            raw_results=slope,
            reinforcement=reinforcement_design,
        )

    def _estimate_driving_force(self) -> float:
        """Estimate driving force in kN/m using slope self-weight and external loads."""
        if self._materials:
            avg_gamma = sum(m.unit_weight for m in self._materials) / len(self._materials)
        else:
            avg_gamma = 18.0

        slope_area = 0.5 * self._height * self._length
        slope_weight = avg_gamma * slope_area
        driving_from_weight = slope_weight * math.sin(math.radians(self._angle))

        udl_contrib = sum(
            load.magnitude * load.length for load in self._loads if isinstance(load, UniformLoad)
        )
        ll_contrib = sum(
            load.magnitude for load in self._loads if isinstance(load, LineLoad)
        )
        return max(1.0, driving_from_weight + udl_contrib + ll_contrib)

    def _design_reinforcement(self, fos: float) -> Optional[Dict[str, Any]]:
        """Generate practical soil nail recommendations when FOS is below target."""
        if self._reinforcement is None:
            return None

        cfg = self._reinforcement
        if not cfg.enabled:
            return {
                "required": False,
                "enabled": False,
                "target_fos": cfg.target_fos,
                "message": "Reinforcement design disabled by input settings.",
            }

        if fos >= cfg.target_fos:
            return {
                "required": False,
                "enabled": True,
                "target_fos": cfg.target_fos,
                "current_fos": fos,
                "message": "No reinforcement required. Current FOS already meets target.",
            }

        driving_force = self._estimate_driving_force()
        delta_r = max(0.0, (cfg.target_fos - fos) * driving_force)

        spacing_v = max(1.0, min(2.0, round(self._height / max(2, round(self._height / 1.5)), 2)))
        rows = max(2, int(math.ceil(self._height / spacing_v)))
        spacing_h_initial = 1.5
        cols_initial = max(1, int(math.ceil(self._length / spacing_h_initial)))
        initial_nails = max(1, rows * cols_initial)
        t_design = (delta_r / initial_nails) * 1.25

        as_mm2 = (t_design * 1000.0) / (0.55 * cfg.steel_yield_strength)
        dia_mm = math.sqrt((4.0 * as_mm2) / math.pi)
        available_diams = [12, 16, 20, 25, 28, 32]
        recommended_d_mm = next((d for d in available_diams if d >= dia_mm), available_diams[-1])

        d_m = recommended_d_mm / 1000.0
        tau = cfg.soil_grout_bond_friction
        pullout_embedment = t_design / max(1e-6, math.pi * d_m * tau)
        stable_zone_embedment = max(1.0, 0.25 * self._height)
        free_length = max(2.0, 0.35 * self._height)
        total_length = free_length + stable_zone_embedment + pullout_embedment
        total_length = round(max(3.0, total_length), 1)

        capacity_per_nail = max(1e-6, (math.pi * d_m * tau * pullout_embedment) / 1.25)
        required_nails = max(1, int(math.ceil(delta_r / capacity_per_nail)))
        cols = max(1, int(math.ceil(required_nails / rows)))
        spacing_h = round(max(1.0, min(2.5, self._length / cols)), 1)
        spacing_v = round(max(1.0, min(2.0, self._height / rows)), 1)

        return {
            "required": True,
            "enabled": True,
            "target_fos": round(cfg.target_fos, 3),
            "current_fos": round(fos, 3),
            "delta_r": round(delta_r, 2),
            "design_tension_per_nail_kn": round(t_design, 2),
            "steel_yield_strength_mpa": round(cfg.steel_yield_strength, 2),
            "as_required_mm2": round(as_mm2, 2),
            "recommended_diameter_mm": int(recommended_d_mm),
            "recommended_length_m": total_length,
            "spacing_v_m": spacing_v,
            "spacing_h_m": spacing_h,
            "nail_angle_deg": 15.0,
            "estimated_rows": rows,
            "estimated_columns": cols,
            "assumptions": [
                "Practical design defaults are used for driving force normalization.",
                "Steel area is computed as As = Tdesign / (0.55 * fy).",
                "Bond friction is treated as allowable pullout resistance along nail perimeter.",
            ],
            "message": (
                "Slope Unstable. Recommended Design: Use "
                f"{int(recommended_d_mm)}mm diameter soil nails, {total_length} meters long, "
                f"spaced at {spacing_h}m horizontal and {spacing_v}m vertical intervals."
            ),
        }

    def _build_pyslope_model(self):
        import pyslope
        slope = pyslope.Slope(
            height=self._height,
            angle=self._angle,
            length=self._length,
        )
        slope.update_analysis_options(
            slices=self._settings.num_slices,
            iterations=self._settings.num_iterations,
            tolerance=self._settings.tolerance,
        )
        finite_depths = [m.depth for m in self._materials if m.depth is not None]
        default_bottom = max(finite_depths) + self._height if finite_depths else self._height * 3
        pyslope_materials = []
        for material in self._materials:
            depth_to_bottom = (
                material.depth
                if material.depth is not None
                else default_bottom
            )
            pyslope_materials.append(
                pyslope.Material(
                    unit_weight=material.unit_weight,
                    friction_angle=material.friction_angle,
                    cohesion=material.cohesion,
                    depth_to_bottom=depth_to_bottom,
                    name=material.name,
                )
            )
        if pyslope_materials:
            slope.set_materials(*pyslope_materials)

        # Load mapping
        pyslope_udls = []
        pyslope_line_loads = []
        for load in self._loads:
            if isinstance(load, UniformLoad):
                pyslope_udls.append(
                    pyslope.Udl(
                        magnitude=load.magnitude,
                        offset=load.offset,
                        length=load.length,
                    )
                )
            elif isinstance(load, LineLoad):
                pyslope_line_loads.append(
                    pyslope.LineLoad(
                        magnitude=load.magnitude,
                        offset=load.offset,
                    )
                )
        if pyslope_udls:
            slope.set_udls(*pyslope_udls)
        if pyslope_line_loads:
            slope.set_lls(*pyslope_line_loads)

        # Water table mapping
        if self._water_table is not None:
            slope.set_water_table(depth=self._water_table.depth)
        return slope

    def _generate_candidate_circles(self, iterations: int, seed: int) -> List[Tuple[float, float, float]]:
        rng = random.Random(seed)
        circles: List[Tuple[float, float, float]] = []
        m = self._height / self._length

        for _ in range(max(1, iterations)):
            x1 = rng.uniform(0.03 * self._length, 0.45 * self._length)
            min_x2 = max(x1 + 0.08 * self._length, x1 + 0.5)
            if min_x2 >= self._length:
                continue
            x2 = rng.uniform(min_x2, 0.98 * self._length)

            y1 = m * x1
            y2 = m * x2

            mx = 0.5 * (x1 + x2)
            my = 0.5 * (y1 + y2)
            dx = x2 - x1
            dy = y2 - y1
            chord = math.hypot(dx, dy)
            if chord <= 0:
                continue

            nx = -dy / chord
            ny = dx / chord
            offset = rng.uniform(chord * 0.6, chord * 4.0)
            cx = mx + nx * offset
            cy = my + ny * offset
            r = math.hypot(cx - x1, cy - y1)

            if cy <= max(y1, y2):
                continue
            circles.append((cx, cy, r))

        return circles

    def _run_bishop_on_circles(self, circles: List[Tuple[float, float, float]]) -> MethodResult:
        slope = self._build_pyslope_model()
        slope.remove_analysis_limits()
        slope.remove_individual_planes()
        for cx, cy, r in circles:
            slope.add_single_circular_plane(cx, cy, r)
        slope.analyse_slope()
        fos = float(slope.get_min_FOS())
        circle = slope.get_min_FOS_circle()
        center = None
        radius = None
        if circle and len(circle) >= 3:
            center = (float(circle[0]), float(circle[1]))
            radius = float(circle[2])
        return MethodResult(
            method_name="Bishop",
            fos=fos,
            critical_circle_center=center,
            critical_circle_radius=radius,
        )

    def _equivalent_soil_properties(self, depth_below_surface: float) -> Tuple[float, float, float]:
        if depth_below_surface <= 0:
            top = self._materials[0]
            return top.unit_weight, top.cohesion, top.friction_angle

        materials = self._materials.copy()
        weighted_gamma = 0.0
        weighted_c = 0.0
        weighted_phi = 0.0
        consumed = 0.0

        for idx, mat in enumerate(materials):
            layer_bottom = mat.depth if mat.depth is not None else float("inf")
            layer_top = 0.0 if idx == 0 else (materials[idx - 1].depth or 0.0)
            top = max(consumed, layer_top)
            bottom = min(depth_below_surface, layer_bottom)
            thickness = max(0.0, bottom - top)
            if thickness <= 0:
                continue
            weighted_gamma += mat.unit_weight * thickness
            weighted_c += mat.cohesion * thickness
            weighted_phi += mat.friction_angle * thickness
            consumed += thickness
            if consumed >= depth_below_surface:
                break

        if consumed <= 0:
            top = materials[0]
            return top.unit_weight, top.cohesion, top.friction_angle

        return weighted_gamma / consumed, weighted_c / consumed, weighted_phi / consumed

    def _circle_surface_intersections(self, cx: float, cy: float, r: float) -> Optional[Tuple[float, float]]:
        m = self._height / self._length
        a = 1 + m * m
        b = -2 * cx - 2 * m * cy
        c = cx * cx + cy * cy - r * r
        disc = b * b - 4 * a * c
        if disc <= 0:
            return None
        root = math.sqrt(disc)
        x_a = (-b - root) / (2 * a)
        x_b = (-b + root) / (2 * a)
        x1, x2 = sorted((x_a, x_b))
        x1 = max(0.0, min(self._length, x1))
        x2 = max(0.0, min(self._length, x2))
        if x2 - x1 <= 1e-6:
            return None
        return x1, x2

    def _fellenius_fos_for_circle(self, circle: Tuple[float, float, float]) -> Optional[float]:
        cx, cy, r = circle
        intersections = self._circle_surface_intersections(cx, cy, r)
        if intersections is None:
            return None
        x1, x2 = intersections
        n = max(10, self._settings.num_slices)
        dx = (x2 - x1) / n
        if dx <= 0:
            return None

        m = self._height / self._length
        water_table_y = None
        if self._water_table is not None:
            # Water table elevation measured from crest datum.
            water_table_y = self._height - self._water_table.depth
        sum_resisting = 0.0
        sum_driving = 0.0

        for i in range(n):
            x_mid = x1 + (i + 0.5) * dx
            y_surface = m * x_mid
            term = r * r - (x_mid - cx) ** 2
            if term <= 0:
                continue
            y_base = cy - math.sqrt(term)
            if y_base >= y_surface:
                continue

            slice_height = y_surface - y_base
            slope_tan = -(x_mid - cx) / math.sqrt(term)
            alpha = abs(math.atan(slope_tan))
            cos_alpha = max(math.cos(alpha), 1e-6)
            l_base = dx / cos_alpha

            gamma, cohesion, phi = self._equivalent_soil_properties(slice_height)
            area = slice_height * dx
            W = gamma * area

            for load in self._loads:
                if isinstance(load, UniformLoad):
                    if load.offset <= x_mid <= (load.offset + load.length):
                        W += load.magnitude * dx
                elif isinstance(load, LineLoad):
                    if abs(x_mid - load.offset) <= (0.5 * dx):
                        W += load.magnitude

            u = 0.0
            if water_table_y is not None:
                head = max(0.0, water_table_y - y_base)
                u = self._water_table.unit_weight * head

            N_eff = W * math.cos(alpha) - u * l_base
            resisting = cohesion * l_base + max(0.0, N_eff) * math.tan(math.radians(phi))
            driving = W * math.sin(alpha)
            sum_resisting += resisting
            sum_driving += driving

        if sum_driving <= 0:
            return None
        return sum_resisting / sum_driving

    def _run_fellenius_on_circles(self, circles: List[Tuple[float, float, float]]) -> MethodResult:
        best_fos = float("inf")
        best_circle: Optional[Tuple[float, float, float]] = None
        for circle in circles:
            fos = self._fellenius_fos_for_circle(circle)
            if fos is None:
                continue
            if fos < best_fos:
                best_fos = fos
                best_circle = circle

        center = None
        radius = None
        if best_circle is not None:
            center = (float(best_circle[0]), float(best_circle[1]))
            radius = float(best_circle[2])
        return MethodResult(
            method_name="Fellenius",
            fos=float(best_fos if best_fos != float("inf") else 0.0),
            critical_circle_center=center,
            critical_circle_radius=radius,
        )

    def run_comparison(self, iterations: Optional[int] = None, seed: int = 42) -> ComparisonResults:
        circle_count = iterations if iterations is not None else self._settings.num_iterations
        circles = self._generate_candidate_circles(circle_count, seed)
        bishop = self._run_bishop_on_circles(circles)
        fellenius = self._run_fellenius_on_circles(circles)
        return ComparisonResults(
            bishop=bishop,
            fellenius=fellenius,
            circle_count=len(circles),
            seed=seed,
        )
    
    def _calculate_simplified_fos(self) -> float:
        """
        Calculate a simplified Factor of Safety.
        
        Note: This is a placeholder. In production, this would call PySlope's
        Bishop method implementation.
        """
        # Get average material properties
        avg_friction = sum(m.friction_angle for m in self._materials) / len(self._materials)
        avg_cohesion = sum(m.cohesion for m in self._materials) / len(self._materials)
        avg_unit_weight = sum(m.unit_weight for m in self._materials) / len(self._materials)
        
        # Simplified infinite slope formula (placeholder)
        angle_rad = math.radians(self._angle)
        
        # Resisting forces
        tan_friction = math.tan(math.radians(avg_friction))
        cohesion_term = avg_cohesion / (avg_unit_weight * self._height * math.sin(angle_rad))
        friction_term = tan_friction / math.tan(angle_rad)
        
        fos = cohesion_term + friction_term
        
        # Apply penalties for loads
        if len(self._loads) > 0:
            load_penalty = 0.1 * len(self._loads)
            fos = fos * (1 - load_penalty)
        
        # Apply penalty for water table
        if self._water_table is not None:
            fos = fos * 0.85
        
        return max(0.1, fos)  # Ensure positive FOS
    
    def _generate_plots(self, results: AnalysisResults) -> None:
        """
        Generate matplotlib visualizations.
        
        Args:
            results: Analysis results to visualize
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            warnings.warn("Matplotlib not installed. Skipping plot generation.", UserWarning)
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Slope geometry
        self._plot_slope_geometry(ax1)
        
        # Plot 2: Critical failure surface
        self._plot_critical_surface(ax2, results)
        
        plt.tight_layout()
        plt.show()

    def generate_plot_bytes(self, results: AnalysisResults) -> bytes:
        """
        Generate matplotlib diagram as PNG bytes (for web/API use).
        Does not display; returns bytes suitable for StreamingResponse.

        Args:
            results: Analysis results to visualize

        Returns:
            PNG image bytes
        """
        import io
        try:
            import matplotlib
            matplotlib.use('Agg')  # non-interactive backend for headless use
            import matplotlib.pyplot as plt
        except ImportError:
            raise RuntimeError("Matplotlib required for diagram generation. pip install matplotlib")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        self._plot_slope_geometry(ax1)
        self._plot_critical_surface(ax2, results)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def _plot_slope_geometry(self, ax) -> None:
        """Plot the slope geometry with materials and loads."""
        # Draw slope
        x = [0, self._length, self._length, 0, 0]
        y = [self._height, 0, -self._height, -self._height, self._height]
        ax.plot(x, y, 'k-', linewidth=2)
        ax.fill(x, y, alpha=0.3, color='brown', label='Slope')
        
        # Add material layers (simplified visualization)
        for i, mat in enumerate(self._materials):
            ax.text(self._length/2, -self._height/2 - i, 
                   f"{mat.name}\nγ={mat.unit_weight} kN/m³\nφ={mat.friction_angle}°\nc={mat.cohesion} kPa",
                   ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Elevation (m)')
        ax.set_title('Slope Geometry')
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        ax.legend()
    
    def _plot_critical_surface(self, ax, results: AnalysisResults) -> None:
        """Plot the critical failure surface."""
        # Draw slope
        x = [0, self._length, self._length, 0, 0]
        y = [self._height, 0, -self._height, -self._height, self._height]
        ax.plot(x, y, 'k-', linewidth=2)
        ax.fill(x, y, alpha=0.3, color='brown')
        
        # Draw critical circle if available
        if results.critical_circle_center and results.critical_circle_radius:
            import matplotlib.pyplot as plt
            cx, cy = results.critical_circle_center
            radius = results.critical_circle_radius
            circle = plt.Circle((cx, cy), radius, fill=False, 
                               color='red', linewidth=2, linestyle='--',
                               label=f'Critical Circle (FOS={results.factor_of_safety:.3f})')
            ax.add_patch(circle)
            ax.plot(cx, cy, 'r*', markersize=10, label='Circle Center')
        
        # Add FOS text
        status_color = {
            StabilityStatus.UNSTABLE: 'red',
            StabilityStatus.MARGINALLY_STABLE: 'orange',
            StabilityStatus.STABLE: 'yellow',
            StabilityStatus.VERY_STABLE: 'green'
        }
        
        ax.text(0.02, 0.98, f"FOS = {results.factor_of_safety:.3f}\nStatus: {results.status.value}",
                transform=ax.transAxes, fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor=status_color[results.status], alpha=0.7))
        
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Elevation (m)')
        ax.set_title('Critical Failure Surface')
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        ax.legend()
    
    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------
    
    def get_model_summary(self) -> str:
        """Generate a summary of the current model configuration."""
        summary = f"""
Slope Stability Model Configuration
{'=' * 50}
Geometry:
  Height: {self._height:.2f} m
  Angle: {self._angle:.2f}°
  Length: {self._length:.2f} m

Materials: {len(self._materials)}
"""
        for i, mat in enumerate(self._materials, 1):
            summary += f"  Layer {i}: {mat.name}\n"
            summary += f"    - Unit Weight: {mat.unit_weight} kN/m³\n"
            summary += f"    - Friction Angle: {mat.friction_angle}°\n"
            summary += f"    - Cohesion: {mat.cohesion} kPa\n"
        
        summary += f"\nExternal Loads: {len(self._loads)}\n"
        for i, load in enumerate(self._loads, 1):
            if isinstance(load, UniformLoad):
                summary += f"  UDL {i}: {load.magnitude} kPa at {load.offset}m offset\n"
            else:
                summary += f"  Line Load {i}: {load.magnitude} kN/m at {load.offset}m offset\n"
        
        summary += f"\nWater Table: {'Configured' if self._water_table else 'Not configured'}\n"
        summary += f"Analysis Settings: {self._settings.num_slices} slices, {self._settings.num_iterations} iterations\n"
        summary += "=" * 50
        
        return summary
    
    def export_config(self) -> Dict[str, Any]:
        """
        Export current configuration as a dictionary.
        
        Returns:
            Dictionary containing all model parameters
        """
        return {
            'geometry': {
                'height': self._height,
                'angle': self._angle,
                'length': self._length
            },
            'materials': [
                {
                    'unit_weight': m.unit_weight,
                    'friction_angle': m.friction_angle,
                    'cohesion': m.cohesion,
                    'depth': m.depth,
                    'name': m.name
                }
                for m in self._materials
            ],
            'loads': [
                {
                    'type': 'udl' if isinstance(load, UniformLoad) else 'line',
                    'magnitude': load.magnitude,
                    'offset': load.offset,
                    'length': load.length if isinstance(load, UniformLoad) else None
                }
                for load in self._loads
            ],
            'water_table': {
                'depth': self._water_table.depth,
                'unit_weight': self._water_table.unit_weight
            } if self._water_table else None,
            'settings': {
                'num_slices': self._settings.num_slices,
                'num_iterations': self._settings.num_iterations,
                'tolerance': self._settings.tolerance
            }
        }
    
    def get_last_results(self) -> Optional[AnalysisResults]:
        """Get results from the most recent analysis, if available."""
        return self._last_results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_simple_slope(height: float,
                       angle: float,
                       unit_weight: float = 18.0,
                       friction_angle: float = 30.0,
                       cohesion: float = 10.0) -> SlopeStabilityAnalyzer:
    """
    Quick factory function to create a basic slope model.
    
    Args:
        height: Slope height in meters
        angle: Slope angle in degrees
        unit_weight: Soil unit weight in kN/m³
        friction_angle: Soil friction angle in degrees
        cohesion: Soil cohesion in kPa
        
    Returns:
        Configured SlopeStabilityAnalyzer ready for analysis
    """
    analyzer = SlopeStabilityAnalyzer(height=height, angle=angle)
    analyzer.add_material(
        unit_weight=unit_weight,
        friction_angle=friction_angle,
        cohesion=cohesion,
        name="Homogeneous Soil"
    )
    return analyzer


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example 1: Simple slope
    print("=" * 70)
    print("EXAMPLE 1: Simple Homogeneous Slope")
    print("=" * 70)
    
    analyzer1 = create_simple_slope(height=10, angle=30)
    print(analyzer1.get_model_summary())
    
    results1 = analyzer1.run_analysis(gui_mode=False)
    print("\n" + results1.get_summary())
    
    # Example 2: Multi-layer slope with loads
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multi-Layer Slope with External Load")
    print("=" * 70)
    
    analyzer2 = SlopeStabilityAnalyzer(height=15, angle=35)
    analyzer2.add_material(unit_weight=17, friction_angle=28, cohesion=8, depth=5, name="Topsoil")
    analyzer2.add_material(unit_weight=19, friction_angle=32, cohesion=12, depth=10, name="Clay")
    analyzer2.add_material(unit_weight=22, friction_angle=38, cohesion=20, name="Bedrock")
    analyzer2.add_uniform_load(magnitude=50, offset=2, length=5)
    
    print(analyzer2.get_model_summary())
    
    results2 = analyzer2.run_analysis(gui_mode=False)
    print("\n" + results2.get_summary())
    
    # Example 3: Slope with water table
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Slope with Water Table")
    print("=" * 70)
    
    analyzer3 = SlopeStabilityAnalyzer(height=12, angle=40)
    analyzer3.add_material(unit_weight=18, friction_angle=30, cohesion=10, name="Sandy Clay")
    analyzer3.set_water_table(depth=6)
    
    print(analyzer3.get_model_summary())
    
    results3 = analyzer3.run_analysis(gui_mode=False)
    print("\n" + results3.get_summary())
    
    # Example 4: Method chaining
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Method Chaining")
    print("=" * 70)
    
    results4 = (SlopeStabilityAnalyzer(height=10, angle=30)
                .add_material(18, 30, 10, name="Soil Layer 1")
                .add_material(20, 35, 15, name="Soil Layer 2")
                .add_line_load(100, 3)
                .run_analysis(gui_mode=False))
    
    print(results4.get_summary())
    
    # Export configuration example
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Export Configuration")
    print("=" * 70)
    
    config = analyzer2.export_config()
    import json
    print(json.dumps(config, indent=2))
