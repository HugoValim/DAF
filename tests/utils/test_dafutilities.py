"""
Unit tests for daf.utils.dafutilities module
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import yaml


class TestReadYml(unittest.TestCase):
    def test_read_yml_returns_data(self):
        """Test read_yml reads and parses YAML file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump({"key": "value", "number": 42}, f)
            filepath = f.name

        try:
            from daf.utils.dafutilities import read_yml

            result = read_yml(filepath)

            self.assertEqual(result["key"], "value")
            self.assertEqual(result["number"], 42)
        finally:
            os.unlink(filepath)

    def test_read_yml_with_nested_data(self):
        """Test read_yml handles nested data"""
        nested_data = {
            "motors": {
                "mu": {"pv": "test:mu", "value": 0},
                "eta": {"pv": "test:eta", "value": 0},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump(nested_data, f)
            filepath = f.name

        try:
            from daf.utils.dafutilities import read_yml

            result = read_yml(filepath)

            self.assertEqual(result["motors"]["mu"]["pv"], "test:mu")
        finally:
            os.unlink(filepath)


class TestFetchPvsAndCheckForConnection(unittest.TestCase):
    def test_fetch_pvs_returns_dict(self):
        """Test fetch_pvs_and_check_for_connection returns a dict"""
        with patch("daf.utils.dafutilities.epics") as mock_epics:
            mock_epics.caget.return_value = 0

            with patch("daf.utils.dafutilities.dp") as mock_dp:
                mock_dp.check_for_local_config.return_value = "/tmp/test.yml"

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".yml"
                ) as f:
                    yaml.dump({"motors": {"mu": {"pv": "test:mu", "up": True}}}, f)
                    filepath = f.name

                try:
                    mock_dp.check_for_local_config.return_value = filepath

                    from daf.utils.dafutilities import (
                        fetch_pvs_and_check_for_connection,
                    )

                    result = fetch_pvs_and_check_for_connection()

                    self.assertIsInstance(result, dict)
                    self.assertIn("motors", result)
                finally:
                    os.unlink(filepath)


class TestZeroOfflineMotorsAndBlPvs(unittest.TestCase):
    def test_offline_motors_are_zeroed(self):
        """Test that offline motors are zeroed by the explicit policy function."""
        from daf.utils.dafutilities import zero_offline_motors_and_bl_pvs

        data = {
            "motors": {"mu": {"value": 50.0, "bounds": [-10, 10], "up": False}},
            "beamline_pvs": {},
        }

        zero_offline_motors_and_bl_pvs(data)

        self.assertEqual(data["motors"]["mu"]["value"], 0)
        self.assertEqual(data["motors"]["mu"]["bounds"][0], 0)
        self.assertEqual(data["motors"]["mu"]["bounds"][1], 0)

    def test_online_motors_unchanged(self):
        """Test that online motors are not touched."""
        from daf.utils.dafutilities import zero_offline_motors_and_bl_pvs

        data = {
            "motors": {"mu": {"value": 50.0, "bounds": [-10, 10], "up": True}},
            "beamline_pvs": {},
        }

        zero_offline_motors_and_bl_pvs(data)

        self.assertEqual(data["motors"]["mu"]["value"], 50.0)
        self.assertEqual(data["motors"]["mu"]["bounds"][0], -10)
        self.assertEqual(data["motors"]["mu"]["bounds"][1], 10)

    def test_offline_bl_pvs_are_zeroed(self):
        """Test that offline beamline PVs are zeroed."""
        from daf.utils.dafutilities import zero_offline_motors_and_bl_pvs

        data = {
            "motors": {},
            "beamline_pvs": {"energy": {"value": 8000, "up": False}},
        }

        zero_offline_motors_and_bl_pvs(data)

        self.assertEqual(data["beamline_pvs"]["energy"]["value"], 0)

    def test_online_bl_pvs_unchanged(self):
        """Test that online beamline PVs are not touched."""
        from daf.utils.dafutilities import zero_offline_motors_and_bl_pvs

        data = {
            "motors": {},
            "beamline_pvs": {"energy": {"value": 8000, "up": True}},
        }

        zero_offline_motors_and_bl_pvs(data)

        self.assertEqual(data["beamline_pvs"]["energy"]["value"], 8000)


class TestDAFIO(unittest.TestCase):
    def test_dafio_init_with_read_true(self):
        """Test DAFIO initialization with read=True creates epics client"""
        with patch("daf.utils.dafutilities.EpicsMotorClient") as mock_client:
            with patch("daf.utils.dafutilities.ExperimentFileStore") as mock_store:
                mock_store_instance = MagicMock()
                mock_store_instance.read.return_value = {
                    "motors": {"mu": {"pv": "test:mu", "up": True}},
                    "beamline_pvs": {},
                }
                mock_store.return_value = mock_store_instance

                from daf.utils.dafutilities import DAFIO

                io = DAFIO(read=True)

                self.assertTrue(io.epics_put_flag)
                self.assertTrue(io.epics_get_flag)
                self.assertIsNotNone(io.epics_client)
                mock_client.return_value.build_epics_pvs.assert_called_once()

    def test_dafio_init_with_read_false(self):
        """Test DAFIO initialization with read=False"""
        from daf.utils.dafutilities import DAFIO

        io = DAFIO(read=False)

        self.assertFalse(io.epics_put_flag)
        self.assertFalse(io.epics_get_flag)
        self.assertIsNone(io.epics_client)

    def test_only_read_static_method(self):
        """Test only_read is a static method that reads file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump({"test": "data"}, f)
            filepath = f.name

        try:
            from daf.utils.dafutilities import DAFIO

            result = DAFIO.only_read(filepath)
            self.assertEqual(result["test"], "data")
        finally:
            os.unlink(filepath)


class TestDAFIOWriteAndRead(unittest.TestCase):
    def test_only_read_uses_local_experiment_before_global(self):
        """Test active experiment reads prefer local .Experiment over global."""
        from daf.utils.daf_paths import DAFPaths
        from daf.utils.dafutilities import DAFIO

        with tempfile.TemporaryDirectory() as tmpdir:
            global_dir = os.path.join(tmpdir, "global")
            local_dir = os.path.join(tmpdir, "local")
            os.makedirs(global_dir)
            os.makedirs(local_dir)
            global_file = os.path.join(global_dir, ".Experiment")
            local_file = os.path.join(local_dir, ".Experiment")

            with open(global_file, "w") as f:
                yaml.dump({"source": "global"}, f)
            with open(local_file, "w") as f:
                yaml.dump({"source": "local"}, f)

            current_dir = os.getcwd()
            try:
                os.chdir(local_dir)
                with patch.object(DAFPaths, "GLOBAL_EXPERIMENT_DEFAULT", global_file):
                    result = DAFIO.only_read()
            finally:
                os.chdir(current_dir)

        self.assertEqual(result["source"], "local")

    def test_read_returns_persisted_file_without_epics_overlay(self):
        """Test DAFIO.read returns persisted YAML values, not live EPICS values."""
        persisted_data = {
            "motors": {
                "mu": {
                    "pv": "test:mu",
                    "value": 10.0,
                    "bounds": [-20.0, 20.0],
                    "up": True,
                }
            },
            "beamline_pvs": {
                "energy": {
                    "pv": "test:energy",
                    "value": 8000.0,
                    "up": True,
                    "simulated": False,
                }
            },
        }
        live_data = {
            "motors": {
                "mu": {
                    "pv": "test:mu",
                    "value": 99.0,
                    "bounds": [-1.0, 1.0],
                    "up": True,
                }
            },
            "beamline_pvs": {
                "energy": {
                    "pv": "test:energy",
                    "value": 12000.0,
                    "up": True,
                    "simulated": False,
                }
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump(persisted_data, f)
            filepath = f.name

        try:
            with patch("daf.utils.dafutilities.EpicsMotorClient") as mock_client:
                mock_client.return_value.epics_get.return_value = live_data

                from daf.utils.dafutilities import DAFIO

                io = DAFIO(read=True)
                result = io.read(filepath)

                self.assertEqual(result["motors"]["mu"]["value"], 10.0)
                self.assertEqual(result["motors"]["mu"]["bounds"], [-20.0, 20.0])
                self.assertEqual(result["beamline_pvs"]["energy"]["value"], 8000.0)
                mock_client.return_value.epics_get.assert_not_called()
        finally:
            os.unlink(filepath)

    def test_write_read_cycle(self):
        """Test DAFIO write and read cycle"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            filepath = f.name

        try:
            # Write data
            data = {
                "motors": {
                    "mu": {
                        "pv": "test:mu",
                        "value": 10.0,
                        "bounds": [-180, 180],
                        "up": True,
                    }
                },
                "beamline_pvs": {
                    "energy": {
                        "pv": "test:energy",
                        "value": 8000,
                        "up": True,
                        "simulated": False,
                    }
                },
            }

            from daf.utils.dafutilities import DAFIO

            io = DAFIO(read=False)
            io.write(data, filepath)

            # Read back
            result = DAFIO.only_read(filepath)

            self.assertEqual(result["motors"]["mu"]["value"], 10.0)
        finally:
            os.unlink(filepath)

    def test_write_zeroes_offline_motors_explicitly(self):
        """Test DAFIO write applies offline zeroing explicitly at the seam."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            filepath = f.name

        try:
            data = {
                "motors": {
                    "mu": {
                        "pv": "test:mu",
                        "value": 50.0,
                        "bounds": [-10, 10],
                        "up": False,
                    }
                },
                "beamline_pvs": {
                    "energy": {
                        "pv": "test:energy",
                        "value": 8000,
                        "up": False,
                        "simulated": False,
                    }
                },
            }

            from daf.utils.dafutilities import DAFIO

            io = DAFIO(read=False)
            io.write(data, filepath)

            result = DAFIO.only_read(filepath)
            self.assertEqual(result["motors"]["mu"]["value"], 0)
            self.assertEqual(result["motors"]["mu"]["bounds"][0], 0)
            self.assertEqual(result["motors"]["mu"]["bounds"][1], 0)
            self.assertEqual(result["beamline_pvs"]["energy"]["value"], 0)
        finally:
            os.unlink(filepath)


class TestDAFIOEpicsGetPut(unittest.TestCase):
    def test_epics_get_delegates_to_client(self):
        """Test DAFIO.epics_get delegates to EpicsMotorClient when available."""
        with patch("daf.utils.dafutilities.EpicsMotorClient") as mock_client:
            with patch("daf.utils.dafutilities.ExperimentFileStore") as mock_store:
                mock_store_instance = MagicMock()
                mock_store_instance.read.return_value = {
                    "motors": {"mu": {"pv": "test:mu", "up": True}},
                    "beamline_pvs": {},
                }
                mock_store.return_value = mock_store_instance

                from daf.utils.dafutilities import DAFIO

                io = DAFIO(read=True)
                data = {"motors": {}, "beamline_pvs": {}}
                io.epics_get(data)
                mock_client.return_value.epics_get.assert_called_once_with(data)

    def test_epics_put_delegates_to_client(self):
        """Test DAFIO.epics_put delegates to EpicsMotorClient when available."""
        with patch("daf.utils.dafutilities.EpicsMotorClient") as mock_client:
            with patch("daf.utils.dafutilities.ExperimentFileStore") as mock_store:
                mock_store_instance = MagicMock()
                mock_store_instance.read.return_value = {
                    "motors": {"mu": {"pv": "test:mu", "up": True}},
                    "beamline_pvs": {},
                }
                mock_store.return_value = mock_store_instance

                from daf.utils.dafutilities import DAFIO

                io = DAFIO(read=True)
                data = {"motors": {}, "beamline_pvs": {}}
                io.epics_put(data)
                mock_client.return_value.epics_put.assert_called_once_with(data)

    def test_epics_get_no_op_when_read_false(self):
        """Test DAFIO.epics_get is a no-op when epics client is None."""
        from daf.utils.dafutilities import DAFIO

        io = DAFIO(read=False)
        data = {"motors": {}, "beamline_pvs": {}}
        result = io.epics_get(data)
        self.assertEqual(result, data)

    def test_epics_put_no_op_when_read_false(self):
        """Test DAFIO.epics_put is a no-op when epics client is None."""
        from daf.utils.dafutilities import DAFIO

        io = DAFIO(read=False)
        data = {"motors": {}, "beamline_pvs": {}}
        io.epics_put(data)
        # Should not raise


if __name__ == "__main__":
    unittest.main()
