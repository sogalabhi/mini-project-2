import csv
from pathlib import Path
from typing import List, Tuple

from ..domain.errors import InputValidationError
from ..domain.models import DEMPoint
from .validators import validate_dem_points


def _coerce_float(value: str, file_path: Path, row_idx: int, col_idx: int) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise InputValidationError(
            f"Invalid numeric value '{value}' in {file_path} at row {row_idx + 1}, col {col_idx + 1}"
        ) from exc


def read_xyz_csv(path: str) -> List[DEMPoint]:
    file_path = Path(path)
    if not file_path.exists():
        raise InputValidationError(f"Surface file not found: {file_path}")

    points: List[DEMPoint] = []
    with file_path.open("r", newline="") as handle:
        reader = csv.reader(handle)
        for row_idx, row in enumerate(reader):
            row = [item.strip() for item in row if item.strip() != ""]
            if not row:
                continue
            if len(row) < 3:
                raise InputValidationError(
                    f"Expected at least 3 values (x,y,z) in {file_path} at row {row_idx + 1}"
                )
            x = _coerce_float(row[0], file_path, row_idx, 0)
            y = _coerce_float(row[1], file_path, row_idx, 1)
            z = _coerce_float(row[2], file_path, row_idx, 2)
            points.append(DEMPoint(x=x, y=y, z=z))

    validate_dem_points(points, label=file_path.name)
    return points


def read_xy_curve_csv(path: str) -> List[Tuple[float, float]]:
    file_path = Path(path)
    if not file_path.exists():
        raise InputValidationError(f"Curve file not found: {file_path}")

    rows: List[Tuple[float, float]] = []
    with file_path.open("r", newline="") as handle:
        reader = csv.reader(handle)
        for row_idx, row in enumerate(reader):
            row = [item.strip() for item in row if item.strip() != ""]
            if not row:
                continue
            if len(row) < 2:
                raise InputValidationError(
                    f"Expected at least 2 values in {file_path} at row {row_idx + 1}"
                )
            x = _coerce_float(row[0], file_path, row_idx, 0)
            y = _coerce_float(row[1], file_path, row_idx, 1)
            rows.append((x, y))

    if not rows:
        raise InputValidationError(f"Curve file has no numeric rows: {file_path}")
    return rows

