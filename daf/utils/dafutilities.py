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


if os.path.isfile(DEFAULT):
    dict_now = only_read()
    MOTOR_PVS = {key: dict_now[key]["pv"] for key, value in dict_now.items() if key.startswith("motor_")}
    BL_PVS = {key: dict_now[key]["pv"] for key, value in dict_now.items() if key.startswith("bl_")}
    MOTORS = {i: epics.Motor(MOTOR_PVS[i]) for i in MOTOR_PVS.keys()}

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
        dict_[key]["value"] = MOTORS[key].readback
        dict_[key]["bounds"] = [MOTORS[key].low_limit, MOTORS[key].high_limit]

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
        MOTORS[key].low_limit = dict_[key]["bounds"][0]
        MOTORS[key].high_limit = dict_[key]["bounds"][1]
        MOTORS[key].move(dict_[key]["value"], ignore_limits=True, confirm_move=True)
    wait()


def write(dict_, filepath=DEFAULT):
    print(dict_)
    epics_put(dict_)
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)
        file.flush()
