#!/usr/bin/env python3
"""Library for reading and writing experiment files"""

import atexit
import os

import epics
import yaml


DEFAULT = ".Experiment"


class DAFIO:
    def __init__(self, read=True):
        if read:
            self.build_epics_pvs()

    def build_epics_pvs(self):
        if os.path.isfile(DEFAULT):
            dict_now = self.only_read()
            self.MOTOR_PVS = {
                key: dict_now["motors"][key]["pv"]
                for key, value in dict_now["motors"].items()
            }
            self.BL_PVS = {
                key: dict_now["beamline_pvs"][key]["pv"]
                for key, value in dict_now["beamline_pvs"].items()
                if dict_now["beamline_pvs"][key]["simulated"] == False
            }
            self.motor_pv_list = [pv for pv in self.MOTOR_PVS.values()]
            self.rbv_motor_pv_list = [pv + ".RBV" for pv in self.MOTOR_PVS.values()]
            self.llm_motor_pv_list = [pv + ".LLM" for pv in self.MOTOR_PVS.values()]
            self.hlm_motor_pv_list = [pv + ".HLM" for pv in self.MOTOR_PVS.values()]
            self.bl_pv_list = [pv for pv in self.BL_PVS.values()]

    @staticmethod
    def only_read(filepath=DEFAULT):
        """Just get the data from .Experiment file without any epics command"""
        with open(filepath) as file:
            data = yaml.safe_load(file)
            return data

    def wait(self):
        for motor in self.motor_pv_list:
            while epics.caget(motor + ".MOVN"):
                pass

    def epics_get(self, dict_):

        updated_rbv_motor_pv_list = epics.caget_many(self.rbv_motor_pv_list)
        updated_llm_motor_pv_list = epics.caget_many(self.llm_motor_pv_list)
        updated_hlm_motor_pv_list = epics.caget_many(self.hlm_motor_pv_list)
        updated_bl_pv_list = epics.caget_many(self.bl_pv_list)

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
            dict_["beamline_pvs"][key]["value"] = updated_bl_pv_list[bl_counter] * 1000
            bl_counter += 1

        return dict_

    def epics_put(self, dict_):
        set_motor_pv_list = [
            dict_["motors"][key]["value"] for key in dict_["motors"].keys()
        ]
        epics.caput_many(self.motor_pv_list, set_motor_pv_list)
        set_llm_motor_pv_list = [
            dict_["motors"][key]["bounds"][0] for key in dict_["motors"].keys()
        ]
        epics.caput_many(self.llm_motor_pv_list, set_llm_motor_pv_list)
        set_hlm_motor_pv_list = [
            dict_["motors"][key]["bounds"][1] for key in dict_["motors"].keys()
        ]
        epics.caput_many(self.hlm_motor_pv_list, set_hlm_motor_pv_list)
        self.wait()

    def read(self, filepath=DEFAULT):
        with open(filepath) as file:
            data = yaml.safe_load(file)
            data_w_caget = self.epics_get(data)
            return data_w_caget

    def write(self, dict_, filepath=DEFAULT):
        self.epics_put(dict_)
        with open(filepath, "w") as file:
            yaml.dump(dict_, file)
            file.flush()
