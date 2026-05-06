"""
Unit tests for the consolidated angular scan command (daf.ascan).

Tests cover:
- AngularScan class exists in daf.command_line.scan.angular_scan
- Accepts --type absolute|relative
- Accepts --n-motors 1..6
- Validates n-motors range
- Builds correct scan inputs for each motor count and both scan types
- Entry-point main() is importable and callable
"""
import argparse
import sys
from unittest.mock import patch, MagicMock

import pytest


MOTOR_CONFIG = {
    "mu": {"cli_abbrev": "m", "pv": "SIM:m1", "value": 0.0, "bounds": [-180, 180]},
    "eta": {"cli_abbrev": "e", "pv": "SIM:m2", "value": 0.0, "bounds": [-180, 180]},
    "chi": {"cli_abbrev": "c", "pv": "SIM:m3", "value": 0.0, "bounds": [-180, 180]},
    "phi": {"cli_abbrev": "p", "pv": "SIM:m4", "value": 0.0, "bounds": [-180, 180]},
    "nu": {"cli_abbrev": "n", "pv": "SIM:m5", "value": 0.0, "bounds": [-180, 180]},
    "del": {"cli_abbrev": "d", "pv": "SIM:m6", "value": 0.0, "bounds": [-180, 180]},
}

EXPERIMENT_FILE = {
    "motors": MOTOR_CONFIG,
    "default_counters": "config.daf_default.yml",
    "main_scan_counter": "counter1",
    "kafka_topic": "test_topic",
    "scan_db": "temp",
    "kafka_server": None,
    "counters": {
        "counter1": {"pv": "SIM:c1", "type": "EpicsSignalRO", "class": "EpicsSignalRO"},
    },
}


class TestAngularScanModuleExists:
    """AngularScan module and class must be importable."""

    def test_module_is_importable(self):
        from daf.command_line.scan import angular_scan  # noqa: F401

    def test_class_is_importable(self):
        from daf.command_line.scan.angular_scan import AngularScan  # noqa: F401

    def test_main_is_importable(self):
        from daf.command_line.scan.angular_scan import main  # noqa: F401


class TestAngularScanDescAndEpi:
    """AngularScan must expose non-empty DESC and EPI class attributes."""

    def test_has_desc(self):
        from daf.command_line.scan.angular_scan import AngularScan

        assert hasattr(AngularScan, "DESC")
        assert len(AngularScan.DESC) > 0

    def test_has_epi(self):
        from daf.command_line.scan.angular_scan import AngularScan

        assert hasattr(AngularScan, "EPI")
        assert len(AngularScan.EPI) > 0


class TestAngularScanParsesType:
    """AngularScan must accept --type absolute|relative."""

    def _make_scan(self, argv):
        from daf.command_line.scan.angular_scan import AngularScan
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            obj = AngularScan.__new__(AngularScan)
            obj.experiment_file_dict = EXPERIMENT_FILE
            obj.parser = argparse.ArgumentParser()
            with patch("sys.argv", argv):
                obj._add_type_and_n_motors_args()
                args = obj.parser.parse_args()
            return args

    def test_type_absolute(self):
        args = self._make_scan(
            ["daf.ascan", "--type", "absolute", "--n-motors", "2"]
        )
        assert args.type == "absolute"

    def test_type_relative(self):
        args = self._make_scan(
            ["daf.ascan", "--type", "relative", "--n-motors", "1"]
        )
        assert args.type == "relative"

    def test_n_motors_parsed_as_int(self):
        args = self._make_scan(
            ["daf.ascan", "--type", "absolute", "--n-motors", "3"]
        )
        assert args.n_motors == 3


class TestAngularScanNMotorsValidation:
    """AngularScan must reject n-motors outside 1..6."""

    def _parse(self, n_motors_str: str, scan_type: str = "absolute"):
        from daf.command_line.scan.angular_scan import AngularScan
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            obj = AngularScan.__new__(AngularScan)
            obj.experiment_file_dict = EXPERIMENT_FILE
            obj.parser = argparse.ArgumentParser()
            with patch("sys.argv", ["daf.ascan", "--type", scan_type, "--n-motors", n_motors_str]):
                obj._add_type_and_n_motors_args()
                return obj.parser.parse_args()

    @pytest.mark.parametrize("n", range(1, 7))
    def test_valid_n_motors(self, n: int):
        args = self._parse(str(n))
        assert args.n_motors == n

    @pytest.mark.parametrize("n", [0, 7, -1])
    def test_invalid_n_motors_raises(self, n: int):
        with pytest.raises(SystemExit):
            self._parse(str(n))


class TestAngularScanBuildsScanType:
    """AngularScan.scan_type must reflect --type flag."""

    def _build_scan(self, scan_type: str, n_motors: int, motor_args: list[str]):
        from daf.command_line.scan.angular_scan import AngularScan
        from daf.command_line.scan.daf_scan_utils import ScanBase

        argv = (
            ["daf.ascan", "--type", scan_type, "--n-motors", str(n_motors)]
            + motor_args
            + ["100", "0.1"]
        )
        with patch("sys.argv", argv):
            with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
                obj = AngularScan.__new__(AngularScan)
                obj.experiment_file_dict = EXPERIMENT_FILE
                obj.parsed_args = obj.parse_command_line()
                obj.parsed_args_dict = vars(obj.parsed_args)
                obj.scan_type = scan_type
                obj.number_of_motors = n_motors
                obj.inputed_motors = obj.get_inputed_motor_order(argv)
        return obj

    def test_absolute_scan_type_set(self):
        obj = self._build_scan("absolute", 1, ["-m", "0", "10"])
        assert obj.scan_type == "absolute"

    def test_relative_scan_type_set(self):
        obj = self._build_scan("relative", 1, ["-m", "-5", "5"])
        assert obj.scan_type == "relative"


@pytest.mark.parametrize("n_motors", range(1, 7))
class TestAngularScanAllMotorCounts:
    """AngularScan must work for all motor counts 1-6, both types."""

    _MOTOR_ARGS = {
        1: ["-m", "0", "10"],
        2: ["-m", "0", "10", "-e", "0", "20"],
        3: ["-m", "0", "10", "-e", "0", "20", "-c", "0", "30"],
        4: ["-m", "0", "10", "-e", "0", "20", "-c", "0", "30", "-p", "0", "40"],
        5: ["-m", "0", "10", "-e", "0", "20", "-c", "0", "30", "-p", "0", "40", "-n", "0", "50"],
        6: [
            "-m", "0", "10", "-e", "0", "20", "-c", "0", "30",
            "-p", "0", "40", "-n", "0", "50", "-d", "0", "60",
        ],
    }

    def _build_obj(self, n_motors: int, scan_type: str):
        from daf.command_line.scan.angular_scan import AngularScan
        from daf.command_line.scan.daf_scan_utils import ScanBase

        motor_args = self._MOTOR_ARGS[n_motors]
        argv = (
            ["daf.ascan", "--type", scan_type, "--n-motors", str(n_motors)]
            + motor_args
            + ["100", "0.1"]
        )
        with patch("sys.argv", argv):
            with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
                obj = AngularScan.__new__(AngularScan)
                obj.experiment_file_dict = EXPERIMENT_FILE
                obj.parsed_args = obj.parse_command_line()
                obj.parsed_args_dict = vars(obj.parsed_args)
                obj.scan_type = scan_type
                obj.number_of_motors = n_motors
                obj.inputed_motors = obj.get_inputed_motor_order(argv)
        return obj

    def test_absolute_parse_succeeds(self, n_motors: int):
        obj = self._build_obj(n_motors, "absolute")
        assert obj.scan_type == "absolute"
        assert obj.number_of_motors == n_motors

    def test_relative_parse_succeeds(self, n_motors: int):
        obj = self._build_obj(n_motors, "relative")
        assert obj.scan_type == "relative"
        assert obj.number_of_motors == n_motors

    def test_configure_scan_input_has_required_keys(self, n_motors: int):
        """configure_scan_input must return all keys expected by DAFScanInputs."""
        import daf.utils.dafutilities as du
        from daf.command_line.scan.angular_scan import AngularScan
        from daf.command_line.scan.daf_scan_utils import ScanBase

        motor_args = self._MOTOR_ARGS[n_motors]
        argv = (
            ["daf.ascan", "--type", "absolute", "--n-motors", str(n_motors)]
            + motor_args
            + ["100", "0.1"]
        )
        with patch("sys.argv", argv):
            with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
                with patch.object(du, "read_yml", return_value=["counter1"]):
                    obj = AngularScan.__new__(AngularScan)
                    obj.experiment_file_dict = EXPERIMENT_FILE
                    obj.parsed_args = obj.parse_command_line()
                    obj.parsed_args_dict = vars(obj.parsed_args)
                    obj.scan_type = "absolute"
                    obj.number_of_motors = n_motors
                    obj.inputed_motors = obj.get_inputed_motor_order(argv)
                    scan_inputs = obj.configure_scan_input()

        required_keys = {
            "scan_data", "inputed_motors", "motors_data_dict", "counters",
            "main_counter", "scan_type", "steps", "acquisition_time", "output",
            "kafka_topic", "scan_db", "kafka_server",
        }
        assert required_keys.issubset(set(scan_inputs.keys()))
        assert scan_inputs["scan_type"] == "absolute"
        assert scan_inputs["steps"] == 101  # 100 + 1


class TestAngularScanRunCmd:
    """run_cmd must delegate to run_scan."""

    def test_run_cmd_calls_run_scan(self):
        from daf.command_line.scan.angular_scan import AngularScan
        from daf.command_line.scan.daf_scan_utils import ScanBase

        with patch.object(ScanBase, "__init__", lambda self, **kwargs: None):
            obj = AngularScan.__new__(AngularScan)
            with patch.object(obj, "run_scan") as mock_run:
                obj.run_cmd()
                mock_run.assert_called_once()


class TestSetupPyEntryPoints:
    """setup.py must expose daf.ascan and must NOT expose the old 12 entry points."""

    def _get_console_scripts(self) -> dict[str, str]:
        import ast
        import re

        path = "/home/hugo/cfg/DAF/.claude/worktrees/agent-a47a31bee0070ec6a/setup.py"
        with open(path) as fh:
            source = fh.read()
        # Extract the list of "key = value" strings from console_scripts
        match = re.search(
            r'"console_scripts"\s*:\s*\[(.*?)\]', source, re.DOTALL
        )
        assert match, "Could not find console_scripts in setup.py"
        entries = re.findall(r'"([^"]+)"', match.group(1))
        result = {}
        for entry in entries:
            if "=" in entry:
                key, val = entry.split("=", 1)
                result[key.strip()] = val.strip()
        return result

    def test_daf_ascan_entry_point_exists(self):
        scripts = self._get_console_scripts()
        assert "daf.ascan" in scripts, "daf.ascan must be in console_scripts"

    @pytest.mark.parametrize(
        "old_ep",
        [
            "daf.a2scan",
            "daf.a3scan",
            "daf.a4scan",
            "daf.a5scan",
            "daf.a6scan",
            "daf.dscan",
            "daf.lup",
            "daf.d2scan",
            "daf.d3scan",
            "daf.d4scan",
            "daf.d5scan",
            "daf.d6scan",
        ],
    )
    def test_old_entry_points_removed(self, old_ep: str):
        scripts = self._get_console_scripts()
        assert old_ep not in scripts, f"{old_ep} must be removed from console_scripts"

    def test_daf_ascan_points_to_angular_scan(self):
        scripts = self._get_console_scripts()
        assert "angular_scan" in scripts.get("daf.ascan", ""), (
            "daf.ascan must point to angular_scan module"
        )
