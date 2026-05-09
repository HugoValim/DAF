from unittest.mock import MagicMock

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
