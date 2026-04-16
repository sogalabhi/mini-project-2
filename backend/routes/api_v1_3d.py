import importlib
from typing import Dict, List

from fastapi import APIRouter

from ..adapters.three_d_mapper import ALLOWED_METHOD_IDS, build_pipeline_kwargs, normalize_exception, normalize_pipeline_result
from ..schemas.analysis_3d import Analyze3DMultiRequest, Analyze3DRequest, Validate3DResponse

_pipeline = importlib.import_module("3d_slope_stability.pipeline")
_enums = importlib.import_module("3d_slope_stability.domain.enums")
run_pipeline = _pipeline.run_pipeline
MethodId = _enums.MethodId

router = APIRouter(prefix="/api/v1/3d", tags=["3d"])


@router.get("/methods")
def get_3d_methods() -> Dict[str, List[Dict[str, object]]]:
    methods = [{"id": int(method.value), "label": method.name} for method in MethodId]
    return {"methods": methods}


@router.post("/validate", response_model=Validate3DResponse)
def validate_3d_payload(data: Analyze3DRequest) -> Validate3DResponse:
    try:
        build_pipeline_kwargs(data)
    except Exception as exc:
        http_exc = normalize_exception(exc)
        detail = http_exc.detail if isinstance(http_exc.detail, dict) else {"message": str(http_exc.detail)}
        message = str(detail.get("message", "invalid payload"))
        return Validate3DResponse(valid=False, errors=[message])
    return Validate3DResponse(valid=True, errors=[])


@router.post("/analyze")
def analyze_3d(data: Analyze3DRequest):
    try:
        kwargs = build_pipeline_kwargs(data)
        result = run_pipeline(**kwargs)
        return normalize_pipeline_result(result, include_rows=data.debug.include_analysis_rows)
    except Exception as exc:
        raise normalize_exception(exc) from exc


@router.post("/analyze/multi")
def analyze_3d_multi(data: Analyze3DMultiRequest):
    summaries = []
    for method_id in data.method_ids:
        if method_id not in ALLOWED_METHOD_IDS:
            summaries.append(
                {
                    "method_id": method_id,
                    "ok": False,
                    "error": {"code": "invalid_method", "message": "method_id must be one of {1,2,3,4,5,6,7}"},
                }
            )
            continue

        try:
            per_method = data.base_request.model_copy(deep=True)
            per_method.method_config.method_id = method_id
            kwargs = build_pipeline_kwargs(per_method)
            result = run_pipeline(**kwargs)
            normalized = normalize_pipeline_result(result, include_rows=per_method.debug.include_analysis_rows)
            summaries.append(
                {
                    "method_id": method_id,
                    "ok": True,
                    "fs_min": normalized["fs_min"],
                    "critical_direction_rad": normalized["critical_direction_rad"],
                    "converged": normalized["converged"],
                    "diagnostics": normalized["diagnostics"],
                }
            )
        except Exception as exc:
            http_exc = normalize_exception(exc)
            detail = http_exc.detail if isinstance(http_exc.detail, dict) else {"message": str(http_exc.detail)}
            summaries.append({"method_id": method_id, "ok": False, "error": detail})

    return {"results": summaries}

