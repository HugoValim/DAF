#!/usr/bin/env python3
"""Library for reading and writing experiment files"""

import atexit
import os
import time

import epics
import yaml

from daf.utils.daf_paths import DAFPaths as dp

DEFAULT = dp.check_for_local_config()
TIMEOUT = 2  # .2s timeout for caputs and cagets


def read_yml(filepath: str = None):
    """Just get the data from .Experiment file without any epics command"""
    with open(filepath) as file:
        data = yaml.safe_load(file)
        return data


def fetch_pvs_and_check_for_connection():
    """Fetch all motos PVs to check if it is connect or not. If it is not connected change the up bit to 0"""
    file = dp.check_for_local_config()
    data = read_yml(file)
    for key in data["motors"].keys():
        val = epics.caget(data["motors"][key]["pv"], timeout=2)
        if val is None:
            print("Cannot connect to {}, PV: {}".format(key, data["motors"][key]["pv"]))
            data["motors"][key]["up"] = 0
    return data


class DAFIO:
    def __init__(self, read=True):
        if read:
            self.build_epics_pvs()
            self.epics_put_flag = True
            self.epics_get_flag = True
        else:
            self.epics_put_flag = False
            self.epics_get_flag = False

    def build_epics_pvs(self):
        """Build PVs list to work with caput/caget many"""
        if os.path.isfile(DEFAULT):
            dict_now = self.only_read()
            self.MOTOR_PVS = {
                key: dict_now["motors"][key]["pv"]
                for key, value in dict_now["motors"].items()
                if dict_now["motors"][key]["up"]
            }
            self.BL_PVS = {
                key: dict_now["beamline_pvs"][key]["pv"]
                for key, value in dict_now["beamline_pvs"].items()
                if not dict_now["beamline_pvs"][key]["simulated"]
                and dict_now["beamline_pvs"][key]["up"]
            }

            self.motor_pv_list = [pv for pv in self.MOTOR_PVS.values()]
            self.rbv_motor_pv_list = [pv + ".RBV" for pv in self.MOTOR_PVS.values()]
            self.llm_motor_pv_list = [pv + ".LLM" for pv in self.MOTOR_PVS.values()]
            self.hlm_motor_pv_list = [pv + ".HLM" for pv in self.MOTOR_PVS.values()]
            self.stop_motor_pv_list = [pv + ".STOP" for pv in self.MOTOR_PVS.values()]
            self.bl_pv_list = [pv for pv in self.BL_PVS.values()]

    def sync_with_environment(self):
        """Get PVs and sync with it"""
        self.write(self.read())

    @staticmethod
    def only_read(filepath=DEFAULT):
        """Just get the data from .Experiment file without any epics command"""
        with open(filepath) as file:
            data = yaml.safe_load(file)
            return data

    def stop(self):
        """Stop all motors"""
        epics.caput_many(
            self.stop_motor_pv_list,
            [1 for i in self.stop_motor_pv_list],
            connection_timeout=TIMEOUT,
        )

    def wait(self):
        """Wait for all motors to reach its position"""
        atexit.register(self.stop)
        for motor in self.motor_pv_list:
            while True:
                is_moving = epics.caget(motor + ".MOVN", timeout=TIMEOUT)
                if not is_moving:
                    break
                time.sleep(0.1)

    def epics_get(self, dict_):
        """Method to sync DAF with PVs"""
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
        for key, value in self.BL_PVS.items():
            if updated_bl_pv_list[bl_counter] is not None and updated_bl_pv_list[bl_counter] < 100:  # Less them 100keV
                dict_["beamline_pvs"][key]["value"] = (
                    updated_bl_pv_list[bl_counter] * 1000
                )
            else:
                dict_["beamline_pvs"][key]["value"] = 1
                bl_counter += 1
        return dict_

    def epics_put(self, dict_):
        """Method to write inputed values to PV"""
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

    def read(self, filepath=DEFAULT):
        """Read data from the experiment file"""
        with open(filepath) as file:
            data = yaml.safe_load(file)
            if self.epics_get_flag:
                data = self.epics_get(data)
            return data

    def check_for_offline_motors_and_bl_pvs_before_write(self, dict_: dict):
        """Check for a offline motor before writing, if it is offline, set all values as 0"""
        for motor in dict_["motors"].keys():
            if not dict_["motors"][motor]["up"]:
                dict_["motors"][motor]["value"] = 0
                dict_["motors"][motor]["bounds"][0] = 0
                dict_["motors"][motor]["bounds"][1] = 0

        for bl_pv in dict_["beamline_pvs"].keys():
            if not dict_["beamline_pvs"][bl_pv]["up"]:
                dict_["beamline_pvs"]["value"] = 0

    def write(self, dict_, filepath=DEFAULT):
        """Write data to experiment file and also move motors if needed"""
        if self.epics_put_flag:
            self.epics_put(dict_)
        self.check_for_offline_motors_and_bl_pvs_before_write(dict_)
        with open(filepath, "w") as file:
            yaml.dump(dict_, file)
            file.flush()
