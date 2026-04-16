from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _base_3d_payload(method_id: int = 1) -> dict:
    return {
        "method_config": {
            "method_id": method_id,
            "solver": {"max_iterations": 80, "tol_fs": 0.001, "damping": 1.0},
            "direction": {"spacing_deg": 2.0, "tolerance_deg": 4.0, "user_direction_deg": None},
            "use_side_resistance": True,
        },
        "grid_config": {
            "x_min": 0.0,
            "x_max": 2.0,
            "y_min": 0.0,
            "y_max": 2.0,
            "z_min": 0.0,
            "z_max": 20.0,
            "col_x_max": 8,
            "col_y_max": 8,
        },
        "slip_surface_config": {
            "mode": "ellipsoid",
            "ellipsoid_center": [1.0, 1.0, 9.0],
            "ellipsoid_radii": [2.0, 2.0, 3.0],
            "user_defined_surface_path": None,
            "user_defined_interpolation": "a1",
        },
        "materials": {
            "default": {
                "name": "default",
                "model_type": 1,
                "model_parameters": [30.0, 5.0],
                "unit_weight": 18.0,
            }
        },
        "top_surface": {
            "label": "tt",
            "path": "synthetic_top.csv",
            "interpolation_mode": "a1",
            "points": [
                {"x": 0.0, "y": 0.0, "z": 10.0},
                {"x": 2.0, "y": 0.0, "z": 10.0},
                {"x": 0.0, "y": 2.0, "z": 9.5},
                {"x": 2.0, "y": 2.0, "z": 9.5},
            ],
        },
        "user_slip_surface": None,
        "surface_paths": None,
        "surface_types": None,
        "interpolation_modes": None,
        "water_level_z": None,
        "reinforcement": {
            "enabled": False,
            "diameter": 0.025,
            "length_embed": 6.0,
            "spacing_x": 2.0,
            "spacing_y": 2.0,
            "steel_area": 0.0005,
            "yield_strength": 500000.0,
            "bond_strength": 150.0,
            "inclination_deg": 0.0,
            "include_vertical_component": False,
        },
        "debug": {"include_analysis_rows": False},
    }


def test_3d_methods_endpoint_returns_frozen_method_ids() -> None:
    response = client.get("/api/v1/3d/methods")
    assert response.status_code == 200
    payload = response.json()
    assert "methods" in payload
    ids = sorted([entry["id"] for entry in payload["methods"]])
    assert ids == [1, 2, 3, 4, 5, 6, 7]


def test_3d_analyze_happy_path_returns_normalized_result() -> None:
    response = client.post("/api/v1/3d/analyze", json=_base_3d_payload())
    assert response.status_code == 200
    body = response.json()
    assert "fs_min" in body
    assert "critical_direction_rad" in body
    assert "direction_results" in body
    assert "diagnostics" in body
    assert "analysis_rows" not in body
    assert "t_max" in body["diagnostics"]["method"]


def test_3d_analyze_invalid_method_schema_rejected() -> None:
    payload = _base_3d_payload()
    payload["method_config"]["method_id"] = 99
    response = client.post("/api/v1/3d/analyze", json=payload)
    assert response.status_code == 422


def test_3d_validate_reports_invalid_when_debug_rows_exceed_limit() -> None:
    payload = _base_3d_payload()
    payload["debug"]["include_analysis_rows"] = True
    payload["grid_config"]["col_x_max"] = 300
    payload["grid_config"]["col_y_max"] = 300

    response = client.post("/api/v1/3d/validate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert len(body["errors"]) >= 1


def test_3d_analyze_failure_path_returns_structured_error() -> None:
    payload = _base_3d_payload()
    payload["slip_surface_config"] = {
        "mode": "user_defined",
        "ellipsoid_center": None,
        "ellipsoid_radii": None,
        "user_defined_surface_path": "missing_surface.csv",
        "user_defined_interpolation": "a1",
    }
    payload["user_slip_surface"] = None
    response = client.post("/api/v1/3d/analyze", json=payload)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "code" in detail
    assert "message" in detail


def test_3d_multi_returns_partial_results_for_invalid_method_id() -> None:
    response = client.post(
        "/api/v1/3d/analyze/multi",
        json={"method_ids": [1, 99], "base_request": _base_3d_payload(method_id=1)},
    )
    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert len(body["results"]) == 2
    assert any(item["ok"] is True for item in body["results"])
    assert any(item["ok"] is False for item in body["results"])


def test_3d_analyze_reinforcement_payload_applied_and_reported() -> None:
    payload = _base_3d_payload(method_id=1)
    payload["reinforcement"]["enabled"] = True
    payload["reinforcement"]["steel_area"] = 0.0004
    payload["reinforcement"]["yield_strength"] = 200000.0
    response = client.post("/api/v1/3d/analyze", json=payload)
    assert response.status_code == 200
    body = response.json()
    method_diag = body["diagnostics"]["method"]
    assert method_diag["enabled"] == 1.0
    assert method_diag["t_max"] > 0.0


def test_3d_analyze_reinforcement_invalid_schema_rejected() -> None:
    payload = _base_3d_payload(method_id=1)
    payload["reinforcement"]["spacing_x"] = -1.0
    response = client.post("/api/v1/3d/analyze", json=payload)
    assert response.status_code == 422

