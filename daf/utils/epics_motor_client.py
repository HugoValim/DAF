#!/usr/bin/env python3
"""EPICS PV communication for motors and beamline PVs."""
from __future__ import annotations

import atexit
import logging
import time
from typing import Any

import epics

logger = logging.getLogger(__name__)

TIMEOUT = 2  # timeout for caputs and cagets
_ENERGY_KEV_THRESHOLD = 100  # Threshold below which beamline PV values are in keV


class EpicsMotorClient:
    """Handles EPICS PV communication for motors and beamline PVs."""

    def __init__(self) -> None:
        self.MOTOR_PVS: dict[str, str] = {}
        self.BL_PVS: dict[str, str] = {}
        self.motor_pv_list: list[str] = []
        self.rbv_motor_pv_list: list[str] = []
        self.llm_motor_pv_list: list[str] = []
        self.hlm_motor_pv_list: list[str] = []
        self.stop_motor_pv_list: list[str] = []
        self.bl_pv_list: list[str] = []

    def build_epics_pvs(self, dict_now: dict[str, Any]) -> None:
        """Build PV lists from an experiment dict for caput/caget many."""
        self.MOTOR_PVS = {
            key: dict_now["motors"][key]["pv"]
            for key in dict_now["motors"].keys()
            if dict_now["motors"][key]["up"]
        }
        self.BL_PVS = {
            key: dict_now["beamline_pvs"][key]["pv"]
            for key in dict_now["beamline_pvs"].keys()
            if not dict_now["beamline_pvs"][key]["simulated"]
            and dict_now["beamline_pvs"][key]["up"]
        }

        self.motor_pv_list = [pv for pv in self.MOTOR_PVS.values()]
        self.rbv_motor_pv_list = [pv + ".RBV" for pv in self.MOTOR_PVS.values()]
        self.llm_motor_pv_list = [pv + ".LLM" for pv in self.MOTOR_PVS.values()]
        self.hlm_motor_pv_list = [pv + ".HLM" for pv in self.MOTOR_PVS.values()]
        self.stop_motor_pv_list = [pv + ".STOP" for pv in self.MOTOR_PVS.values()]
        self.bl_pv_list = [pv for pv in self.BL_PVS.values()]

    def stop(self) -> None:
        """Stop all motors."""
        epics.caput_many(
            self.stop_motor_pv_list,
            [1 for _ in self.stop_motor_pv_list],
            connection_timeout=TIMEOUT,
        )

    def wait(self) -> None:
        """Wait for all motors to reach their position."""
        atexit.register(self.stop)
        for motor in self.motor_pv_list:
            while True:
                is_moving = epics.caget(motor + ".MOVN", timeout=TIMEOUT)
                if not is_moving:
                    break
                time.sleep(0.1)

    def epics_get(self, dict_: dict[str, Any]) -> dict[str, Any]:
        """Sync DAF with PVs by reading motor positions and beamline values."""
        updated_rbv_motor_pv_list = epics.caget_many(
            self.rbv_motor_pv_list, timeout=TIMEOUT
        )
        updated_llm_motor_pv_list = epics.caget_many(
            self.llm_motor_pv_list, timeout=TIMEOUT
        )
        updated_hlm_motor_pv_list = epics.caget_many(
            self.hlm_motor_pv_list, timeout=TIMEOUT
        )
        updated_bl_pv_list = epics.caget_many(self.bl_pv_list, timeout=TIMEOUT)

        motor_counter = 0
        for key in self.MOTOR_PVS.keys():
            dict_["motors"][key]["value"] = updated_rbv_motor_pv_list[motor_counter]
            dict_["motors"][key]["bounds"] = [
                updated_llm_motor_pv_list[motor_counter],
                updated_hlm_motor_pv_list[motor_counter],
            ]
            motor_counter += 1

        bl_counter = 0
        for key in self.BL_PVS.keys():
            if (
                updated_bl_pv_list[bl_counter] is not None
                and updated_bl_pv_list[bl_counter] < _ENERGY_KEV_THRESHOLD
            ):
                dict_["beamline_pvs"][key]["value"] = (
                    updated_bl_pv_list[bl_counter] * 1000
                )
            else:
                dict_["beamline_pvs"][key]["value"] = 1
            bl_counter += 1
        return dict_

    def epics_put(self, dict_: dict[str, Any]) -> None:
        """Write motor values and bounds to PVs."""
        set_motor_pv_list = [
            dict_["motors"][key]["value"] for key in self.MOTOR_PVS.keys()
        ]
        epics.caput_many(
            self.motor_pv_list,
            set_motor_pv_list,
            connection_timeout=TIMEOUT,
        )
        set_llm_motor_pv_list = [
            dict_["motors"][key]["bounds"][0] for key in self.MOTOR_PVS.keys()
        ]
        epics.caput_many(
            self.llm_motor_pv_list,
            set_llm_motor_pv_list,
            connection_timeout=TIMEOUT,
        )
        set_hlm_motor_pv_list = [
            dict_["motors"][key]["bounds"][1] for key in self.MOTOR_PVS.keys()
        ]
        epics.caput_many(
            self.hlm_motor_pv_list,
            set_hlm_motor_pv_list,
            connection_timeout=TIMEOUT,
        )
        self.wait()
