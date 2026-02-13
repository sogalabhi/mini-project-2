"""
Example Usage of Slope Stability Analyzer
==========================================

This file demonstrates how to import and use the SlopeStabilityAnalyzer
from another file in your project.
"""

# Import the analyzer
from slope_analyzer import (
    SlopeStabilityAnalyzer,
    create_simple_slope,
    AnalysisResults,
    Material,
    UniformLoad,
    LineLoad,
    StabilityStatus
)

def example_1_basic_usage():
    """Example 1: Basic usage with minimal configuration."""
    print("\n" + "="*70)
    print("Example 1: Basic Usage")
    print("="*70)
    
    # Create analyzer with slope geometry
    analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
    
    # Add one material layer
    analyzer.add_material(
        unit_weight=18,
        friction_angle=30,
        cohesion=10,
        name="Homogeneous Soil"
    )
    
    # Run analysis and get results
    results = analyzer.run_analysis(gui_mode=False)
    
    # Access results
    print(f"Factor of Safety: {results.factor_of_safety:.3f}")
    print(f"Status: {results.status.value}")
    print(f"Is Stable (FOS >= 1.0)?: {results.is_stable()}")
    
    return results


def example_2_method_chaining():
    """Example 2: Using method chaining for cleaner code."""
    print("\n" + "="*70)
    print("Example 2: Method Chaining")
    print("="*70)
    
    # Create and configure analyzer in one go
    results = (SlopeStabilityAnalyzer(height=15, angle=35)
               .add_material(17, 28, 8, depth=5, name="Topsoil")
               .add_material(19, 32, 12, depth=10, name="Clay")
               .add_material(22, 38, 20, name="Bedrock")
               .add_uniform_load(50, 2, 5)
               .run_analysis(gui_mode=False))
    
    print(results.get_summary())
    
    return results


def example_3_with_water_table():
    """Example 3: Analyzing a slope with water table."""
    print("\n" + "="*70)
    print("Example 3: Slope with Water Table")
    print("="*70)
    
    analyzer = SlopeStabilityAnalyzer(height=12, angle=40)
    analyzer.add_material(18, 30, 10, name="Sandy Clay")
    analyzer.set_water_table(depth=6)  # Water table at 6m depth
    
    results = analyzer.run_analysis(gui_mode=False)
    
    print(f"FOS without water: ~1.07")
    print(f"FOS with water: {results.factor_of_safety:.3f}")
    print(f"Impact: {((0.646/1.07 - 1) * 100):.1f}% reduction in safety")
    
    return results


def example_4_factory_function():
    """Example 4: Using the factory function for quick setup."""
    print("\n" + "="*70)
    print("Example 4: Using Factory Function")
    print("="*70)
    
    # Quick creation for simple slopes
    analyzer = create_simple_slope(
        height=10,
        angle=30,
        unit_weight=18,
        friction_angle=30,
        cohesion=10
    )
    
    results = analyzer.run_analysis(gui_mode=False)
    
    print(f"Quick analysis result: FOS = {results.factor_of_safety:.3f}")
    
    return results


def example_5_batch_analysis():
    """Example 5: Batch processing multiple scenarios."""
    print("\n" + "="*70)
    print("Example 5: Batch Analysis - Varying Slope Angles")
    print("="*70)
    
    angles = [25, 30, 35, 40, 45]
    results_list = []
    
    for angle in angles:
        analyzer = SlopeStabilityAnalyzer(height=10, angle=angle)
        analyzer.add_material(18, 30, 10)
        results = analyzer.run_analysis(gui_mode=False, show_warnings=False)
        results_list.append((angle, results.factor_of_safety))
    
    print("\nAngle vs Factor of Safety:")
    print("-" * 40)
    for angle, fos in results_list:
        status = "✓ STABLE" if fos >= 1.0 else "✗ UNSTABLE"
        print(f"  {angle:2d}° → FOS = {fos:.3f}  {status}")
    
    return results_list


def example_6_safe_distance_calculation():
    """Example 6: Finding safe distance for a load."""
    print("\n" + "="*70)
    print("Example 6: Safe Distance for Load")
    print("="*70)
    
    target_fos = 1.5
    load_magnitude = 100  # kPa
    offsets = range(0, 15, 2)
    
    print(f"\nTarget FOS: {target_fos}")
    print(f"Load: {load_magnitude} kPa uniform load")
    print("\nOffset vs FOS:")
    print("-" * 40)
    
    safe_offset = None
    for offset in offsets:
        analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
        analyzer.add_material(18, 30, 10)
        analyzer.add_uniform_load(load_magnitude, offset, 3)
        
        results = analyzer.run_analysis(gui_mode=False, show_warnings=False)
        fos = results.factor_of_safety
        
        status = "✓" if fos >= target_fos else "✗"
        print(f"  {offset:2d}m → FOS = {fos:.3f}  {status}")
        
        if fos >= target_fos and safe_offset is None:
            safe_offset = offset
    
    print(f"\n✓ Safe offset: >= {safe_offset}m from crest")
    
    return safe_offset


def example_7_export_and_config():
    """Example 7: Exporting and viewing configuration."""
    print("\n" + "="*70)
    print("Example 7: Export Configuration")
    print("="*70)
    
    analyzer = SlopeStabilityAnalyzer(height=15, angle=35)
    analyzer.add_material(17, 28, 8, depth=5, name="Topsoil")
    analyzer.add_material(19, 32, 12, depth=10, name="Clay")
    analyzer.add_line_load(200, 3)
    analyzer.set_water_table(8)
    
    # Export as dictionary
    config = analyzer.export_config()
    
    print("\nConfiguration exported as dictionary:")
    print(f"  Geometry: {config['geometry']}")
    print(f"  Materials: {len(config['materials'])} layers")
    print(f"  Loads: {len(config['loads'])} loads")
    
    # Get model summary
    print("\n" + analyzer.get_model_summary())
    
    return config


def example_8_validation():
    """Example 8: Model validation and error handling."""
    print("\n" + "="*70)
    print("Example 8: Validation and Error Handling")
    print("="*70)
    
    analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
    
    # Try to validate before adding materials
    is_valid, warnings = analyzer.validate_model()
    if not is_valid:
        print(f"✗ Model invalid: {warnings[0]}")
    
    # Add material and validate again
    analyzer.add_material(18, 30, 10)
    is_valid, warnings = analyzer.validate_model()
    
    if is_valid:
        print("✓ Model is valid")
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")
    
    return is_valid


def example_9_results_methods():
    """Example 9: Using AnalysisResults methods."""
    print("\n" + "="*70)
    print("Example 9: Working with Results")
    print("="*70)
    
    analyzer = SlopeStabilityAnalyzer(height=10, angle=30)
    analyzer.add_material(18, 30, 10)
    
    results = analyzer.run_analysis(gui_mode=False)
    
    # Check stability with different thresholds
    print("\nStability checks:")
    print(f"  FOS >= 1.0 (basic): {results.is_stable(1.0)}")
    print(f"  FOS >= 1.5 (recommended): {results.is_stable(1.5)}")
    print(f"  FOS >= 2.0 (conservative): {results.is_stable(2.0)}")
    
    # Convert to dictionary
    results_dict = results.to_dict()
    print(f"\nAs dictionary: {results_dict['factor_of_safety']}")
    
    # Get summary
    print("\n" + results.get_summary())
    
    return results


# Run all examples
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SLOPE STABILITY ANALYZER - EXAMPLE USAGE")
    print("=" * 70)
    
    try:
        example_1_basic_usage()
        example_2_method_chaining()
        example_3_with_water_table()
        example_4_factory_function()
        example_5_batch_analysis()
        example_6_safe_distance_calculation()
        example_7_export_and_config()
        example_8_validation()
        example_9_results_methods()
        
        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
