"""
Unit tests for daf.command_line.experiment modules
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import numpy as np


class TestExperimentConfiguration(unittest.TestCase):
    def test_experiment_configuration_desc_defined(self):
        """Test that ExperimentConfiguration has DESC attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            self.assertTrue(hasattr(ExperimentConfiguration, "DESC"))
            self.assertIsInstance(ExperimentConfiguration.DESC, str)

    def test_experiment_configuration_epi_defined(self):
        """Test that ExperimentConfiguration has EPI attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            self.assertTrue(hasattr(ExperimentConfiguration, "EPI"))

    def test_set_lattice_parameters(self):
        """Test setting lattice parameters"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            exp = ExperimentConfiguration.__new__(ExperimentConfiguration)
            exp.experiment_file_dict = {}

            lattice_params = [1.0, 2.0, 3.0, 90.0, 90.0, 90.0]
            exp.set_lattice_parameters(lattice_params)

            self.assertEqual(exp.experiment_file_dict["lparam_a"], 1.0)
            self.assertEqual(exp.experiment_file_dict["lparam_b"], 2.0)
            self.assertEqual(exp.experiment_file_dict["lparam_c"], 3.0)
            self.assertEqual(exp.experiment_file_dict["lparam_alpha"], 90.0)
            self.assertEqual(exp.experiment_file_dict["lparam_beta"], 90.0)
            self.assertEqual(exp.experiment_file_dict["lparam_gama"], 90.0)

    def test_set_energy(self):
        """Test setting energy"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            exp = ExperimentConfiguration.__new__(ExperimentConfiguration)
            exp.experiment_file_dict = {"beamline_pvs": {"energy": {"value": 10000}}}

            offset = exp.set_energy(8000)

            self.assertEqual(offset, 2000)  # 10000 - 8000
            self.assertEqual(exp.experiment_file_dict["energy_offset"], 2000)

    def test_set_energy_above_pv_value(self):
        """Test setting energy above PV value"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            exp = ExperimentConfiguration.__new__(ExperimentConfiguration)
            exp.experiment_file_dict = {"beamline_pvs": {"energy": {"value": 8000}}}

            offset = exp.set_energy(10000)

            self.assertEqual(offset, -2000)  # 8000 - 10000
            self.assertEqual(exp.experiment_file_dict["energy_offset"], -2000)

    def test_set_rdir(self):
        """Test setting reference direction"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            exp = ExperimentConfiguration.__new__(ExperimentConfiguration)
            exp.experiment_file_dict = {}

            rdir = np.array([1.0, 0.0, 0.0])
            exp.set_rdir(rdir)

            np.testing.assert_array_equal(
                exp.experiment_file_dict["RDir"], [1.0, 0.0, 0.0]
            )

    def test_set_sample_or(self):
        """Test setting sample orientation"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            exp = ExperimentConfiguration.__new__(ExperimentConfiguration)
            exp.experiment_file_dict = {}

            exp.set_sample_or("x+")

            self.assertEqual(exp.experiment_file_dict["Sampleor"], "x+")

    def test_set_simulated_motors(self):
        """Test setting simulated motors flag"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            exp = ExperimentConfiguration.__new__(ExperimentConfiguration)
            exp.experiment_file_dict = {"simulated": False}

            exp.set_simulated_motors()

            self.assertTrue(exp.experiment_file_dict["simulated"])

    def test_set_real_motors(self):
        """Test setting real motors flag"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.experiment_configuration import (
                ExperimentConfiguration,
            )

            exp = ExperimentConfiguration.__new__(ExperimentConfiguration)
            exp.experiment_file_dict = {"simulated": True}

            exp.set_real_motors()

            self.assertFalse(exp.experiment_file_dict["simulated"])


class TestExperimentBase(unittest.TestCase):
    def test_experiment_base_imports(self):
        """Test that ExperimentBase can be imported"""
        from daf.command_line.experiment.experiment_utils import ExperimentBase

        self.assertTrue(issubclass(ExperimentBase, object))

    def test_experiment_base_inherits_from_cli_base(self):
        """Test that ExperimentBase inherits from CLIBase"""
        from daf.command_line.experiment.experiment_utils import ExperimentBase
        from daf.command_line.cli_base_utils import CLIBase

        self.assertTrue(issubclass(ExperimentBase, CLIBase))


if __name__ == "__main__":
    unittest.main()
