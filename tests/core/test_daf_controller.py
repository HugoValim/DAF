"""Unit tests for DAFController.move_hkl().

All EPICS interactions are mocked by the session-scoped conftest.
No subprocess calls, no Docker, no real hardware required.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from daf.core.daf_controller import DAFController, MoveHKLResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def experiment_data() -> dict:
    """Minimal but valid experiment-file dict for Si in mode 2052."""
    return {
        "Mode": "2052",
        "Material": "Si",
        "IDir": [0, 1, 0],
        "IDir_print": [0, 1, 0],
        "NDir": [0, 0, 1],
        "NDir_print": [0, 0, 1],
        "RDir": [0, 0, 1],
        "Sampleor": "z+",
        "energy_offset": 0.0,
        "hklnow": [0, 0, 0],
        "reflections": [],
        "Print_marker": "",
        "Print_cmarker": "",
        "Print_space": "",
        "hkl": "",
        "cons_mu": 0.0,
        "cons_eta": 0.0,
        "cons_chi": 0.0,
        "cons_phi": 0.0,
        "cons_nu": 0.0,
        "cons_del": 0.0,
        "cons_alpha": 0.0,
        "cons_beta": 0.0,
        "cons_psi": 0.0,
        "cons_omega": 0.0,
        "cons_qaz": 0.0,
        "cons_naz": 0.0,
        "twotheta": 0.0,
        "theta": 0.0,
        "alpha": 0.0,
        "qaz": 90.0,
        "naz": 0.0,
        "tau": 0.0,
        "psi": 0.0,
        "beta": 0.0,
        "omega": 0.0,
        "U_mat": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        "UB_mat": [
            [1.15690279, 0.0, 0.0],
            [0.0, 1.15690279, 0.0],
            [0.0, 0.0, 1.15690279],
        ],
        "lparam_a": 0.0,
        "lparam_b": 0.0,
        "lparam_c": 0.0,
        "lparam_alpha": 0.0,
        "lparam_beta": 0.0,
        "lparam_gama": 0.0,
        "Max_diff": 0.1,
        "scan_name": "scan_test",
        "separator": ",",
        "macro_flag": False,
        "macro_file": "macro",
        "setup": "default",
        "user_samples": {},
        "setup_desc": "This is DAF default setup",
        "default_counters": "config.daf_default.yml",
        "dark_mode": 0,
        "scan_stats": {},
        "PV_energy": 0.0,
        "scan_running": False,
        "scan_counters": [],
        "current_scan_file": "",
        "main_scan_counter": None,
        "main_scan_motor": "",
        "simulated": False,
        "kafka_topic": "EMA_bluesky",
        "scan_db": "temp",
        "version": "1.0.0",
        "motors": {
            "mu": {"pv": "SIM:m1", "value": 0.0, "bounds": [-180, 180], "up": True},
            "eta": {"pv": "SIM:m2", "value": 0.0, "bounds": [-180, 180], "up": True},
            "chi": {"pv": "SIM:m3", "value": 0.0, "bounds": [-5, 95], "up": True},
            "phi": {"pv": "SIM:m4", "value": 0.0, "bounds": [30, 400], "up": True},
            "nu": {"pv": "SIM:m5", "value": 0.0, "bounds": [-180, 180], "up": True},
            "del": {"pv": "SIM:m6", "value": 0.0, "bounds": [-180, 180], "up": True},
        },
        "beamline_pvs": {
            "energy": {
                "pv": "SIM:energy",
                "value": 8000,
                "up": True,
                "simulated": False,
            },
        },
    }


@pytest.fixture()
def mock_file_store(experiment_data: dict) -> MagicMock:
    """A mock ExperimentFileStore that returns the test experiment dict."""
    store = MagicMock()
    store.read.return_value = experiment_data
    return store


# ---------------------------------------------------------------------------
# Tests — MoveHKLResult dataclass
# ---------------------------------------------------------------------------


class TestMoveHKLResult:
    def test_success_flag_true_for_successful_move(self) -> None:
        result = MoveHKLResult(
            success=True,
            angles={"mu": 0.0, "eta": 11.4, "chi": 35.3, "phi": 45.0, "nu": 0.0, "del": 22.8},
            hkl_error=1e-9,
        )
        assert result.success is True

    def test_success_flag_false_for_failed_move(self) -> None:
        result = MoveHKLResult(success=False, angles={}, hkl_error=1.0)
        assert result.success is False

    def test_angles_dict_is_accessible(self) -> None:
        angles = {"mu": 0.0, "eta": 11.4}
        result = MoveHKLResult(success=True, angles=angles, hkl_error=1e-9)
        assert result.angles == angles


# ---------------------------------------------------------------------------
# Tests — DAFController
# ---------------------------------------------------------------------------


class TestDAFController:
    def test_controller_accepts_file_store(self, mock_file_store: MagicMock) -> None:
        """Controller can be instantiated with a custom file store (testable seam)."""
        controller = DAFController(file_store=mock_file_store)
        assert controller is not None

    def test_move_hkl_returns_move_hkl_result(self, mock_file_store: MagicMock) -> None:
        """move_hkl() always returns a MoveHKLResult instance."""
        controller = DAFController(file_store=mock_file_store)
        result = controller.move_hkl(1.0, 1.0, 1.0)
        assert isinstance(result, MoveHKLResult)

    def test_move_hkl_success_for_reachable_reflection(
        self, mock_file_store: MagicMock
    ) -> None:
        """(1,1,1) should be reachable in mode 2052 for Si at 8 keV."""
        controller = DAFController(file_store=mock_file_store)
        result = controller.move_hkl(1.0, 1.0, 1.0)
        assert result.success is True

    def test_move_hkl_returns_six_motor_angles(
        self, mock_file_store: MagicMock
    ) -> None:
        """Result angles dict must contain all six diffractometer motors."""
        expected_motors = {"mu", "eta", "chi", "phi", "nu", "del"}
        controller = DAFController(file_store=mock_file_store)
        result = controller.move_hkl(1.0, 1.0, 1.0)
        assert expected_motors.issubset(result.angles.keys())

    def test_move_hkl_error_is_small_for_valid_hkl(
        self, mock_file_store: MagicMock
    ) -> None:
        """Minimisation error must be below 1e-4 for a valid HKL."""
        controller = DAFController(file_store=mock_file_store)
        result = controller.move_hkl(1.0, 1.0, 1.0)
        assert result.hkl_error < 1e-4

    def test_move_hkl_failure_for_unreachable_hkl(
        self, mock_file_store: MagicMock, experiment_data: dict
    ) -> None:
        """An HKL that the minimizer cannot reach returns success=False."""
        # Tighten all bounds to zero so no angle can move
        for motor in experiment_data["motors"]:
            experiment_data["motors"][motor]["bounds"] = [0.0, 0.0]
        mock_file_store.read.return_value = experiment_data

        controller = DAFController(file_store=mock_file_store)
        result = controller.move_hkl(10.0, 10.0, 10.0)
        assert result.success is False

    def test_move_hkl_does_not_call_subprocess(
        self, mock_file_store: MagicMock
    ) -> None:
        """move_hkl() must never spawn a subprocess — it is the subprocess replacement."""
        with patch("subprocess.Popen") as mock_popen:
            controller = DAFController(file_store=mock_file_store)
            controller.move_hkl(1.0, 1.0, 1.0)
            mock_popen.assert_not_called()

    def test_file_store_read_is_called_on_move(
        self, mock_file_store: MagicMock
    ) -> None:
        """Controller reads experiment state from the file store on each move."""
        controller = DAFController(file_store=mock_file_store)
        controller.move_hkl(1.0, 1.0, 1.0)
        mock_file_store.read.assert_called_once()
