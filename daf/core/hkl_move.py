"""HKL calculation and movement workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from daf.core.daf_engine_factory import DAFEngineFactory
from daf.utils.experiment_config import ExperimentConfig, MOTOR_NAMES
from daf.utils.experiment_file_store import ExperimentFileStore


MAX_HKL_ERROR = 1e-4


@dataclass(frozen=True)
class HKLMoveResult:
    success: bool
    angles: dict[str, Any]
    hkl_error: float
    engine: Any


class HKLMove:
    """Calculate HKL targets and optionally persist motor setpoints."""

    def __init__(
        self,
        file_store: Any | None = None,
        max_error: float = MAX_HKL_ERROR,
    ) -> None:
        self._file_store = (
            file_store if file_store is not None else ExperimentFileStore()
        )
        self._max_error = max_error

    def calculate(
        self, experiment_data: dict[str, Any], hkl: list[float]
    ) -> HKLMoveResult:
        config = ExperimentConfig.from_dict(experiment_data)
        engine = DAFEngineFactory.from_config(config)
        start_values = [config.motor_values[motor] for motor in MOTOR_NAMES]
        engine.set_hkl(hkl)
        engine(start_values=start_values)
        solution = engine.solution()
        return HKLMoveResult(
            success=solution.success(self._max_error),
            angles=solution.to_angle_dict(),
            hkl_error=solution.qerror,
            engine=engine,
        )

    def move(self, hkl: list[float]) -> HKLMoveResult:
        data = self._file_store.read()
        result = self.calculate(data, hkl)
        if result.success:
            config = ExperimentConfig.from_dict(data)
            self._file_store.write(config.with_motor_setpoints(result.angles))
        return result
