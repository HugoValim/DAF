"""
Unit tests for daf.command_line.experiment.bounds module
"""
import unittest
from unittest.mock import patch, MagicMock
import sys


class TestBounds(unittest.TestCase):
    def test_bounds_desc_defined(self):
        """Test that Bounds has DESC attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.bounds import Bounds

            self.assertTrue(hasattr(Bounds, "DESC"))
            self.assertIsInstance(Bounds.DESC, str)

    def test_bounds_default_bounds(self):
        """Test that Bounds has correct DEFAULT_BOUNDS"""
        from daf.command_line.experiment.bounds import Bounds

        self.assertIn("mu", Bounds.DEFAULT_BOUNDS)
        self.assertIn("eta", Bounds.DEFAULT_BOUNDS)
        self.assertIn("chi", Bounds.DEFAULT_BOUNDS)
        self.assertIn("phi", Bounds.DEFAULT_BOUNDS)
        self.assertIn("nu", Bounds.DEFAULT_BOUNDS)
        self.assertIn("del", Bounds.DEFAULT_BOUNDS)

    def test_bounds_default_mu_bounds(self):
        """Test Mu default bounds"""
        from daf.command_line.experiment.bounds import Bounds

        self.assertEqual(Bounds.DEFAULT_BOUNDS["mu"], [-20.0, 160.0])

    def test_bounds_default_eta_bounds(self):
        """Test Eta default bounds"""
        from daf.command_line.experiment.bounds import Bounds

        self.assertEqual(Bounds.DEFAULT_BOUNDS["eta"], [-20.0, 160.0])

    def test_bounds_default_chi_bounds(self):
        """Test Chi default bounds"""
        from daf.command_line.experiment.bounds import Bounds

        self.assertEqual(Bounds.DEFAULT_BOUNDS["chi"], [-5.0, 95.0])

    def test_bounds_default_phi_bounds(self):
        """Test Phi default bounds"""
        from daf.command_line.experiment.bounds import Bounds

        self.assertEqual(Bounds.DEFAULT_BOUNDS["phi"], [-400.0, 400.0])

    def test_bounds_default_nu_bounds(self):
        """Test Nu default bounds"""
        from daf.command_line.experiment.bounds import Bounds

        self.assertEqual(Bounds.DEFAULT_BOUNDS["nu"], [-20.0, 160.0])

    def test_bounds_default_del_bounds(self):
        """Test Del default bounds"""
        from daf.command_line.experiment.bounds import Bounds

        self.assertEqual(Bounds.DEFAULT_BOUNDS["del"], [-20.0, 160.0])

    def test_reset_bounds_to_default(self):
        """Test reset_bounds_to_default method"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.bounds import Bounds

            bounds = Bounds.__new__(Bounds)
            bounds.experiment_file_dict = {
                "motors": {
                    "mu": {"bounds": [0, 0]},
                    "eta": {"bounds": [0, 0]},
                    "chi": {"bounds": [0, 0]},
                    "phi": {"bounds": [0, 0]},
                    "nu": {"bounds": [0, 0]},
                    "del": {"bounds": [0, 0]},
                }
            }
            bounds.write_to_experiment_file = MagicMock()

            bounds.reset_bounds_to_default()

            # Check that write_to_experiment_file was called with DEFAULT_BOUNDS
            bounds.write_to_experiment_file.assert_called_once()
            call_args = bounds.write_to_experiment_file.call_args
            self.assertEqual(call_args[1]["is_motor_bounds"], True)


class TestBoundsListBounds(unittest.TestCase):
    def test_list_bounds_outputs_content(self):
        """Test that list_bounds prints bounds"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.experiment.bounds import Bounds

            bounds = Bounds.__new__(Bounds)
            bounds.experiment_file_dict = {
                "motors": {
                    "mu": {"bounds": [-20.0, 160.0]},
                    "eta": {"bounds": [-20.0, 160.0]},
                    "chi": {"bounds": [-5.0, 95.0]},
                    "phi": {"bounds": [-400.0, 400.0]},
                    "nu": {"bounds": [-20.0, 160.0]},
                    "del": {"bounds": [-180.0, 180.0]},
                }
            }

            # Capture stdout
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                bounds.list_bounds()

            output = f.getvalue()
            self.assertIn("Mu", output)
            self.assertIn("Eta", output)
            self.assertIn("Chi", output)
            self.assertIn("Phi", output)
            self.assertIn("Nu", output)
            self.assertIn("Del", output)


if __name__ == "__main__":
    unittest.main()
