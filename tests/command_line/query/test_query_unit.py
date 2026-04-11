"""
Unit tests for daf.command_line.query modules
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import io
from contextlib import redirect_stdout


class TestQueryBase(unittest.TestCase):
    def test_query_base_inherits_from_cli_base(self):
        """Test that QueryBase inherits from CLIBase"""
        from daf.command_line.query.query_utils import QueryBase
        from daf.command_line.cli_base_utils import CLIBase

        self.assertTrue(issubclass(QueryBase, CLIBase))


class TestWhere(unittest.TestCase):
    def test_where_desc_defined(self):
        """Test that Where has DESC attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.where import Where

            self.assertTrue(hasattr(Where, "DESC"))
            self.assertIsInstance(Where.DESC, str)

    def test_where_epi_defined(self):
        """Test that Where has EPI attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.where import Where

            self.assertTrue(hasattr(Where, "EPI"))

    def test_update_pseudo_angles_and_hkl(self):
        """Test update_pseudo_angles_and_hkl method"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.where import Where

            where = Where.__new__(Where)
            where.hkl_now = [1.0, 2.0, 3.0]
            where.pseudo_dict_to_update = {"alpha": 10.0}
            where.experiment_file_dict = {"motors": {}}
            where.update_experiment_file = MagicMock()
            where.write_to_experiment_file = MagicMock()

            where.update_pseudo_angles_and_hkl()

            # Check that float conversion happened
            self.assertEqual(where.pseudo_dict_to_update["hklnow"], [1.0, 2.0, 3.0])


class TestStatus(unittest.TestCase):
    def test_status_desc_defined(self):
        """Test that Status has DESC attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            self.assertTrue(hasattr(Status, "DESC"))
            self.assertIsInstance(Status.DESC, str)

    def test_status_epi_defined(self):
        """Test that Status has EPI attribute"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            self.assertTrue(hasattr(Status, "EPI"))

    def test_show_bounds_outputs_content(self):
        """Test that show_bounds prints bounds"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            status = Status.__new__(Status)
            status.experiment_file_dict = {
                "motors": {
                    "mu": {"bounds": [-20.0, 160.0]},
                    "eta": {"bounds": [-20.0, 160.0]},
                    "chi": {"bounds": [-5.0, 95.0]},
                    "phi": {"bounds": [-400.0, 400.0]},
                    "nu": {"bounds": [-20.0, 160.0]},
                    "del": {"bounds": [-180.0, 180.0]},
                }
            }

            f = io.StringIO()
            with redirect_stdout(f):
                status.show_bounds()

            output = f.getvalue()
            self.assertIn("Mu", output)
            self.assertIn("Eta", output)
            self.assertIn("Chi", output)
            self.assertIn("Phi", output)
            self.assertIn("Nu", output)
            self.assertIn("Del", output)

    def test_show_u_and_ub_creates_tables(self):
        """Test that show_u_and_ub creates table output"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            status = Status.__new__(Status)
            status.experiment_file_dict = {
                "U_mat": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                "UB_mat": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            }

            f = io.StringIO()
            with redirect_stdout(f):
                result = status.show_u_and_ub()

            output = f.getvalue()
            self.assertIn("U", output)
            self.assertIn("UB", output)

    def test_show_mode_method_exists(self):
        """Test that show_mode method exists"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            status = Status.__new__(Status)
            self.assertTrue(hasattr(status, "show_mode"))

    def test_show_expt_method_exists(self):
        """Test that show_expt method exists"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            status = Status.__new__(Status)
            self.assertTrue(hasattr(status, "show_expt"))

    def test_show_sample_method_exists(self):
        """Test that show_sample method exists"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            status = Status.__new__(Status)
            self.assertTrue(hasattr(status, "show_sample"))

    def test_show_all_method_exists(self):
        """Test that show_all method exists"""
        with patch("daf.command_line.cli_base_utils.du.DAFIO"):
            from daf.command_line.query.status import Status

            status = Status.__new__(Status)
            self.assertTrue(hasattr(status, "show_all"))


if __name__ == "__main__":
    unittest.main()
