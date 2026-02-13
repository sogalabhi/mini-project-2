# Slope Stability Analyzer

A production-ready, object-oriented Python wrapper for slope stability analysis using Bishop's Simplified Method of Slices. Built following SOLID and DRY principles with comprehensive validation and flexible configuration.

## Features

- **2D Slope Modeling**: Create visual models with defined height and steepness
- **Multi-Layer Soil Profiles**: Support for infinite horizontal layers with different properties
- **External Loading**: Simulate UDL (Uniform Distributed Loads) and Line Loads
- **Water Table Analysis**: Account for groundwater effects on stability
- **Failure Surface Search**: Automatic identification of critical slip circles
- **Batch Processing**: Analyze multiple scenarios efficiently
- **Method Chaining**: Fluent API for clean, readable code
- **Comprehensive Validation**: Input validation with helpful error messages
- **Export/Import**: Save and load configurations as JSON

## Installation

```bash
# Required (future integration)
`pip install pyslope
`
# Optional for visualization
pip install matplotlib
```

## Quick Start

### Basic Usage

```python
from slope_analyzer import SlopeStabilityAnalyzer

# Create analyzer with slope geometry
analyzer = SlopeStabilityAnalyzer(height=10, angle=30)

# Add soil material
analyzer.add_material(
    unit_weight=18,      # kN/m³
    friction_angle=30,   # degrees
    cohesion=10         # kPa
)

# Run analysis
results = analyzer.run_analysis(gui_mode=False)

# Access results
print(f"Factor of Safety: {results.factor_of_safety:.3f}")
print(f"Status: {results.status.value}")
```

### Method Chaining

```python
results = (SlopeStabilityAnalyzer(height=15, angle=35)
          .add_material(17, 28, 8, depth=5, name="Topsoil")
          .add_material(19, 32, 12, depth=10, name="Clay")
          .add_uniform_load(50, 2, 5)
          .set_water_table(6)
          .run_analysis())
```

## API Reference

### SlopeStabilityAnalyzer

#### Constructor

```python
SlopeStabilityAnalyzer(height=None, angle=None, length=None)
```

**Parameters:**
- `height` (float): Slope height in meters
- `angle` (float): Slope angle in degrees
- `length` (float): Horizontal length in meters

**Note:** Provide at least two of the three parameters. The third will be calculated.

#### Methods

##### Material Management

```python
add_material(unit_weight, friction_angle, cohesion, depth=None, name="Soil Layer")
```

Add a soil material layer.

**Parameters:**
- `unit_weight` (float): Soil unit weight in kN/m³
- `friction_angle` (float): Internal friction angle in degrees (0-90)
- `cohesion` (float): Soil cohesion in kPa (≥0)
- `depth` (float, optional): Depth to bottom of layer in meters (None for infinite depth)
- `name` (str): Descriptive name for the layer

**Returns:** self (for method chaining)

**Example:**
```python
analyzer.add_material(18, 30, 10, depth=5, name="Topsoil")
```

##### Load Management

```python
add_uniform_load(magnitude, offset, length)
```

Add a uniform distributed load (UDL).

**Parameters:**
- `magnitude` (float): Load magnitude in kPa
- `offset` (float): Distance from slope crest in meters
- `length` (float): Width of the load in meters

```python
add_line_load(magnitude, offset)
```

Add a concentrated line load.

**Parameters:**
- `magnitude` (float): Load magnitude in kN/m
- `offset` (float): Distance from slope crest in meters

##### Water Table

```python
set_water_table(depth, unit_weight=9.81)
```

Configure water table for analysis.

**Parameters:**
- `depth` (float): Depth to water table from slope surface in meters
- `unit_weight` (float): Unit weight of water in kN/m³ (default 9.81)

##### Analysis Configuration

```python
configure_analysis(num_slices=None, num_iterations=None, tolerance=None)
```

Configure analysis parameters.

**Parameters:**
- `num_slices` (int): Number of slices for Bishop's method (default 50)
- `num_iterations` (int): Number of slip circle iterations (default 2000)
- `tolerance` (float): Convergence tolerance (default 0.001)

##### Analysis Execution

```python
run_analysis(gui_mode=False, show_warnings=True)
```

Execute the slope stability analysis.

**Parameters:**
- `gui_mode` (bool): If True, display plots; if False, return data only
- `show_warnings` (bool): Whether to print validation warnings

**Returns:** AnalysisResults object

##### Utility Methods

```python
validate_model()
```
Returns: `(is_valid: bool, warnings: List[str])`

```python
get_model_summary()
```
Returns: String summary of model configuration

```python
export_config()
```
Returns: Dictionary containing all model parameters

```python
get_materials()
get_loads()
get_last_results()
```

### AnalysisResults

Results object returned by `run_analysis()`.

**Attributes:**
- `factor_of_safety` (float): Critical factor of safety
- `status` (StabilityStatus): UNSTABLE, MARGINALLY_STABLE, STABLE, or VERY_STABLE
- `critical_circle_center` (tuple): (x, y) coordinates of slip circle center
- `critical_circle_radius` (float): Radius in meters
- `slope_geometry` (dict): Slope dimensions
- `material_count` (int): Number of soil layers
- `load_count` (int): Number of external loads
- `has_water_table` (bool): Whether water table was included

**Methods:**
- `is_stable(minimum_fos=1.0)`: Check if slope meets FOS requirement
- `to_dict()`: Convert to dictionary format
- `get_summary()`: Generate human-readable summary

### Factory Functions

```python
create_simple_slope(height, angle, unit_weight=18.0, friction_angle=30.0, cohesion=10.0)
```

Quick factory function for basic homogeneous slopes.

## Usage Examples

### Example 1: Basic Analysis

```python
from slope_analyzer import SlopeStabilityAnalyzer

analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
analyzer.add_material(18, 30, 10, name="Clay")
results = analyzer.run_analysis()

print(f"Factor of Safety: {results.factor_of_safety:.3f}")
```

### Example 2: Multi-Layer Slope

```python
analyzer = SlopeStabilityAnalyzer(height=15, angle=35)
analyzer.add_material(17, 28, 8, depth=5, name="Topsoil")
analyzer.add_material(19, 32, 12, depth=10, name="Clay")
analyzer.add_material(22, 38, 20, name="Bedrock")

results = analyzer.run_analysis()
```

### Example 3: With External Load

```python
analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
analyzer.add_material(18, 30, 10)
analyzer.add_uniform_load(magnitude=50, offset=2, length=5)  # Building load

results = analyzer.run_analysis()
```

### Example 4: With Water Table

```python
analyzer = SlopeStabilityAnalyzer(height=12, angle=40)
analyzer.add_material(18, 30, 10, name="Sandy Clay")
analyzer.set_water_table(depth=6)  # Water at 6m depth

results = analyzer.run_analysis()
print(f"Water impact: {results.factor_of_safety:.3f}")
```

### Example 5: Batch Analysis

```python
angles = [25, 30, 35, 40, 45]
results_list = []

for angle in angles:
    analyzer = SlopeStabilityAnalyzer(height=10, angle=angle)
    analyzer.add_material(18, 30, 10)
    results = analyzer.run_analysis(show_warnings=False)
    results_list.append((angle, results.factor_of_safety))

# Analyze results
for angle, fos in results_list:
    print(f"{angle}° → FOS = {fos:.3f}")
```

### Example 6: Safe Distance Calculation

```python
target_fos = 1.5
load = 100  # kPa

for offset in range(0, 20, 2):
    analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
    analyzer.add_material(18, 30, 10)
    analyzer.add_uniform_load(load, offset, 3)
    
    results = analyzer.run_analysis(show_warnings=False)
    
    if results.factor_of_safety >= target_fos:
        print(f"Safe offset: >= {offset}m")
        break
```

### Example 7: Export Configuration

```python
analyzer = SlopeStabilityAnalyzer(height=15, angle=35)
analyzer.add_material(17, 28, 8, depth=5, name="Topsoil")
analyzer.add_line_load(200, 3)

# Export as dictionary
config = analyzer.export_config()

# Save to JSON
import json
with open('slope_config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Stability Classification

The analyzer automatically classifies slopes based on Factor of Safety (FOS):

- **UNSTABLE**: FOS < 1.0 (Failure likely)
- **MARGINALLY_STABLE**: 1.0 ≤ FOS < 1.25 (Marginal safety)
- **STABLE**: 1.25 ≤ FOS < 1.5 (Adequate safety)
- **VERY_STABLE**: FOS ≥ 1.5 (High safety margin)

## Design Principles

### SOLID Principles

1. **Single Responsibility**: Each class has one clear purpose
   - `Material`, `UniformLoad`, `LineLoad`: Data containers
   - `GeometryValidator`: Validation logic
   - `SlopeStabilityAnalyzer`: Analysis orchestration
   - `AnalysisResults`: Results packaging

2. **Open/Closed**: Open for extension, closed for modification
   - Easy to add new load types, material models, or analysis methods
   - Extensible through inheritance

3. **Liskov Substitution**: Load types are interchangeable
   - `UniformLoad` and `LineLoad` can be used polymorphically

4. **Interface Segregation**: Minimal, focused interfaces
   - Methods grouped by responsibility
   - Optional parameters avoid interface bloat

5. **Dependency Inversion**: Depends on abstractions
   - PySlope library is lazily loaded
   - Can swap analysis backends

### DRY Principle

- Validation logic centralized in `GeometryValidator`
- Material properties validated in `Material.__post_init__`
- No repeated validation code
- Reusable factory functions

## Error Handling

The analyzer provides clear, actionable error messages:

```python
# Missing required inputs
analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
results = analyzer.run_analysis()
# ValueError: Invalid model configuration: At least one material layer must be defined

# Invalid material properties
analyzer.add_material(-5, 30, 10)
# ValueError: Unit weight must be positive, got -5

# Invalid geometry
analyzer = SlopeStabilityAnalyzer(height=10, angle=95)
# ValueError: Slope angle must be between 0° and 90°, got 95
```

## Performance Considerations

- **Lazy imports**: PySlope only loaded when needed
- **Efficient validation**: Early validation prevents wasted computation
- **Batch processing**: Disable warnings in loops with `show_warnings=False`
- **Caching**: Results cached in `_last_results` for retrieval

## Future Enhancements

- [ ] Full PySlope integration (currently using simplified calculation)
- [ ] Support for more analysis methods (Janbu, Spencer, etc.)
- [ ] Seismic analysis capability
- [ ] 3D slope analysis
- [ ] Parametric studies automation
- [ ] GUI application
- [ ] Database integration for project management

## Testing

Run the included examples:

```bash
python slope_analyzer.py     # Run built-in examples
python example_usage.py      # Run comprehensive examples
```

## License

Based on PySlope library by Jesse Bonanno. See PySlope documentation for license details.

## Contributing

Contributions welcome! Please:
1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Follow SOLID/DRY principles

## Support

For PySlope-specific questions, see: https://github.com/JesseBonanno/PySlope

For this wrapper, file an issue or submit a pull request.
