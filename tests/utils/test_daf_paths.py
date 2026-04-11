"""
Unit tests for daf.utils.daf_paths module
"""
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestDAFPaths(unittest.TestCase):

    def test_default_file_name(self):
        """Test that default file name is .Experiment"""
        from daf.utils.daf_paths import DAFPaths

        self.assertEqual(DAFPaths.DEFAULT_FILE_NAME, ".Experiment")

    def test_home_from_environment(self):
        """Test that HOME is read from environment"""
        from daf.utils.daf_paths import DAFPaths

        home = os.getenv("HOME")
        self.assertEqual(DAFPaths.HOME, home)

    def test_daf_configs_path(self):
        """Test that DAF_CONFIGS path is correctly formed"""
        from daf.utils.daf_paths import DAFPaths

        expected = os.path.join(os.getenv("HOME"), ".daf")
        self.assertEqual(DAFPaths.DAF_CONFIGS, expected)

    def test_scan_configs_path(self):
        """Test that SCAN_CONFIGS path is correctly formed"""
        from daf.utils.daf_paths import DAFPaths

        expected = os.path.join(os.getenv("HOME"), ".daf", "scan")
        self.assertEqual(DAFPaths.SCAN_CONFIGS, expected)

    def test_global_experiment_default_path(self):
        """Test that GLOBAL_EXPERIMENT_DEFAULT is correctly formed"""
        from daf.utils.daf_paths import DAFPaths

        expected = os.path.join(os.getenv("HOME"), ".daf", ".Experiment")
        self.assertEqual(DAFPaths.GLOBAL_EXPERIMENT_DEFAULT, expected)

    def test_local_experiment_default_path(self):
        """Test that LOCAL_EXPERIMENT_DEFAULT is in current directory"""
        from daf.utils.daf_paths import DAFPaths

        expected = os.path.join(".", ".Experiment")
        self.assertEqual(DAFPaths.LOCAL_EXPERIMENT_DEFAULT, expected)

    def test_check_for_local_config_local_exists(self):
        """Test check_for_local_config returns local path when it exists"""
        from daf.utils.daf_paths import DAFPaths

        with tempfile.TemporaryDirectory() as tmpdir:
            local_file = Path(tmpdir) / ".Experiment"
            local_file.touch()

            with patch.object(DAFPaths, 'LOCAL_EXPERIMENT_DEFAULT', str(local_file)):
                result = DAFPaths.check_for_local_config()
                self.assertEqual(result, local_file)

    def test_check_for_local_config_local_not_exists(self):
        """Test check_for_local_config returns global path when local doesn't exist"""
        from daf.utils.daf_paths import DAFPaths

        with tempfile.TemporaryDirectory() as tmpdir:
            global_file = Path(tmpdir) / ".Experiment"
            global_file.touch()

            with patch.object(DAFPaths, 'GLOBAL_EXPERIMENT_DEFAULT', str(global_file)):
                with patch.object(DAFPaths, 'LOCAL_EXPERIMENT_DEFAULT', '/nonexistent/path/.Experiment'):
                    result = DAFPaths.check_for_local_config()
                    self.assertEqual(result, global_file)


if __name__ == '__main__':
    unittest.main()
