import argparse
import json
from pathlib import Path

from ..config.method_options import DirectionSearchConfig, MethodRunConfig, SolverConfig
from ..config.schema import GridConfig, SlipSurfaceConfig
from ..domain.models import MaterialDefinition
from .runner import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run 3D LEM pipeline from JSON config.")
    parser.add_argument("--config", required=True, help="Path to pipeline config JSON")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    config = json.loads(cfg_path.read_text())

    method_cfg = MethodRunConfig(
        method_id=int(config["method"]["method_id"]),
        solver=SolverConfig(
            max_iterations=int(config["method"].get("max_iterations", 200)),
            tol_fs=float(config["method"].get("tol_fs", 1e-3)),
            damping=float(config["method"].get("damping", 1.0)),
        ),
        direction=DirectionSearchConfig(
            spacing_deg=float(config["method"].get("spacing_deg", 0.5)),
            tolerance_deg=float(config["method"].get("tolerance_deg", 10.0)),
            user_direction_deg=config["method"].get("user_direction_deg"),
        ),
    )
    grid_cfg = GridConfig(**config["grid"])
    slip_cfg = SlipSurfaceConfig(**config["slip_surface"])
    materials = {
        item["name"]: MaterialDefinition(
            name=item["name"],
            model_type=int(item["model_type"]),
            model_parameters=tuple(float(v) for v in item["model_parameters"]),
            unit_weight=float(item["unit_weight"]),
        )
        for item in config["materials"]
    }

    result = run_pipeline(
        method_config=method_cfg,
        grid_config=grid_cfg,
        slip_surface_config=slip_cfg,
        materials=materials,
        surface_paths=config.get("surface_paths"),
        surface_types=config.get("surface_types"),
        interpolation_modes=config.get("interpolation_modes"),
        water_level_z=config.get("water_level_z"),
        export_rows_path=config.get("export_rows_path"),
    )
    print(
        json.dumps(
            {
                "column_count": result.column_count,
                "fs_min": None if result.method_result is None else result.method_result.fs_min,
                "critical_direction_rad": None
                if result.method_result is None
                else result.method_result.critical_direction_rad,
                "generated_files": result.generated_files,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

