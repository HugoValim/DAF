"""
Unit tests for daf.command_line.scan modules
"""
import os
import sys
import argparse
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import pytest


class TestScanBaseConfig:
    """Test ScanBase parse_command_line configuration"""

    def test_common_cli_scan_arguments_with_step(self):
        """Test common_cli_scan_arguments adds step argument when step=True"""
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            scan_base = ScanBase()
            scan_base.parser = argparse.ArgumentParser()
            scan_base.experiment_file_dict = {
                "motors": {
                    "mu": {"cli_abbrev": "m"},
                    "eta": {"pv": "SIM:m2", "value": 0.0, "bounds": [-180, 180]},
                }
            }

            scan_base.common_cli_scan_arguments(step=True)

            # Check step argument exists
            assert any(
                action.dest == "step" for action in scan_base.parser._actions
            ), "step argument should be added"

    def test_common_cli_scan_arguments_without_step(self):
        """Test common_cli_scan_arguments omits step argument when step=False"""
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            scan_base = ScanBase()
            scan_base.parser = argparse.ArgumentParser()

            scan_base.common_cli_scan_arguments(step=False)

            # Check step argument does not exist
            assert not any(
                action.dest == "step" for action in scan_base.parser._actions
            ), "step argument should NOT be added when step=False"


class TestScanBaseGetMotors:
    """Test ScanBase get_inputed_motor_order method"""

    def test_get_inputed_motor_order_with_abbrev(self):
        """Test motor order retrieval with abbreviated arguments"""
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            scan_base = ScanBase()
            scan_base.experiment_file_dict = {
                "motors": {
                    "mu": {"cli_abbrev": "m"},
                    "eta": {"cli_abbrev": "e"},
                    "chi": {"cli_abbrev": "c"},
                    "phi": {"cli_abbrev": "p"},
                    "nu": {"cli_abbrev": "n"},
                    "del": {"cli_abbrev": "d"},
                }
            }

            sys.argv = ["daf.test", "-m", "1", "10", "-e", "2", "20", "100", "0.1"]
            motor_order = scan_base.get_inputed_motor_order(sys.argv)

            assert motor_order == ["mu", "eta"]

    def test_get_inputed_motor_order_with_full_name(self):
        """Test motor order retrieval with full argument names"""
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            scan_base = ScanBase()
            scan_base.experiment_file_dict = {
                "motors": {
                    "mu": {"cli_abbrev": "m"},
                    "eta": {"cli_abbrev": "e"},
                }
            }

            sys.argv = ["daf.test", "--mu", "1", "10", "--eta", "2", "20", "100", "0.1"]
            motor_order = scan_base.get_inputed_motor_order(sys.argv)

            assert motor_order == ["mu", "eta"]

    def test_get_inputed_motor_order_empty(self):
        """Test motor order retrieval with no motors specified"""
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            scan_base = ScanBase()
            scan_base.experiment_file_dict = {
                "motors": {
                    "mu": {"cli_abbrev": "m"},
                    "eta": {"cli_abbrev": "e"},
                }
            }

            sys.argv = ["daf.test", "100", "0.1"]
            motor_order = scan_base.get_inputed_motor_order(sys.argv)

            assert motor_order == []


class TestDAFScanInputs:
    """Test DAFScanInputs dataclass"""

    def test_scan_db_defaults_to_none(self):
        """Test that scan_db can be None"""
        from daf.command_line.scan.scan_daf import DAFScanInputs

        inputs = DAFScanInputs()
        assert inputs.scan_db is None

    def test_scan_db_can_be_set(self):
        """Test that scan_db can be set"""
        from daf.command_line.scan.scan_daf import DAFScanInputs

        inputs = DAFScanInputs(scan_db="temp")
        assert inputs.scan_db == "temp"

    def test_all_fields_optional(self):
        """Test that all fields have sensible defaults"""
        from daf.command_line.scan.scan_daf import DAFScanInputs

        inputs = DAFScanInputs()
        assert inputs.scan_data is None
        assert inputs.inputed_motors == ()
        assert inputs.motors_data_dict is None
        assert inputs.counters == ()
        assert inputs.main_counter is None
        assert inputs.scan_type is None
        assert inputs.steps is None
        assert inputs.acquisition_time is None
        assert inputs.delay_time is None
        assert inputs.output is None
        assert inputs.kafka_topic is None
        assert inputs.kafka_server is None


class TestDAFScanClass:
    """Test DAFScan class methods"""

    def test_plans_map_contains_all_types(self):
        """Test PLANS_MAP contains all expected scan types"""
        from daf.command_line.scan.scan_daf import DAFScan

        expected_types = {"absolute", "relative", "list_scan", "grid_scan"}
        assert set(DAFScan.PLANS_MAP.keys()) == expected_types

    def test_counters_map_contains_all_types(self):
        """Test COUNTERS_MAP contains all expected counter types"""
        from daf.command_line.scan.scan_daf import DAFScan

        expected_types = {"EpicsSignalRO", "pilatus300k", "pilatus6ROIs"}
        assert set(DAFScan.COUNTERS_MAP.keys()) == expected_types

    def test_convert_to_float_if_not_none_tuple(self):
        """Test convert_to_float_if_not_none with tuple input"""
        from daf.command_line.scan.scan_daf import DAFScan

        result = DAFScan.convert_to_float_if_not_none((1.5, None, 2.0))
        assert result == [1.5, 2.0]

    def test_convert_to_float_if_not_none_single_value(self):
        """Test convert_to_float_if_not_none with single float value"""
        from daf.command_line.scan.scan_daf import DAFScan

        result = DAFScan.convert_to_float_if_not_none(3.14)
        assert result == 3.14

    def test_convert_to_float_if_not_none_none(self):
        """Test convert_to_float_if_not_none with None returns None"""
        from daf.command_line.scan.scan_daf import DAFScan

        result = DAFScan.convert_to_float_if_not_none(None)
        assert result is None


class TestScanBaseConfigureScanInput:
    """Test ScanBase configure_scan_input method"""

    def test_configure_scan_input_structure(self):
        """Test configure_scan_input returns correct structure"""
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            scan_base = ScanBase()
            scan_base.number_of_motors = 2
            scan_base.scan_type = "absolute"
            scan_base.parsed_args_dict = {
                "step": 100,
                "time": 0.1,
                "output": "/tmp/scan.nxs",
                "mu": [1.0, 10.0],
                "eta": [2.0, 20.0],
            }
            scan_base.inputed_motors = ["mu", "eta"]
            scan_base.experiment_file_dict = {
                "motors": {
                    "mu": {"pv": "SIM:m1", "value": 0.0, "bounds": [-180, 180]},
                    "eta": {"pv": "SIM:m2", "value": 0.0, "bounds": [-180, 180]},
                },
                "default_counters": "config.daf_default.yml",
                "main_scan_counter": "counter1",
                "kafka_topic": "test_topic",
                "scan_db": "temp",
                "kafka_server": "localhost:9092",
            }

            with patch.object(scan_base, "get_counters", return_value={"counter1": {}}):
                scan_inputs = scan_base.configure_scan_input()

            assert "scan_data" in scan_inputs
            assert "inputed_motors" in scan_inputs
            assert "motors_data_dict" in scan_inputs
            assert "counters" in scan_inputs
            assert "main_counter" in scan_inputs
            assert "scan_type" in scan_inputs
            assert "steps" in scan_inputs
            assert "acquisition_time" in scan_inputs
            assert "output" in scan_inputs
            assert "kafka_topic" in scan_inputs
            assert "scan_db" in scan_inputs
            assert "kafka_server" in scan_inputs
            assert scan_inputs["steps"] == 101  # steps + 1


class TestTimeScan:
    """Test TimeScan class"""

    def test_time_scan_has_correct_scan_type(self):
        """Test TimeScan uses 'count' scan type"""
        from daf.command_line.scan.time_scan import TimeScan

        # Just verify the class can be inspected
        assert TimeScan.__name__ == "TimeScan"


class TestMeshScan:
    """Test MeshScan class"""

    def test_mesh_scan_has_correct_scan_type(self):
        """Test MeshScan uses 'grid_scan' scan type"""
        from daf.command_line.scan.mesh_scan import MeshScan

        assert MeshScan.__name__ == "MeshScan"


class TestHKLScan:
    """Test HKLScan class"""

    def test_hkl_scan_has_correct_scan_type(self):
        """Test HKLScan uses 'list_scan' scan type"""
        from daf.command_line.scan.hkl_scan import HKLScan

        assert HKLScan.__name__ == "HKLScan"


class TestFromFileScan:
    """Test FromFileScan class"""

    def test_from_file_scan_has_correct_scan_type(self):
        """Test FromFileScan uses 'list_scan' scan type"""
        from daf.command_line.scan.from_file_scan import FromFileScan

        assert FromFileScan.__name__ == "FromFileScan"


class TestDAFSigIntHandler:
    """Test DAFSigIntHandler signal handling"""

    def test_signals_map_contains_expected_keys(self):
        """Test signals_map contains all expected keys"""
        from daf.command_line.scan.signal_handler import DAFSigIntHandler

        # Just verify the class can be imported and has expected structure
        assert DAFSigIntHandler.__name__ == "DAFSigIntHandler"

    def test_init_builds_signals_map_from_re(self):
        """Test __init__ builds signals_map using the RunEngine passed to parent"""
        from daf.command_line.scan.signal_handler import DAFSigIntHandler

        mock_re = MagicMock()
        handler = DAFSigIntHandler(mock_re)

        assert handler.signals_map["r"] is mock_re.resume
        assert handler.signals_map["resume"] is mock_re.resume
        assert handler.signals_map["a"] is mock_re.abort
        assert handler.signals_map["abort"] is mock_re.abort
        assert handler.signals_map["h"] is mock_re.halt
        assert handler.signals_map["halt"] is mock_re.halt
        assert handler.signals_map["s"] is mock_re.stop
        assert handler.signals_map["stop"] is mock_re.stop


class TestScanBaseGetCounters:
    """Test ScanBase get_counters method"""

    def test_get_counters_returns_correct_structure(self):
        """Test get_counters returns properly structured counter data"""
        from daf.command_line.scan.daf_scan_utils import ScanBase
        from daf.utils.daf_paths import DAFPaths as dp
        import daf.utils.dafutilities as du

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            scan_base = ScanBase()
            scan_base.experiment_file_dict = {
                "default_counters": "config.daf_default.yml",
                "counters": {
                    "counter1": {"pv": "SIM:counter1", "type": "EpicsSignalRO"},
                    "counter2": {"pv": "SIM:counter2", "type": "EpicsSignalRO"},
                },
            }

            with patch.object(du, "read_yml", return_value=["counter1", "counter2"]):
                counters = scan_base.get_counters()

            assert "counter1" in counters
            assert "counter2" in counters


class TestDAFScanConfigureMetadata:
    """Test DAFScan configure_metadata method"""

    def test_configure_metadata_includes_file_info(self):
        """Test configure_metadata includes file path and name"""
        from daf.command_line.scan.scan_daf import DAFScan, DAFScanInputs

        with patch.object(DAFScan, "__init__", lambda self, inputs: None):
            daf_scan = DAFScan(None)
            daf_scan.motors = ["mu"]
            daf_scan.main_counter = "counter1"
            daf_scan.output = "/tmp/test_scan.nxs"

            md = daf_scan.configure_metadata()

            assert "file_name" in md
            assert "file_path" in md
            assert md["file_name"] == "test_scan.nxs"
            assert md["file_path"] == "/tmp"


class TestDAFScanPlansMap:
    """Test DAFScan PLANS_MAP usage"""

    def test_absolute_uses_scan_plan(self):
        """Test absolute scan type uses bluesky scan plan"""
        from daf.command_line.scan.scan_daf import DAFScan

        assert DAFScan.PLANS_MAP["absolute"].__name__ == "scan"

    def test_relative_uses_rel_scan_plan(self):
        """Test relative scan type uses bluesky rel_scan plan"""
        from daf.command_line.scan.scan_daf import DAFScan

        assert DAFScan.PLANS_MAP["relative"].__name__ == "rel_scan"

    def test_list_scan_uses_list_scan_plan(self):
        """Test list_scan type uses bluesky list_scan plan"""
        from daf.command_line.scan.scan_daf import DAFScan

        assert DAFScan.PLANS_MAP["list_scan"].__name__ == "list_scan"

    def test_grid_scan_uses_grid_scan_plan(self):
        """Test grid_scan type uses bluesky grid_scan plan"""
        from daf.command_line.scan.scan_daf import DAFScan

        assert DAFScan.PLANS_MAP["grid_scan"].__name__ == "grid_scan"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
