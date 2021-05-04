#!/usr/bin/env python3
"""Library for reading and writing experiment files"""

import atexit
import epics
import yaml

DEFAULT = ".Experiment"
PV_PREFIX = "EMA:B:PB18"
PV_PREFIX = "SOL:S"

PVS = {
"Phi" : PV_PREFIX + ":m1",
"Chi" : PV_PREFIX + ":m2",
"Mu"  : PV_PREFIX + ":m3",
"Nu"  : PV_PREFIX + ":m4",
"Eta" : PV_PREFIX + ":m5",
"Del" : PV_PREFIX + ":m6",
}

MOTORS = {i : epics.Motor(PVS[i]) for i in PVS}


# original values for mu, eta, chi, phi nu and del: 0.0
# original value for bound_Mu: "[-20.0, 160.0]"
# original value for bound_Eta: "[-20.0, 160.0]"
# original value for bound_Chi: "[-5.0, 95.0]"
# original value for bound_Phi: "[-400.0, 400.0]"
# original value for bound_Nu: "[-20.0, 160.0]"
# original value for bound_Del: "[-20.0, 160.0]"
def epics_get(dict_):
    for key in MOTORS:
        dict_[key] = str(MOTORS[key].readback)
        dict_["bound_" + key] = "[{}, {}]".format(MOTORS[key].high_limit, MOTORS[key].low_limit)


def read(filepath=DEFAULT):
    with open(filepath) as file:
        data = yaml.safe_load(file)
        epics_get(data)
        return data


def ret_list(string):
    return [float(i) for i in string.strip("][").split(", ")]


def stop():
    for key in MOTORS:
        MOTORS[key].stop()


def stop():
    for key in MOTORS:
        while not MOTORS[key].done_moving:
            pass


def epics_put(dict_):
    # Make sure we stop all motors.
    atexit.register(stop)
    for key in MOTORS:
        aux = ret_list(dict_["bound_" + key])
        MOTORS[key].low_limit = aux[0]
        MOTORS[key].high_limit = aux[1]
        MOTORS[key].move(dict_[key], confirm_move=True)
    wait()


def write(dict_, filepath=DEFAULT):
    epics_put(dict_)
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)
