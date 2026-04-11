"""
Unit test configuration for DAF.
This conftest provides mocks for EPICS and other integration dependencies.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Mock epics module before any daf imports
mock_epics = MagicMock()
sys.modules["epics"] = mock_epics
sys.modules["epics.ca"] = MagicMock()
sys.modules["epics.pv"] = MagicMock()

# Mock pyepics
mock_pyepics = MagicMock()
sys.modules["pyepics"] = mock_pyepics

# Create a proper mock for the DAFIO class that doesn't need epics
from daf.utils import dafutilities

original_dafio_init = dafutilities.DAFIO.__init__


def mock_dafio_init(self, read=True):
    if read:
        self.epics_put_flag = False
        self.epics_get_flag = False
    else:
        self.epics_put_flag = False
        self.epics_get_flag = False


# Apply the mock
dafutilities.DAFIO.__init__ = mock_dafio_init


@pytest.fixture(autouse=True)
def mock_epics_pvs(monkeypatch):
    """Mock EPICS PVs for all tests"""
    mock_pv = MagicMock()
    mock_pv.get.return_value = 0
    mock_pv.put.return_value = None

    def mock_caget(pvname, timeout=None):
        return 0

    def mock_caput(pvname, value, timeout=None, wait=None):
        return None

    def mock_caget_many(pvnames, timeout=None):
        return [0] * len(pvnames)

    def mock_caput_many(
        pvnames, values, timeout=None, wait=None, connection_timeout=None
    ):
        return None

    mock_epics.caget = mock_caget
    mock_epics.caput = mock_caput
    mock_epics.caget_many = mock_caget_many
    mock_epics.caput_many = mock_caput_many

    yield mock_epics


@pytest.fixture
def temp_experiment_file(tmp_path, monkeypatch):
    """Create a temporary experiment file for testing"""
    import yaml

    experiment_data = {
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

    exp_file = tmp_path / ".Experiment"
    with open(exp_file, "w") as f:
        yaml.dump(experiment_data, f)

    return exp_file, experiment_data
