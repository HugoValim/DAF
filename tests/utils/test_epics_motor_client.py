"""
Unit tests for daf.utils.epics_motor_client module.
"""
import unittest
from unittest.mock import patch

from daf.utils.epics_motor_client import EpicsMotorClient


class TestEpicsMotorClient(unittest.TestCase):
    def test_build_epics_pvs_filters_offline_motors(self):
        """Test that build_epics_pvs excludes motors with up=False."""
        client = EpicsMotorClient()
        data = {
            "motors": {
                "mu": {"pv": "SIM:m1", "up": True},
                "eta": {"pv": "SIM:m2", "up": False},
            },
            "beamline_pvs": {
                "energy": {"pv": "SIM:energy", "up": True, "simulated": False}
            },
        }
        client.build_epics_pvs(data)

        self.assertIn("mu", client.MOTOR_PVS)
        self.assertNotIn("eta", client.MOTOR_PVS)
        self.assertEqual(client.motor_pv_list, ["SIM:m1"])

    def test_build_epics_pvs_filters_simulated_bl_pvs(self):
        """Test that build_epics_pvs excludes simulated beamline PVs."""
        client = EpicsMotorClient()
        data = {
            "motors": {"mu": {"pv": "SIM:m1", "up": True}},
            "beamline_pvs": {
                "energy": {"pv": "SIM:energy", "up": True, "simulated": True},
                "ring_current": {
                    "pv": "SIM:rc",
                    "up": True,
                    "simulated": False,
                },
            },
        }
        client.build_epics_pvs(data)

        self.assertNotIn("energy", client.BL_PVS)
        self.assertIn("ring_current", client.BL_PVS)

    def test_stop_calls_caput_many(self):
        """Test stop delegates to epics.caput_many."""
        with patch("daf.utils.epics_motor_client.epics") as mock_epics:
            client = EpicsMotorClient()
            client.stop_motor_pv_list = ["SIM:m1.STOP"]
            client.stop()

            mock_epics.caput_many.assert_called_once()
            args, kwargs = mock_epics.caput_many.call_args
            self.assertEqual(args[0], ["SIM:m1.STOP"])
            self.assertEqual(args[1], [1])

    def test_epics_get_updates_motor_values(self):
        """Test epics_get updates dict with PV readback values."""
        with patch("daf.utils.epics_motor_client.epics") as mock_epics:
            mock_epics.caget_many.side_effect = [
                [10.0],  # RBV
                [-180.0],  # LLM
                [180.0],  # HLM
                [8.0],  # BL PV (energy in keV -> should be multiplied by 1000)
            ]

            client = EpicsMotorClient()
            client.MOTOR_PVS = {"mu": "SIM:m1"}
            client.BL_PVS = {"energy": "SIM:energy"}
            client.rbv_motor_pv_list = ["SIM:m1.RBV"]
            client.llm_motor_pv_list = ["SIM:m1.LLM"]
            client.hlm_motor_pv_list = ["SIM:m1.HLM"]
            client.bl_pv_list = ["SIM:energy"]

            data = {
                "motors": {"mu": {"value": 0.0, "bounds": [0, 0]}},
                "beamline_pvs": {"energy": {"value": 0}},
            }
            result = client.epics_get(data)

            self.assertEqual(result["motors"]["mu"]["value"], 10.0)
            self.assertEqual(result["motors"]["mu"]["bounds"], [-180.0, 180.0])
            self.assertEqual(result["beamline_pvs"]["energy"]["value"], 8000.0)

    def test_epics_get_energy_above_threshold_sets_one(self):
        """Test epics_get sets energy to 1 when PV value is above threshold."""
        with patch("daf.utils.epics_motor_client.epics") as mock_epics:
            mock_epics.caget_many.side_effect = [
                [10.0],  # RBV
                [-180.0],  # LLM
                [180.0],  # HLM
                [200.0],  # BL PV above threshold
            ]

            client = EpicsMotorClient()
            client.MOTOR_PVS = {"mu": "SIM:m1"}
            client.BL_PVS = {"energy": "SIM:energy"}
            client.rbv_motor_pv_list = ["SIM:m1.RBV"]
            client.llm_motor_pv_list = ["SIM:m1.LLM"]
            client.hlm_motor_pv_list = ["SIM:m1.HLM"]
            client.bl_pv_list = ["SIM:energy"]

            data = {
                "motors": {"mu": {"value": 0.0, "bounds": [0, 0]}},
                "beamline_pvs": {"energy": {"value": 0}},
            }
            result = client.epics_get(data)

            self.assertEqual(result["beamline_pvs"]["energy"]["value"], 1)

    def test_epics_put_writes_motor_values(self):
        """Test epics_put writes motor values and bounds to PVs."""
        with patch("daf.utils.epics_motor_client.epics") as mock_epics:
            with patch.object(EpicsMotorClient, "wait"):
                client = EpicsMotorClient()
                client.MOTOR_PVS = {"mu": "SIM:m1"}
                client.motor_pv_list = ["SIM:m1"]
                client.llm_motor_pv_list = ["SIM:m1.LLM"]
                client.hlm_motor_pv_list = ["SIM:m1.HLM"]

                data = {
                    "motors": {"mu": {"value": 15.0, "bounds": [-90, 90]}},
                }
                client.epics_put(data)

                self.assertEqual(mock_epics.caput_many.call_count, 3)


if __name__ == "__main__":
    unittest.main()
