#!/usr/bin/env python3
"""Library for reading and writing experiment files"""

import atexit
import sys
import os
import epics
import yaml
import time
import numpy as np
import signal

def sigint_handler_utilities(signum, frame):
    """Function to handle ctrl + c and avoid breaking daf's .Experiment file"""
    dict_args = read()
    write(dict_args)
    print('\n')
    exit(1)


signal.signal(signal.SIGINT, sigint_handler_utilities)

class DevNull:
    """Supress errors for the user"""
    def write(self, msg):
        pass
# sys.stderr = DevNull()

HOME = os.getenv("HOME")
DEFAULT = ".Experiment"

def only_read(filepath=DEFAULT):
    """Just get the data from .Experiment file without any epics command"""
    with open(filepath) as file:
        data = yaml.safe_load(file)
        return data
dict_ = only_read()

if not dict_['simulated']:
    PV_PREFIX = "EMA:B:PB18"
else:
    PV_PREFIX = "SOL:S"
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

    # 'PV_energy' : 'EMA:A:DCM01:GonRxEnergy_RBV'
    'PV_energy' : 'SOL:S:m7'
}

MOTORS = {i : epics.Motor(PVS[i]) for i in PVS}

def log_macro(dargs):
    """Function to generate the log and macro files"""
    log = sys.argv.pop(0).split('command_line/')[1]
    for i in sys.argv:
        log += ' ' + i
    os.system("echo {} >> Log".format(log))
    if dargs['macro_flag'] == 'True':
        os.system("echo {} >> {}".format(log, dict_args['macro_file']))

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
        # write(data)
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
