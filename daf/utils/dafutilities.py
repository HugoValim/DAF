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
            }
            self.MOTORS = {
                i: epics.Motor(self.MOTOR_PVS[i]) for i in self.MOTOR_PVS.keys()
            }

    @staticmethod
    def only_read(filepath=DEFAULT):
        """Just get the data from .Experiment file without any epics command"""
        with open(filepath) as file:
            data = yaml.safe_load(file)
            return data

    def wait(self):
        for key in self.MOTORS:
            while not self.MOTORS[key].done_moving:
                pass

    def epics_get(self, dict_):
        for key in self.MOTORS:
            dict_["motors"][key]["value"] = self.MOTORS[key].readback
            dict_["motors"][key]["bounds"] = [
                self.MOTORS[key].low_limit,
                self.MOTORS[key].high_limit,
            ]

        for key, value in self.BL_PVS.items():
            dict_["beamline_pvs"][key]["value"] = (
                float(epics.caget(self.BL_PVS[key])) * 1000
            )

        return dict_

    def epics_put(self, dict_):
        # Make sure we stop all motors.
        atexit.register(self.stop)
        for key in self.MOTORS:
            self.MOTORS[key].low_limit = dict_["motors"][key]["bounds"][0]
            self.MOTORS[key].high_limit = dict_["motors"][key]["bounds"][1]
            self.MOTORS[key].move(
                dict_["motors"][key]["value"], ignore_limits=True, confirm_move=True
            )
        self.wait()

    def stop(self):
        for key in self.MOTORS:
            self.MOTORS[key].stop()

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
