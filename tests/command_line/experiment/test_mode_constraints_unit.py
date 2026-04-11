"""
Unit tests for daf.command_line.experiment.mode_constraints module
"""
import unittest
from unittest.mock import patch, MagicMock
import sys


class TestModeConstraints(unittest.TestCase):
    def test_mode_constraints_desc_defined(self):
        """Test that ModeConstraints has DESC attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.mode_constraints import ModeConstraints

            self.assertTrue(hasattr(ModeConstraints, "DESC"))
            self.assertIsInstance(ModeConstraints.DESC, str)

    def test_mode_constraints_epi_defined(self):
        """Test that ModeConstraints has EPI attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.mode_constraints import ModeConstraints

            self.assertTrue(hasattr(ModeConstraints, "EPI"))

    def test_mode_constraints_write_flag_initialized(self):
        """Test that write_flag is initialized to False"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            with patch.object(sys, "argv", ["daf.cons"]):
                from daf.command_line.experiment.mode_constraints import ModeConstraints

                mode = ModeConstraints()
                self.assertFalse(mode.write_flag)

    def test_reset_to_constraints_zero(self):
        """Test reset_to_constraints_zero method"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.mode_constraints import ModeConstraints

            mode = ModeConstraints.__new__(ModeConstraints)
            mode.experiment_file_dict = {
                "cons_mu": 10,
                "cons_eta": 20,
                "cons_chi": 30,
                "cons_phi": 40,
                "cons_nu": 50,
                "cons_del": 60,
                "cons_alpha": 70,
                "cons_beta": 80,
                "cons_psi": 90,
                "cons_omega": 100,
                "cons_qaz": 110,
                "cons_naz": 120,
            }

            mode.reset_to_constraints_zero()

            # All constraints should be reset to 0
            self.assertEqual(mode.experiment_file_dict["cons_mu"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_eta"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_chi"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_phi"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_nu"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_del"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_alpha"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_beta"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_psi"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_omega"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_qaz"], 0)
            self.assertEqual(mode.experiment_file_dict["cons_naz"], 0)


class TestListConstraints(unittest.TestCase):
    def test_list_constraints_outputs_content(self):
        """Test that list_constraints prints constraints"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.mode_constraints import ModeConstraints

            mode = ModeConstraints.__new__(ModeConstraints)
            mode.experiment_file_dict = {
                "cons_mu": 10,
                "cons_eta": 20,
                "cons_chi": 30,
                "cons_phi": 40,
                "cons_nu": 50,
                "cons_del": 60,
                "cons_alpha": 70,
                "cons_beta": 80,
                "cons_psi": 90,
                "cons_omega": 100,
                "cons_qaz": 110,
                "cons_naz": 120,
            }

            # Capture stdout
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                mode.list_contraints()

            output = f.getvalue()
            self.assertIn("Alpha", output)
            self.assertIn("Beta", output)
            self.assertIn("Psi", output)
            self.assertIn("Qaz", output)
            self.assertIn("Naz", output)
            self.assertIn("Omega", output)
            self.assertIn("Mu", output)
            self.assertIn("Eta", output)
            self.assertIn("Chi", output)
            self.assertIn("Phi", output)
            self.assertIn("Nu", output)
            self.assertIn("Del", output)


if __name__ == "__main__":
    unittest.main()
