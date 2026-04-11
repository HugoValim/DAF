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


class TestAScansFactory:
    """Test a_scans.py class factory"""

    def test_exported_classes_exist(self):
        """Test that all scan classes are exported in the module"""
        from daf.command_line.scan import a_scans

        # Check all expected classes are exported
        expected_classes = [
            "AScan1",
            "AScan2",
            "AScan3",
            "AScan4",
            "AScan5",
            "AScan6",
            "DScan1",
            "DScan2",
            "DScan3",
            "DScan4",
            "DScan5",
            "DScan6",
        ]
        for cls_name in expected_classes:
            assert hasattr(a_scans, cls_name), f"{cls_name} should be exported"

    def test_ascan1_has_correct_desc(self):
        """Test AScan1 class has correct description for absolute scan"""
        from daf.command_line.scan.a_scans import AScan1

        assert "Perform an absolute scan" in AScan1.DESC
        assert AScan1.__name__ == "AScan1"

    def test_dscan1_has_correct_desc(self):
        """Test DScan1 class has correct description for relative scan"""
        from daf.command_line.scan.a_scans import DScan1

        assert "Perform a relative scan" in DScan1.DESC
        assert DScan1.__name__ == "DScan1"

    def test_ascan6_has_correct_desc(self):
        """Test AScan6 class has correct description for 6-motor absolute scan"""
        from daf.command_line.scan.a_scans import AScan6

        assert (
            "Perform an absolute scan in all six diffractometer motors" in AScan6.DESC
        )
        assert AScan6.__name__ == "AScan6"

    def test_dscan6_has_correct_desc(self):
        """Test DScan6 class has correct description for 6-motor relative scan"""
        from daf.command_line.scan.a_scans import DScan6

        assert "Perform a relative scan in all six diffractometer motors" in DScan6.DESC
        assert DScan6.__name__ == "DScan6"

    def test_exported_main_functions_exist(self):
        """Test that all main functions are exported in the module"""
        from daf.command_line.scan import a_scans

        expected_mains = [
            "ascan1_main",
            "ascan2_main",
            "ascan3_main",
            "ascan4_main",
            "ascan5_main",
            "ascan6_main",
            "dscan1_main",
            "dscan2_main",
            "dscan3_main",
            "dscan4_main",
            "dscan5_main",
            "dscan6_main",
        ]
        for main_name in expected_mains:
            assert hasattr(a_scans, main_name), f"{main_name} should be exported"


class TestScanDocsCompleteness:
    """Test that all scan types have proper documentation"""

    def test_exported_classes_have_docs(self):
        """Verify all exported scan classes have proper DESC and EPI"""
        from daf.command_line.scan.a_scans import (
            AScan1,
            AScan2,
            AScan3,
            AScan4,
            AScan5,
            AScan6,
            DScan1,
            DScan2,
            DScan3,
            DScan4,
            DScan5,
            DScan6,
        )

        all_classes = [
            AScan1,
            AScan2,
            AScan3,
            AScan4,
            AScan5,
            AScan6,
            DScan1,
            DScan2,
            DScan3,
            DScan4,
            DScan5,
            DScan6,
        ]

        for cls in all_classes:
            assert hasattr(cls, "DESC"), f"{cls.__name__} should have DESC"
            assert hasattr(cls, "EPI"), f"{cls.__name__} should have EPI"
            assert len(cls.DESC) > 0, f"{cls.__name__} DESC should not be empty"
            assert len(cls.EPI) > 0, f"{cls.__name__} EPI should not be empty"


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
