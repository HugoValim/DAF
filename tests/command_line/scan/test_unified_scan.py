"""
Unit tests for the unified motor scan command.
"""
import sys
from unittest.mock import patch
import pytest


class TestUnifiedScanParsing:
    """Test UnifiedScan argument parsing and validation."""

    @pytest.mark.parametrize("scan_type", ["absolute", "relative"])
    @pytest.mark.parametrize("n_motors", [1, 2, 3, 4, 5, 6])
    def test_unified_scan_accepts_valid_type_and_n_motors(
        self, scan_type, n_motors, monkeypatch
    ):
        """Test UnifiedScan accepts all valid --type and --n-motors combinations."""
        from daf.command_line.scan.unified_scan import UnifiedScan

        abbrev_map = {
            "mu": "m",
            "eta": "e",
            "chi": "c",
            "phi": "p",
            "nu": "n",
            "del": "d",
        }
        motors = list(abbrev_map.keys())
        argv = ["daf.scan", f"--type={scan_type}", f"--n-motors={n_motors}"]
        for i in range(n_motors):
            motor = motors[i]
            argv.extend([f"--{motor}", str(float(i)), str(float(i + 1))])
        argv.extend(["10", "0.1"])  # step and time

        monkeypatch.setattr(sys, "argv", argv)

        with patch.object(UnifiedScan, "run_scan"):
            scan = UnifiedScan()
            assert scan.scan_type == scan_type
            assert scan.number_of_motors == n_motors
            assert len(scan.inputed_motors) == n_motors

    def test_unified_scan_rejects_wrong_motor_count(self, monkeypatch):
        """Test UnifiedScan errors when motor count doesn't match --n-motors."""
        from daf.command_line.scan.unified_scan import UnifiedScan

        argv = [
            "daf.scan",
            "--type=absolute",
            "--n-motors=3",
            "--mu",
            "1",
            "10",
            "10",
            "0.1",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        with pytest.raises(SystemExit):
            UnifiedScan()

    def test_unified_scan_rejects_invalid_type(self, monkeypatch):
        """Test UnifiedScan errors on invalid --type."""
        from daf.command_line.scan.unified_scan import UnifiedScan

        argv = [
            "daf.scan",
            "--type=invalid",
            "--n-motors=1",
            "--mu",
            "1",
            "10",
            "10",
            "0.1",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        with pytest.raises(SystemExit):
            UnifiedScan()

    def test_unified_scan_rejects_invalid_n_motors(self, monkeypatch):
        """Test UnifiedScan errors on --n-motors outside 1-6."""
        from daf.command_line.scan.unified_scan import UnifiedScan

        argv = [
            "daf.scan",
            "--type=absolute",
            "--n-motors=7",
            "--mu",
            "1",
            "10",
            "10",
            "0.1",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        with pytest.raises(SystemExit):
            UnifiedScan()

    def test_unified_scan_rejects_zero_n_motors(self, monkeypatch):
        """Test UnifiedScan errors on --n-motors=0."""
        from daf.command_line.scan.unified_scan import UnifiedScan

        argv = [
            "daf.scan",
            "--type=absolute",
            "--n-motors=0",
            "--mu",
            "1",
            "10",
            "10",
            "0.1",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        with pytest.raises(SystemExit):
            UnifiedScan()


class TestUnifiedScanRunCmd:
    """Test UnifiedScan run_cmd delegates to run_scan."""

    def test_run_cmd_calls_run_scan(self, monkeypatch):
        """Test that run_cmd invokes run_scan."""
        from daf.command_line.scan.unified_scan import UnifiedScan

        argv = [
            "daf.scan",
            "--type=absolute",
            "--n-motors=1",
            "--mu",
            "1",
            "10",
            "10",
            "0.1",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        with patch.object(UnifiedScan, "run_scan") as mock_run_scan:
            scan = UnifiedScan()
            scan.run_cmd()
            mock_run_scan.assert_called_once()


class TestUnifiedScanIntegration:
    """Integration-style tests for UnifiedScan with mocked DAFIO."""

    @pytest.fixture
    def mock_experiment(self):
        """Return a minimal experiment dict for scan parsing."""
        return {
            "motors": {
                "mu": {
                    "cli_abbrev": "m",
                    "pv": "SIM:m1",
                    "value": 0.0,
                    "bounds": [-180, 180],
                },
                "eta": {
                    "cli_abbrev": "e",
                    "pv": "SIM:m2",
                    "value": 0.0,
                    "bounds": [-180, 180],
                },
                "chi": {
                    "cli_abbrev": "c",
                    "pv": "SIM:m3",
                    "value": 0.0,
                    "bounds": [-5, 95],
                },
                "phi": {
                    "cli_abbrev": "p",
                    "pv": "SIM:m4",
                    "value": 0.0,
                    "bounds": [30, 400],
                },
                "nu": {
                    "cli_abbrev": "n",
                    "pv": "SIM:m5",
                    "value": 0.0,
                    "bounds": [-180, 180],
                },
                "del": {
                    "cli_abbrev": "d",
                    "pv": "SIM:m6",
                    "value": 0.0,
                    "bounds": [-180, 180],
                },
            },
            "default_counters": "config.daf_default.yml",
            "main_scan_counter": None,
            "kafka_topic": "EMA_bluesky",
            "scan_db": "temp",
            "kafka_server": "localhost:9092",
            "counters": {},
        }

    def test_configure_scan_input_matches_n_motors(self, mock_experiment, monkeypatch):
        """Test configure_scan_input reflects the correct number of motors."""
        from daf.command_line.scan.unified_scan import UnifiedScan

        argv = [
            "daf.scan",
            "--type=relative",
            "--n-motors=2",
            "--mu",
            "-2",
            "2",
            "--eta",
            "-4",
            "4",
            "10",
            "0.1",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        with patch.object(UnifiedScan, "run_scan"):
            with patch.object(UnifiedScan, "__init__", lambda self, **kwargs: None):
                scan = UnifiedScan()
                scan.experiment_file_dict = mock_experiment
                scan.parser = None  # Will be recreated by parse_command_line
                # Need to re-init parser and parse args manually
                import argparse

                scan.parser = argparse.ArgumentParser()
                scan.parser.add_argument("--type", choices=["absolute", "relative"])
                scan.parser.add_argument(
                    "--n-motors", type=int, choices=[1, 2, 3, 4, 5, 6]
                )
                for motor in mock_experiment["motors"].keys():
                    abbrev = mock_experiment["motors"][motor]["cli_abbrev"]
                    scan.parser.add_argument(
                        f"-{abbrev}", f"--{motor}", type=float, nargs=2
                    )
                scan.parser.add_argument("step", type=int)
                scan.parser.add_argument("time", type=float)
                scan.parser.add_argument("-o", "--output", default="/tmp/scan.nxs")
                args = scan.parser.parse_args(argv[1:])
                scan.parsed_args_dict = vars(args)
                scan.inputed_motors = ["mu", "eta"]
                scan.number_of_motors = 2
                scan.scan_type = "relative"

                with patch.object(scan, "get_counters", return_value={}):
                    scan_inputs = scan.configure_scan_input()

                assert scan_inputs["scan_type"] == "relative"
                assert scan_inputs["steps"] == 11  # 10 + 1
                assert scan_inputs["inputed_motors"] == ["mu", "eta"]
                assert "mu" in scan_inputs["scan_data"]
                assert "eta" in scan_inputs["scan_data"]
