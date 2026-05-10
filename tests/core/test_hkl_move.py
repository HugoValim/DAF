from unittest.mock import MagicMock

from daf.utils.experiment_file_store import ExperimentFileStore
from daf.core.hkl_move import HKLMove


def test_hkl_move_calculates_solution_from_experiment_config(temp_experiment_file):
    _, data = temp_experiment_file

    move = HKLMove()
    result = move.calculate(data, [1.0, 1.0, 1.0])

    assert result.success is True
    assert {"mu", "eta", "chi", "phi", "nu", "del"}.issubset(result.angles)
    assert result.hkl_error < 1e-4


def test_hkl_move_persists_motor_angles_when_successful(temp_experiment_file):
    _, data = temp_experiment_file
    store = MagicMock()
    store.read.return_value = data

    move = HKLMove(file_store=store)
    result = move.move([1.0, 1.0, 1.0])

    assert result.success is True
    store.write.assert_called_once()
    written = store.write.call_args.args[0]
    assert isinstance(written["motors"]["mu"]["value"], float)


def test_failed_hkl_move_leaves_persisted_motor_values_unchanged(temp_experiment_file):
    filepath, data = temp_experiment_file
    original_motor_values = {
        motor: config["value"] for motor, config in data["motors"].items()
    }
    store = ExperimentFileStore(filepath)

    result = HKLMove(file_store=store, max_error=-1.0).move([1.0, 1.0, 1.0])

    assert result.success is False
    persisted = store.read()
    assert {
        motor: config["value"] for motor, config in persisted["motors"].items()
    } == original_motor_values
