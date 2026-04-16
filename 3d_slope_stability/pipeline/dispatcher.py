from ..config.method_options import MethodRunConfig
from ..domain.models import AnalysisRow, MethodComputationResult
from ..solvers import (
    run_cheng_yip,
    run_hungr_bishop,
    run_hungr_janbu_corrected,
    run_hungr_janbu_simplified,
)


def dispatch_method(rows: list[AnalysisRow], config: MethodRunConfig) -> MethodComputationResult:
    if config.method_id == 1:
        return run_hungr_bishop(rows, config)
    if config.method_id == 2:
        return run_hungr_janbu_simplified(rows, config)
    if config.method_id == 3:
        return run_hungr_janbu_corrected(rows, config)
    if config.method_id in {4, 5, 6, 7}:
        return run_cheng_yip(rows, config)
    raise ValueError(f"Unsupported method id: {config.method_id}")

