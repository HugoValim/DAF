"""
Unit tests for daf.command_line.support.support_utils module
"""
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os


class TestSupportBase(unittest.TestCase):
    def test_write_yaml_creates_file(self):
        """Test that write_yaml creates a YAML file"""
        from daf.command_line.support.support_utils import SupportBase

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.yml")
            test_dict = {"key": "value", "number": 42}

            SupportBase.write_yaml(test_dict, filepath)

            self.assertTrue(os.path.exists(filepath))

            # Verify content
            import yaml

            with open(filepath) as f:
                loaded = yaml.safe_load(f)

            self.assertEqual(loaded["key"], "value")
            self.assertEqual(loaded["number"], 42)

    def test_write_yaml_with_nested_data(self):
        """Test write_yaml handles nested dictionaries"""
        from daf.command_line.support.support_utils import SupportBase

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.yml")
            test_dict = {
                "motors": {
                    "mu": {"pv": "test:mu", "value": 0},
                    "eta": {"pv": "test:eta", "value": 0},
                }
            }

            SupportBase.write_yaml(test_dict, filepath)

            import yaml

            with open(filepath) as f:
                loaded = yaml.safe_load(f)

            self.assertEqual(loaded["motors"]["mu"]["pv"], "test:mu")

    def test_get_motors_beamline_pvs_counters_info_simulated(self):
        """Test get_motors_beamline_pvs_counters_info with simulated=True"""
        from daf.command_line.support.support_utils import SupportBase

        (
            motors,
            beamline_pvs,
            counters,
        ) = SupportBase.get_motors_beamline_pvs_counters_info(simulated=True)

        self.assertIsInstance(motors, dict)
        self.assertIsInstance(beamline_pvs, dict)
        self.assertIsInstance(counters, dict)

    def test_get_motors_beamline_pvs_counters_info_real(self):
        """Test get_motors_beamline_pvs_counters_info with simulated=False"""
        from daf.command_line.support.support_utils import SupportBase

        (
            motors,
            beamline_pvs,
            counters,
        ) = SupportBase.get_motors_beamline_pvs_counters_info(simulated=False)

        self.assertIsInstance(motors, dict)
        self.assertIsInstance(beamline_pvs, dict)
        self.assertIsInstance(counters, dict)

    def test_build_current_file_returns_dict(self):
        """Test build_current_file returns a dictionary"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            from daf.command_line.support.support_utils import SupportBase

            support = SupportBase.__new__(SupportBase)
            result = support.build_current_file(simulated=True)

            self.assertIsInstance(result, dict)

    def test_build_current_file_sets_simulated_flag(self):
        """Test build_current_file sets simulated flag"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            from daf.command_line.support.support_utils import SupportBase

            support = SupportBase.__new__(SupportBase)

            # Test simulated=True
            result_true = support.build_current_file(simulated=True)
            self.assertTrue(result_true["simulated"])

            # Test simulated=False
            result_false = support.build_current_file(simulated=False)
            self.assertFalse(result_false["simulated"])

    def test_build_current_file_contains_motors(self):
        """Test build_current_file includes motors data"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            from daf.command_line.support.support_utils import SupportBase

            support = SupportBase.__new__(SupportBase)
            result = support.build_current_file(simulated=True)

            self.assertIn("motors", result)
            self.assertIsInstance(result["motors"], dict)

    def test_build_current_file_contains_beamline_pvs(self):
        """Test build_current_file includes beamline_pvs data"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            from daf.command_line.support.support_utils import SupportBase

            support = SupportBase.__new__(SupportBase)
            result = support.build_current_file(simulated=True)

            self.assertIn("beamline_pvs", result)
            self.assertIsInstance(result["beamline_pvs"], dict)

    def test_build_current_file_contains_counters(self):
        """Test build_current_file includes counters config"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            from daf.command_line.support.support_utils import SupportBase

            support = SupportBase.__new__(SupportBase)
            result = support.build_current_file(simulated=True)

            self.assertIn("counters", result)

    def test_build_current_file_with_kafka_topic(self):
        """Test build_current_file accepts kafka_topic parameter"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            from daf.command_line.support.support_utils import SupportBase

            support = SupportBase.__new__(SupportBase)
            result = support.build_current_file(
                simulated=True, kafka_topic="test_topic"
            )

            self.assertEqual(result["kafka_topic"], "test_topic")

    def test_build_current_file_with_scan_db(self):
        """Test build_current_file accepts scan_db parameter"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            from daf.command_line.support.support_utils import SupportBase

            support = SupportBase.__new__(SupportBase)
            result = support.build_current_file(simulated=True, scan_db="test_db")

            self.assertEqual(result["scan_db"], "test_db")


class TestWriteToDisc(unittest.TestCase):
    def test_write_to_disc_local(self):
        """Test write_to_disc writes to local directory"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            with patch("daf.command_line.support.support_utils.du") as mock_du:
                mock_du.fetch_pvs_and_check_for_connection.return_value = {}

                with tempfile.TemporaryDirectory() as tmpdir:
                    original_dir = os.getcwd()
                    os.chdir(tmpdir)

                    try:
                        from daf.command_line.support.support_utils import SupportBase

                        support = SupportBase.__new__(SupportBase)
                        support.io = MagicMock()

                        data = {"test": "data"}
                        support.write_to_disc(data, fetch_motors=False)

                        self.assertTrue(os.path.exists(".Experiment"))
                    finally:
                        os.chdir(original_dir)

    def test_write_to_disc_global(self):
        """Test write_to_disc writes to global config directory"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            with patch("daf.command_line.support.support_utils.du") as mock_du:
                mock_du.fetch_pvs_and_check_for_connection.return_value = {}

                with patch("daf.command_line.support.support_utils.dp") as mock_dp:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        mock_dp.DAF_CONFIGS = tmpdir
                        mock_dp.DEFAULT_FILE_NAME = ".Experiment"

                        from daf.command_line.support.support_utils import SupportBase

                        support = SupportBase.__new__(SupportBase)
                        support.io = MagicMock()

                        data = {"test": "data"}
                        support.write_to_disc(data, fetch_motors=False, is_global=True)

                        expected_path = os.path.join(tmpdir, ".Experiment")
                        self.assertTrue(os.path.exists(expected_path))


if __name__ == "__main__":
    unittest.main()
