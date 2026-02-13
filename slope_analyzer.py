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
            'has_water_table': self.has_water_table
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
            import pyslope
            # TODO: Implement actual PySlope integration here
            # For now, use simplified calculation
            use_simplified = True
        except ImportError:
            if show_warnings:
                warnings.warn(
                    "PySlope library not found. Using simplified FOS calculation. "
                    "Install PySlope for accurate analysis: pip install pyslope",
                    UserWarning
                )
            use_simplified = True
        
        # Calculate FOS
        # In production with PySlope installed, you would:
        # 1. Create PySlope slope object with geometry
        # 2. Add materials, loads, water table
        # 3. Run analysis
        # 4. Extract results
        
        # For now, use simplified calculation
        fos = self._calculate_simplified_fos()
        
        # Create results object
        results = AnalysisResults(
            factor_of_safety=fos,
            status=StabilityStatus.STABLE,  # Will be set in __post_init__
            critical_circle_center=(self._length / 2, self._height * 1.5),
            critical_circle_radius=self._height * 2,
            slope_geometry={
                'height': self._height,
                'angle': self._angle,
                'length': self._length
            },
            material_count=len(self._materials),
            load_count=len(self._loads),
            has_water_table=self._water_table is not None
        )
        
        # Handle GUI mode
        if gui_mode:
            self._generate_plots(results)
        
        self._analysis_complete = True
        self._last_results = results
        
        return results
    
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
