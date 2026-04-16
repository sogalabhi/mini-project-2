from typing import Dict, List, Mapping

from ..config.method_options import DirectionSearchConfig, MethodRunConfig, SolverConfig
from ..config.schema import GridConfig, SlipSurfaceConfig
from ..domain.models import MaterialDefinition, SurfaceDataset
from .timers import profile_pipeline_stages


def run_benchmark_matrix(
    *,
    top_surface: SurfaceDataset,
    materials: Mapping[str, MaterialDefinition],
    seed: int = 42,
) -> List[Dict[str, float]]:
    """
    Benchmark matrix across:
    - grid sizes: small, medium, large
    - methods: Bishop, Janbu, Spencer-like
    - tolerance and iteration settings
    Deterministic by design; seed argument retained for explicit reproducibility policy.
    """
    _ = seed
    grid_sizes = {
        "small": (8, 8),
        "medium": (16, 16),
        "large": (24, 24),
    }
    methods = [1, 2, 7]
    solver_profiles = [
        {"max_iterations": 80, "tol_fs": 1e-3},
        {"max_iterations": 120, "tol_fs": 5e-4},
    ]

    out: List[Dict[str, float]] = []
    for size_name, (cx, cy) in grid_sizes.items():
        grid = GridConfig(
            x_min=0,
            x_max=2,
            y_min=0,
            y_max=2,
            z_min=0,
            z_max=20,
            col_x_max=cx,
            col_y_max=cy,
        )
        slip = SlipSurfaceConfig(
            mode="ellipsoid",
            ellipsoid_center=(1.0, 1.0, 9.0),
            ellipsoid_radii=(2.0, 2.0, 3.0),
        )
        for method_id in methods:
            for sp in solver_profiles:
                cfg = MethodRunConfig(
                    method_id=method_id,
                    solver=SolverConfig(
                        max_iterations=sp["max_iterations"],
                        tol_fs=sp["tol_fs"],
                        damping=1.0,
                    ),
                    direction=DirectionSearchConfig(spacing_deg=2.0, tolerance_deg=4.0),
                )
                timings = profile_pipeline_stages(
                    method_config=cfg,
                    grid_config=grid,
                    slip_surface_config=slip,
                    materials=materials,
                    top_surface=top_surface,
                )
                out.append(
                    {
                        "grid_size": float({"small": 1, "medium": 2, "large": 3}[size_name]),
                        "method_id": float(method_id),
                        "max_iterations": float(sp["max_iterations"]),
                        "tol_fs": float(sp["tol_fs"]),
                        **timings,
                    }
                )
    return out

