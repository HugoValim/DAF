"""
Unit tests for daf.command_line.query.where (Where / daf.wh) using run_main().

These tests call run_cmd() directly — no sys.argv patching required.
"""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch


class TestRunMain(unittest.TestCase):
    """Tests for CLIBase.run_main() classmethod."""

    def test_run_main_is_classmethod_on_cli_base(self):
        """CLIBase must expose run_main as a classmethod."""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.cli_base_utils import CLIBase

            self.assertTrue(hasattr(CLIBase, "run_main"))
            self.assertIsInstance(CLIBase.__dict__["run_main"], classmethod)

    def test_run_main_calls_lifecycle_in_order(self):
        """run_main() must call parse_command_line, build_exp, run_cmd in order."""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.cli_base_utils import CLIBase

            calls = []

            class ConcreteCmd(CLIBase):
                DESC = "test"
                EPI = "test"

                def parse_command_line(self):
                    calls.append("parse_command_line")
                    # Return a namespace with no args so vars() works
                    import argparse

                    self.parsed_args = argparse.Namespace()
                    self.parsed_args_dict = {}
                    return self.parsed_args

                def build_exp(self):
                    calls.append("build_exp")
                    return MagicMock()

                def run_cmd(self):
                    calls.append("run_cmd")

            ConcreteCmd.run_main()

            self.assertEqual(calls, ["parse_command_line", "build_exp", "run_cmd"])


class TestWhereMigratedToRunMain(unittest.TestCase):
    """Tests for Where.run_cmd() called directly without sys.argv patching."""

    def _make_where_instance(self):
        """Build a Where instance with all dependencies mocked."""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.where import Where

        where = Where.__new__(Where)
        # Minimal experiment_file_dict to satisfy motor lookups
        where.experiment_file_dict = {
            "motors": {
                "mu": {"value": 0.0, "bounds": [-180, 180]},
                "eta": {"value": 15.0, "bounds": [-180, 180]},
                "chi": {"value": 35.0, "bounds": [-5, 95]},
                "phi": {"value": 45.0, "bounds": [30, 400]},
                "nu": {"value": 0.0, "bounds": [-180, 180]},
                "del": {"value": 31.0, "bounds": [-180, 180]},
            },
            "alpha": 0.0,
            "beta": 0.0,
            "psi": 0.0,
            "tau": 0.0,
            "qaz": 90.0,
            "naz": 0.0,
            "omega": 0.0,
        }
        where.parsed_args_dict = {}
        # Stub out the expensive calculation helpers
        where.calculate_hkl_from_angles = MagicMock(return_value=[1.0, 1.0, 1.0])
        where.get_pseudo_angles_from_motor_angles = MagicMock(
            return_value={
                "alpha": 0.0,
                "beta": 0.0,
                "psi": 0.0,
                "tau": 0.0,
                "qaz": 90.0,
                "naz": 0.0,
                "omega": 0.0,
            }
        )
        where.update_experiment_file = MagicMock()
        where.write_to_experiment_file = MagicMock()
        return where

    def test_run_cmd_calls_print_and_update(self):
        """run_cmd() must call print_position and update_pseudo_angles_and_hkl."""
        where = self._make_where_instance()
        where.print_position = MagicMock()
        where.update_pseudo_angles_and_hkl = MagicMock()

        where.run_cmd()

        where.print_position.assert_called_once()
        where.update_pseudo_angles_and_hkl.assert_called_once()

    def test_print_position_outputs_hkl(self):
        """print_position() must print an HKL line."""
        where = self._make_where_instance()

        f = io.StringIO()
        with redirect_stdout(f):
            where.print_position()

        output = f.getvalue()
        self.assertIn("HKL", output)

    def test_update_pseudo_angles_sets_hklnow(self):
        """update_pseudo_angles_and_hkl must add hklnow as floats."""
        where = self._make_where_instance()
        where.hkl_now = [1.0, 1.0, 1.0]
        where.pseudo_dict_to_update = {"alpha": 0.0}

        where.update_pseudo_angles_and_hkl()

        self.assertEqual(where.pseudo_dict_to_update["hklnow"], [1.0, 1.0, 1.0])

    def test_where_no_longer_has_init_boilerplate(self):
        """After migration Where.__init__ must not call parse_command_line itself."""
        # We verify by checking the source does NOT replicate the boilerplate
        import inspect

        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.where import Where

        src = inspect.getsource(Where.__init__)
        # After migration __init__ should just call super().__init__()
        # and NOT call self.parse_command_line() / self.build_exp()
        self.assertNotIn("self.parse_command_line()", src)
        self.assertNotIn("self.build_exp()", src)


if __name__ == "__main__":
    unittest.main()
