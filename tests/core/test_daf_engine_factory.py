"""
Unit tests for daf.core.daf_engine_factory
"""
import numpy as np
import pytest

from daf.core.main import DAF
from daf.core.daf_engine_factory import DAFEngineFactory


@pytest.fixture
def minimal_experiment_dict():
    """Minimal experiment dict required to build a DAF instance."""
    return {
        "Mode": "2052",
        "Material": "Si",
        "IDir_print": [0, 1, 0],
        "NDir_print": [0, 0, 1],
        "RDir": [0, 0, 1],
        "Sampleor": "z+",
        "energy_offset": 0.0,
        "U_mat": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        "lparam_a": 5.43,
        "lparam_b": 5.43,
        "lparam_c": 5.43,
        "lparam_alpha": 90.0,
        "lparam_beta": 90.0,
        "lparam_gama": 90.0,
        "user_samples": {},
        "beamline_pvs": {
            "energy": {"value": 8000},
        },
        "motors": {
            "mu": {"bounds": [-180, 180]},
            "eta": {"bounds": [-180, 180]},
            "chi": {"bounds": [-5, 95]},
            "phi": {"bounds": [30, 400]},
            "nu": {"bounds": [-180, 180]},
            "del": {"bounds": [-180, 180]},
        },
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
    }


class TestDAFEngineFactory:
    """Tests for DAFEngineFactory."""

    def test_factory_produces_daf_instance(self, minimal_experiment_dict):
        """Factory should return a fully configured DAF instance."""
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        assert isinstance(daf, DAF)

    def test_predefined_material(self, minimal_experiment_dict):
        """Factory should select predefined material when Material is in PREDEFINED_MATERIALS."""
        minimal_experiment_dict["Material"] = "Si"
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        assert daf.sample.name == "Si"

    def test_custom_material_from_user_samples(self, minimal_experiment_dict):
        """Factory should select custom material from user_samples dict."""
        minimal_experiment_dict["Material"] = "MyCustomSample"
        minimal_experiment_dict["user_samples"]["MyCustomSample"] = [
            3.189,
            3.189,
            5.185,
            90.0,
            90.0,
            120.0,
        ]
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        assert daf.sample.name == "MyCustomSample"
        assert daf.sample.a == pytest.approx(3.189)
        assert daf.sample.c == pytest.approx(5.185)

    def test_custom_material_from_lattice_params(self, minimal_experiment_dict):
        """Factory should build custom material from lattice params when not predefined or in user_samples."""
        minimal_experiment_dict["Material"] = "CustomCrystal"
        minimal_experiment_dict["lparam_a"] = 4.0
        minimal_experiment_dict["lparam_b"] = 5.0
        minimal_experiment_dict["lparam_c"] = 6.0
        minimal_experiment_dict["lparam_alpha"] = 90.0
        minimal_experiment_dict["lparam_beta"] = 90.0
        minimal_experiment_dict["lparam_gama"] = 90.0
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        assert daf.sample.name == "CustomCrystal"
        assert daf.sample.a == pytest.approx(4.0)
        assert daf.sample.b == pytest.approx(5.0)
        assert daf.sample.c == pytest.approx(6.0)

    def test_constraints_and_bounds_applied(self, minimal_experiment_dict):
        """Factory should apply mode-derived motor bounds correctly.

        Note: set_circle_constrain receives lowercase keys from the experiment
        dict but DAF.MOTOR_BOUNDS_MAP uses title-case keys, so the call is a
        no-op — matching the original CLIBase.build_exp() behaviour. Bounds
        are therefore determined by ModeParser defaults.
        """
        minimal_experiment_dict["Mode"] = "215"  # Nu fixed -> Nu_bound == 0
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        assert daf.Nu_bound == 0
        assert daf.Eta_bound == pytest.approx((-180, 180))

    def test_mode_parsed_correctly(self, minimal_experiment_dict):
        """Factory should parse the mode string and set up DAF mode correctly."""
        minimal_experiment_dict["Mode"] = "215"
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        assert daf.mode.constraint_columns() == (2, 1, 5, 0, 0)

    def test_energy_applied_correctly(self, minimal_experiment_dict):
        """Factory should compute energy with offset and set conditions."""
        minimal_experiment_dict["beamline_pvs"]["energy"]["value"] = 10000.0
        minimal_experiment_dict["energy_offset"] = 200.0
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        assert daf.en == pytest.approx(9800.0)

    def test_u_matrix_set(self, minimal_experiment_dict):
        """Factory should set the U matrix from the experiment dict."""
        u = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
        minimal_experiment_dict["U_mat"] = u.tolist()
        daf = DAFEngineFactory.from_dict(minimal_experiment_dict)

        np.testing.assert_array_almost_equal(daf.U, u)


class TestCLIBaseIntegration:
    """Integration tests verifying CLIBase.build_exp delegates to factory."""

    def test_clibase_build_exp_returns_daf_instance(self, minimal_experiment_dict):
        """CLIBase.build_exp should still return a DAF instance after refactoring."""
        from daf.command_line.cli_base_utils import CLIBase

        class DummyCLI(CLIBase):
            DESC = "dummy"
            EPI = ""

            def run_cmd(self):
                pass

        cli = DummyCLI(read=False)
        cli.experiment_file_dict = minimal_experiment_dict
        daf = cli.build_exp()

        assert isinstance(daf, DAF)
        assert daf.sample.name == "Si"
