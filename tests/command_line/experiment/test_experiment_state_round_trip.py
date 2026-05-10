import copy
import sys
from unittest.mock import patch

from daf.command_line.experiment.bounds import Bounds
from daf.command_line.experiment.experiment_configuration import (
    ExperimentConfiguration,
)
from daf.utils.experiment_file_store import ExperimentFileStore


def test_bounds_cli_update_preserves_unrelated_experiment_state(
    temp_experiment_file, monkeypatch
):
    filepath, data = temp_experiment_file
    updated_data = copy.deepcopy(data)
    updated_data["Material"] = "Ge"
    updated_data["energy_offset"] = 123.0
    updated_data["motors"]["eta"]["value"] = 17.0
    updated_data["U_mat"] = [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    updated_data["UB_mat"] = [[2.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]]
    ExperimentFileStore(filepath).write(updated_data)
    monkeypatch.chdir(filepath.parent)

    testargs = ["daf.bounds", "--mu", "-10", "20"]
    with patch.object(sys, "argv", testargs):
        command = Bounds()
        command.run_cmd()

    persisted = ExperimentFileStore(filepath).read()

    assert persisted["motors"]["mu"]["bounds"] == [-10.0, 20.0]
    assert persisted["Material"] == "Ge"
    assert persisted["energy_offset"] == 123.0
    assert persisted["motors"]["eta"]["value"] == 17.0
    assert persisted["U_mat"] == updated_data["U_mat"]
    assert persisted["UB_mat"] == updated_data["UB_mat"]


def test_energy_cli_update_preserves_bounds_motors_and_orientation_state(
    temp_experiment_file, monkeypatch
):
    filepath, data = temp_experiment_file
    updated_data = copy.deepcopy(data)
    updated_data["beamline_pvs"]["energy"]["value"] = 10000.0
    updated_data["motors"]["mu"]["value"] = 12.0
    updated_data["motors"]["mu"]["bounds"] = [-30.0, 45.0]
    updated_data["U_mat"] = [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    updated_data["UB_mat"] = [[3.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 3.0]]
    ExperimentFileStore(filepath).write(updated_data)
    monkeypatch.chdir(filepath.parent)

    testargs = ["daf.expt", "--energy", "9000"]
    with patch.object(sys, "argv", testargs):
        command = ExperimentConfiguration()
        command.run_cmd()

    persisted = ExperimentFileStore(filepath).read()

    assert persisted["energy_offset"] == 1000.0
    assert persisted["motors"]["mu"]["value"] == 12.0
    assert persisted["motors"]["mu"]["bounds"] == [-30.0, 45.0]
    assert persisted["U_mat"] == updated_data["U_mat"]
    assert persisted["UB_mat"] == updated_data["UB_mat"]
