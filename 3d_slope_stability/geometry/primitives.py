import math
from typing import Sequence, Tuple

import numpy as np

from ..domain.errors import GeometryError


def deg_to_rad(value_deg: float) -> float:
    return math.radians(value_deg)


def rad_to_deg(value_rad: float) -> float:
    return math.degrees(value_rad)


def tetra_volume(
    a: Tuple[float, float, float],
    b: Tuple[float, float, float],
    c: Tuple[float, float, float],
    d: Tuple[float, float, float],
) -> float:
    """Signed tetra volume magnitude from 4 points."""
    av = np.asarray(a, dtype=float)
    bv = np.asarray(b, dtype=float)
    cv = np.asarray(c, dtype=float)
    dv = np.asarray(d, dtype=float)
    mat = np.stack([bv - av, cv - av, dv - av], axis=1)
    return abs(float(np.linalg.det(mat))) / 6.0


def area_3d_polygon(points: Sequence[Tuple[float, float, float]]) -> float:
    """
    Area of a 3D planar polygon using triangulation from first vertex.
    """
    if len(points) < 3:
        raise GeometryError("Polygon needs at least 3 points")
    p0 = np.asarray(points[0], dtype=float)
    area = 0.0
    for idx in range(1, len(points) - 1):
        p1 = np.asarray(points[idx], dtype=float)
        p2 = np.asarray(points[idx + 1], dtype=float)
        area += np.linalg.norm(np.cross(p1 - p0, p2 - p0)) / 2.0
    return float(area)


def dip_and_direction_from_points(
    p1: Tuple[float, float, float],
    p2: Tuple[float, float, float],
    p3: Tuple[float, float, float],
) -> Tuple[float, float]:
    """
    Return dip and dip-direction in radians from 3 points on a plane.
    """
    v1 = np.asarray(p2, dtype=float) - np.asarray(p1, dtype=float)
    v2 = np.asarray(p3, dtype=float) - np.asarray(p1, dtype=float)
    n = np.cross(v1, v2)
    n_norm = np.linalg.norm(n)
    if n_norm == 0:
        raise GeometryError("Points are colinear; plane normal undefined")
    n = n / n_norm

    # Dip is angle from horizontal plane.
    dip = math.atan2(math.sqrt(n[0] ** 2 + n[1] ** 2), abs(n[2]))

    # Dip direction from +Y axis clockwise, normalized to [0, 2*pi).
    strike_like = math.atan2(n[0], n[1])
    dip_dir = (strike_like + math.pi) % (2.0 * math.pi)
    return float(dip), float(dip_dir)

