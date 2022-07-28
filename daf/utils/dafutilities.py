#!/usr/bin/env python3
"""Library for reading and writing experiment files"""

import atexit
import sys
import os
from os import path
import epics
import yaml
import time
import numpy as np
import signal
import time

import daf.utils.generate_daf_default as gf
from daf.utils.daf_paths import HOME

DEFAULT = ".Experiment"


def only_read(filepath=DEFAULT):
    """Just get the data from .Experiment file without any epics command"""
    with open(filepath) as file:
        data = yaml.safe_load(file)
        return data


try:
    dict_now = only_read()
    flag = dict_now["simulated"]
except FileNotFoundError:
    flag = True

if not flag:
    PV_PREFIX = "EMA:B:PB18"
    BL_PVS = {"PV_energy": "EMA:A:DCM01:GonRxEnergy_RBV"}
else:
    PV_PREFIX = "SOL:S"
    BL_PVS = {"PV_energy": "SOL:S:m7"}
    # PV_PREFIX = "IOC"
try:
    PVS = {
        "Phi": PV_PREFIX + ":m1",
        "Chi": PV_PREFIX + ":m2",
        "Mu": PV_PREFIX + ":m3",
        "Nu": PV_PREFIX + ":m4",
        "Eta": PV_PREFIX + ":m5",
        "Del": PV_PREFIX + ":m6",
    }
    MOTORS = {i: epics.Motor(PVS[i]) for i in PVS}
except epics.motor.MotorException:
    PV_PREFIX = "SOL:S"
    BL_PVS = {"PV_energy": "SOL:S:m7"}
    PVS = {
        "Phi": PV_PREFIX + ":m1",
        "Chi": PV_PREFIX + ":m2",
        "Mu": PV_PREFIX + ":m3",
        "Nu": PV_PREFIX + ":m4",
        "Eta": PV_PREFIX + ":m5",
        "Del": PV_PREFIX + ":m6",
    }
    MOTORS = {i: epics.Motor(PVS[i]) for i in PVS}


def sigint_handler_utilities(signum, frame):
    """Function to handle ctrl + c and avoid breaking daf's .Experiment file"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    dict_args = read()
    write(dict_args)
    print("\n")
    exit(1)


signal.signal(signal.SIGINT, sigint_handler_utilities)


class DevNull:
    """Supress errors for the user"""

    def write(self, msg):
        pass


# sys.stderr = DevNull()


def wait():
    for key in MOTORS:
        while not MOTORS[key].done_moving:
            pass


def epics_get(dict_):
    for key in MOTORS:
        dict_[key] = MOTORS[key].readback
        dict_["bound_" + key] = [MOTORS[key].low_limit, MOTORS[key].high_limit]

    for key, value in BL_PVS.items():
        dict_[key] = float(epics.caget(BL_PVS[key])) * 1000

    return dict_


def read(filepath=DEFAULT):
    with open(filepath) as file:
        data = yaml.safe_load(file)
        data_w_caget = epics_get(data)
        return data_w_caget


def stop():
    for key in MOTORS:
        MOTORS[key].stop()


def epics_put(dict_):
    # Make sure we stop all motors.
    atexit.register(stop)
    for key in MOTORS:
        aux = dict_["bound_" + key]
        MOTORS[key].low_limit = aux[0]
        MOTORS[key].high_limit = aux[1]
        MOTORS[key].move(dict_[key], ignore_limits=True, confirm_move=True)
    wait()


def write(dict_, filepath=DEFAULT):
    epics_put(dict_)
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)
        file.flush()
