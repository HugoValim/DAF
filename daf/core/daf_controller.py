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

from daf.core.hkl_move import HKLMove
from daf.utils.experiment_file_store import ExperimentFileStore

__all__ = ["DAFController", "MoveHKLResult"]

logger = logging.getLogger(__name__)


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
        self._file_store = (
            file_store if file_store is not None else ExperimentFileStore()
        )

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
        result = HKLMove(file_store=self._file_store).calculate(
            self._file_store.read(), [h, k, l]
        )
        logger.debug(
            "move_hkl(%s, %s, %s): error=%.2e success=%s",
            h,
            k,
            l,
            result.hkl_error,
            result.success,
        )
        return MoveHKLResult(
            success=result.success,
            angles=result.angles,
            hkl_error=result.hkl_error,
        )
