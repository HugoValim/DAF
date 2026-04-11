"""
Unit tests for daf.command_line.move modules
"""
import unittest
from unittest.mock import patch, MagicMock
import sys


class TestMoveBase(unittest.TestCase):

    def test_move_base_inherits_from_cli_base(self):
        """Test that MoveBase inherits from CLIBase"""
        from daf.command_line.move.move_utils import MoveBase
        from daf.command_line.cli_base_utils import CLIBase

        self.assertTrue(issubclass(MoveBase, CLIBase))

    def test_motor_inputs_method_exists(self):
        """Test that motor_inputs method exists"""
        from daf.command_line.move.move_utils import MoveBase

        self.assertTrue(hasattr(MoveBase, 'motor_inputs'))
        self.assertTrue(callable(getattr(MoveBase, 'motor_inputs')))


class TestAngleMove(unittest.TestCase):

    def test_angle_move_desc_defined(self):
        """Test that AngleMove has DESC attribute"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.ang_move import AngleMove

            self.assertTrue(hasattr(AngleMove, 'DESC'))
            self.assertIsInstance(AngleMove.DESC, str)

    def test_angle_move_epi_defined(self):
        """Test that AngleMove has EPI attribute"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.ang_move import AngleMove

            self.assertTrue(hasattr(AngleMove, 'EPI'))

    def test_write_angles_with_stat_dict(self):
        """Test write_angles with scan_stats dictionary"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.ang_move import AngleMove

            ang = AngleMove.__new__(AngleMove)
            ang.experiment_file_dict = {
                "scan_stats": {
                    "fwhm": {"counter1": 1.0},
                    "com": {"counter1": 50.0},
                    "max": {"counter1": [100.0, 0]},
                    "min": {"counter1": [0.0, 0]},
                },
                "main_scan_counter": None
            }
            ang.parsed_args_dict = {
                "del": "CEN",
                "counter": None
            }

            result = ang.write_angles(ang.parsed_args_dict)

            self.assertEqual(result["del"], 50.0)

    def test_write_angles_with_counter(self):
        """Test write_angles with specific counter"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.ang_move import AngleMove

            ang = AngleMove.__new__(AngleMove)
            ang.experiment_file_dict = {
                "scan_stats": {
                    "fwhm": {"roi1": 2.0, "roi2": 3.0},
                    "com": {"roi1": 25.0, "roi2": 75.0},
                    "max": {"roi1": [50.0, 0], "roi2": [100.0, 0]},
                    "min": {"roi1": [0.0, 0], "roi2": [50.0, 0]},
                },
                "main_scan_counter": None
            }
            ang.parsed_args_dict = {
                "del": "MAX",
                "counter": "roi1"
            }

            result = ang.write_angles(ang.parsed_args_dict)

            self.assertEqual(result["del"], 50.0)

    def test_write_angles_empty_stats(self):
        """Test write_angles with empty scan_stats"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.ang_move import AngleMove

            ang = AngleMove.__new__(AngleMove)
            ang.experiment_file_dict = {
                "scan_stats": {},
                "main_scan_counter": None
            }
            ang.parsed_args_dict = {
                "del": 30.0,
                "counter": None
            }

            result = ang.write_angles(ang.parsed_args_dict)

            # Should pass through original values
            self.assertEqual(result["del"], 30.0)

    def test_write_angles_main_scan_counter(self):
        """Test write_angles uses main_scan_counter when set"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.ang_move import AngleMove

            ang = AngleMove.__new__(AngleMove)
            ang.experiment_file_dict = {
                "scan_stats": {
                    "fwhm": {"main_counter": 5.0},
                    "com": {"main_counter": 200.0},
                    "max": {"main_counter": [500.0, 0]},
                    "min": {"main_counter": [100.0, 0]},
                },
                "main_scan_counter": "main_counter"
            }
            ang.parsed_args_dict = {
                "del": "CEN",
                "counter": None
            }

            result = ang.write_angles(ang.parsed_args_dict)

            self.assertEqual(result["del"], 200.0)


class TestHklMove(unittest.TestCase):

    def test_hkl_move_imports(self):
        """Test that HklMove can be imported"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.hkl_move import HklMove

            self.assertTrue(hasattr(HklMove, 'DESC'))

    def test_hkl_move_desc_defined(self):
        """Test that HklMove has DESC"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.hkl_move import HklMove

            self.assertTrue(hasattr(HklMove, 'DESC'))


class TestHklCalc(unittest.TestCase):

    def test_hkl_calc_imports(self):
        """Test that HklCalc can be imported"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.hkl_calc import HklCalc

            self.assertTrue(hasattr(HklCalc, 'DESC'))

    def test_hkl_calc_desc_defined(self):
        """Test that HklCalc has DESC"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.hkl_calc import HklCalc

            self.assertTrue(hasattr(HklCalc, 'DESC'))


class TestRelAngleMove(unittest.TestCase):

    def test_rel_angle_move_imports(self):
        """Test that RelAngleMove can be imported"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.rel_ang_move import RelAngleMove

            self.assertTrue(hasattr(RelAngleMove, 'DESC'))

    def test_rel_angle_move_desc_defined(self):
        """Test that RelAngleMove has DESC"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.move.rel_ang_move import RelAngleMove

            self.assertTrue(hasattr(RelAngleMove, 'DESC'))


if __name__ == '__main__':
    unittest.main()
