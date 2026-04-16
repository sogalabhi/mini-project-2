from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    """
    Runtime flags for the 3D LEM rewrite.

    This is intentionally small in Phase 1 and can be expanded as modules land.
    """

    debug_mode: bool = False
    strict_validation: bool = True
    export_intermediate_csv: bool = False
    output_directory: str = "outputs/3d_lem"

    def output_path(self) -> Path:
        return Path(self.output_directory)

