#!/usr/bin/env python3
"""Library for reading and writing experiment files"""

import atexit
import os
import epics
import yaml
import time
import numpy as np

HOME = os.getenv("HOME")
DEFAULT = ".Experiment"
PV_PREFIX = "EMA:B:PB18"
# PV_PREFIX = "SOL:S"
# PV_PREFIX = "IOC"


PVS = {
        "Phi" : PV_PREFIX + ":m1",
        "Chi" : PV_PREFIX + ":m2",
        "Mu"  : PV_PREFIX + ":m3",
        "Nu"  : PV_PREFIX + ":m4",
        "Eta" : PV_PREFIX + ":m5",
        "Del" : PV_PREFIX + ":m6",
}

BL_PVS = {

    'PV_energy' : 'EMA:A:DCM01:GonRxEnergy_RBV',
    'Energy' : 'EMA:A:DCM01:GonRxEnergy_RBV'
}

MOTORS = {i : epics.Motor(PVS[i]) for i in PVS}


def epics_get(dict_):
    for key in MOTORS:
        dict_[key] = MOTORS[key].readback
        dict_["bound_" + key] = [MOTORS[key].low_limit, MOTORS[key].high_limit]

    for key, value in BL_PVS.items():
        dict_[key] = float(epics.caget(BL_PVS[key]))*1000


def read(filepath=DEFAULT):
    with open(filepath) as file:
        data = yaml.safe_load(file)
        epics_get(data)
        write(data)
        return data





def stop():
    for key in MOTORS:
        MOTORS[key].stop()


def wait(is_scan):
    # if not is_scan:
        # print("   PHI       CHI       MU       NU      ETA       DEL")
    lb = lambda x: "{:.5f}".format(float(x))


    for key in MOTORS:
        while not MOTORS[key].done_moving:
            pass
            
            # print_motors = str(lb(MOTORS["Phi"].RBV)) + '  ' + str(lb(MOTORS["Chi"].RBV)) + '  ' + str(lb(MOTORS["Mu"].RBV)) + '  ' + str(lb(MOTORS["Nu"].RBV)) + '  ' + str(lb(MOTORS["Eta"].RBV)) + '  ' + str(lb(MOTORS["Del"].RBV)) + '  '
                
            # print(print_motors)
            # time.sleep(0.5)
    # print('')


def epics_put(dict_, is_scan):
    # Make sure we stop all motors.
    atexit.register(stop)
    for key in MOTORS:
        aux = dict_["bound_" + key]
        MOTORS[key].low_limit = aux[0]
        MOTORS[key].high_limit = aux[1]
        MOTORS[key].move(dict_[key], ignore_limits=True, confirm_move=True)
    wait(is_scan)


def write(dict_, filepath=DEFAULT, is_scan = False):
    epics_put(dict_, is_scan)
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)
