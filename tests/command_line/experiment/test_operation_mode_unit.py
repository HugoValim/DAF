"""
Unit tests for daf.command_line.experiment.operation_mode module
"""
import unittest
from unittest.mock import patch, MagicMock
import sys


class TestOperationMode(unittest.TestCase):

    def test_operation_mode_desc_defined(self):
        """Test that OperationMode has DESC attribute"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.experiment.operation_mode import OperationMode

            self.assertTrue(hasattr(OperationMode, 'DESC'))
            self.assertIsInstance(OperationMode.DESC, str)

    def test_operation_mode_epi_defined(self):
        """Test that OperationMode has EPI attribute"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            from daf.command_line.experiment.operation_mode import OperationMode

            self.assertTrue(hasattr(OperationMode, 'EPI'))
            self.assertIsInstance(OperationMode.EPI, str)

    def test_operation_mode_desc_contains_mode_table(self):
        """Test that DESC contains mode table information"""
        from daf.command_line.experiment.operation_mode import OperationMode

        desc = OperationMode.DESC
        self.assertIn("detector", desc)
        self.assertIn("Reference", desc)
        self.assertIn("Nu-fixed", desc)

    def test_operation_mode_run_cmd_updates_experiment_file(self):
        """Test that run_cmd updates experiment file with mode"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            with patch.object(sys, 'argv', ['daf.mode', '215']):
                from daf.command_line.experiment.operation_mode import OperationMode

                mode = OperationMode.__new__(OperationMode)
                mode.experiment_file_dict = {}
                mode.parsed_args_dict = {'Mode': '215'}
                mode.update_experiment_file = MagicMock()
                mode.write_to_experiment_file = MagicMock()

                mode.run_cmd()

                mode.update_experiment_file.assert_called()
                mode.write_to_experiment_file.assert_called()


class TestOperationModeIntegration(unittest.TestCase):

    def test_mode_parsing(self):
        """Test that mode string is parsed correctly"""
        with patch('daf.command_line.cli_base_utils.DAFIO'):
            with patch.object(sys, 'argv', ['daf.mode', '215']):
                from daf.command_line.experiment.operation_mode import OperationMode

                mode_obj = OperationMode()
                self.assertEqual(mode_obj.parsed_args_dict['Mode'], '215')


if __name__ == '__main__':
    unittest.main()
