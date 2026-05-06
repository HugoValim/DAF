"""DAFController — programmatic seam between the GUI and the DAF engine.

The GUI previously called ``subprocess.Popen(["daf.mv", H, K, L])`` to move
the diffractometer to a given HKL position.  That approach is fire-and-forget
and cannot be unit-tested without spawning real processes.

``DAFController`` replaces that pattern by exposing typed methods that the GUI
can call in-process.  The controller delegates engine construction to the same
logic used by the CLI (``CLIBase.build_exp``), but reads the experiment file
via an injectable ``ExperimentFileStore`` so tests can supply a mock.

Typical usage
-------------
::

    from daf.core.daf_controller import DAFController

    ctrl = DAFController()
    result = ctrl.move_hkl(1.0, 1.0, 1.0)
    if result.success:
        print("New angles:", result.angles)

"""
from __future__ import annotations

import dataclasses
import logging
from typing import Any

import numpy as np

from daf.core.main import DAF
from daf.utils.experiment_file_store import ExperimentFileStore

__all__ = ["DAFController", "MoveHKLResult"]

logger = logging.getLogger(__name__)

# Motor names in canonical order (matches CLIBase._MOTOR_NAMES)
_MOTOR_NAMES: tuple[str, ...] = ("mu", "eta", "chi", "phi", "nu", "del")

# Angle names exported by DAF.export_angles(), in index order
_ANGLE_EXPORT_NAMES: tuple[str, ...] = (
    "mu",
    "eta",
    "chi",
    "phi",
    "nu",
    "del",
    "twotheta",
    "theta",
    "alpha",
    "qaz",
    "naz",
    "tau",
    "psi",
    "beta",
    "omega",
    "hklnow",
)

# An HKL minimisation is considered successful when the residual is below this
_MAX_HKL_ERROR: float = 1e-4


@dataclasses.dataclass
class MoveHKLResult:
    """Structured result returned by :meth:`DAFController.move_hkl`.

    Attributes:
        success: ``True`` when the minimiser converged within tolerance.
        angles: Dict of angle name → computed value (all six motors plus
            pseudo-angles when available).
        hkl_error: Residual Q-error from the minimisation.
    """

    success: bool
    angles: dict[str, Any]
    hkl_error: float


class DAFController:
    """Programmatic interface to the DAF diffractometer engine.

    The controller is the single entry point for GUI code that previously
    relied on subprocess calls.  It is designed to be easily testable: pass a
    ``file_store`` mock to avoid touching the filesystem.

    Args:
        file_store: Object with a ``read() -> dict`` method.  Defaults to
            :class:`~daf.utils.experiment_file_store.ExperimentFileStore`.
    """

    def __init__(
        self,
        file_store: Any | None = None,
    ) -> None:
        self._file_store = file_store if file_store is not None else ExperimentFileStore()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def move_hkl(self, h: float, k: float, l: float) -> MoveHKLResult:
        """Calculate diffractometer angles to reach the HKL position (h, k, l).

        This method is the in-process replacement for::

            subprocess.Popen(["daf.mv", str(h), str(k), str(l)])

        It does *not* move physical motors; motor actuation remains the
        responsibility of the EPICS layer (``DAFIO.write``).  The returned
        angles can be inspected or forwarded to the hardware layer as needed.

        Args:
            h: H component of the reciprocal-space vector.
            k: K component of the reciprocal-space vector.
            l: L component of the reciprocal-space vector.

        Returns:
            A :class:`MoveHKLResult` with ``success``, ``angles``, and
            ``hkl_error`` fields.
        """
        exp_dict = self._file_store.read()
        engine = self._build_engine(exp_dict)
        error = self._calculate_hkl(engine, exp_dict, [h, k, l])
        angles = self._export_angles(engine)
        success = float(error) <= _MAX_HKL_ERROR
        logger.debug(
            "move_hkl(%s, %s, %s): error=%.2e success=%s", h, k, l, error, success
        )
        return MoveHKLResult(success=success, angles=angles, hkl_error=float(error))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_engine(self, exp_dict: dict) -> DAF:
        """Construct and configure a :class:`~daf.core.main.DAF` instance."""
        from daf.core.daf_engine_factory import DAFEngineFactory
        return DAFEngineFactory.from_dict(exp_dict)

    @staticmethod
    def _get_motor_values(exp_dict: dict) -> dict:
        return {m: exp_dict["motors"][m]["value"] for m in _MOTOR_NAMES}

    def _calculate_hkl(
        self, engine: DAF, exp_dict: dict, hkl: list[float]
    ) -> float:
        """Run the HKL minimisation and return the residual Q-error."""
        motor_vals = self._get_motor_values(exp_dict)
        start_values = [motor_vals[m] for m in _MOTOR_NAMES]
        engine.set_hkl(hkl)
        engine(start_values=start_values)
        return engine.qerror

    @staticmethod
    def _export_angles(engine: DAF) -> dict:
        """Return a dict mapping angle names to their computed values."""
        raw = engine.export_angles()
        return {name: raw[i] for i, name in enumerate(_ANGLE_EXPORT_NAMES)}
