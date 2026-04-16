import csv
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from ..domain.models import DEMPoint


def write_xyz_csv(path: str, points: Iterable[DEMPoint]) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        for point in points:
            writer.writerow([point.x, point.y, point.z])
    return out_path


def write_rows_csv(path: str, rows: Sequence[Mapping[str, object]]) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with out_path.open("w", newline="") as handle:
            handle.write("")
        return out_path

    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return out_path

