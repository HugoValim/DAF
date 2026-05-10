import numpy as np

from daf.utils.experiment_config import ExperimentConfig


def test_experiment_config_exposes_named_domain_values(temp_experiment_file):
    _, data = temp_experiment_file

    config = ExperimentConfig.from_dict(data)

    assert config.mode == (2, 0, 5, 2)
    assert config.energy == 8000.0
    assert config.motor_values == {
        "mu": 0.0,
        "eta": 0.0,
        "chi": 0.0,
        "phi": 0.0,
        "nu": 0.0,
        "del": 0.0,
    }
    assert config.motor_bounds["chi"] == [-5, 95]
    assert config.constraints["cons_qaz"] == 0.0
    np.testing.assert_array_equal(config.u_matrix, np.identity(3))


def test_experiment_config_updates_motor_setpoints(temp_experiment_file):
    _, data = temp_experiment_file
    config = ExperimentConfig.from_dict(data)

    updated = config.with_motor_setpoints({"mu": 1.5, "eta": 2.5})

    assert updated["motors"]["mu"]["value"] == 1.5
    assert updated["motors"]["eta"]["value"] == 2.5
    assert updated["motors"]["chi"]["value"] == 0.0
