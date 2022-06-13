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
    BL_PVS = { 'PV_energy' : 'EMA:A:DCM01:GonRxEnergy_RBV'}
else:
    PV_PREFIX = "SOL:S"
    BL_PVS = { 'PV_energy' : 'SOL:S:m7'}
    # PV_PREFIX = "IOC"

PVS = {
        "Phi" : PV_PREFIX + ":m1",
        "Chi" : PV_PREFIX + ":m2",
        "Mu"  : PV_PREFIX + ":m3",
        "Nu"  : PV_PREFIX + ":m4",
        "Eta" : PV_PREFIX + ":m5",
        "Del" : PV_PREFIX + ":m6",
}
MOTORS = {i : epics.Motor(PVS[i]) for i in PVS}



def sigint_handler_utilities(signum, frame):
    """Function to handle ctrl + c and avoid breaking daf's .Experiment file"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    dict_args = read()
    write(dict_args)
    print('\n')
    exit(1)

signal.signal(signal.SIGINT, sigint_handler_utilities)

def get_passed_motor_order(sysargv):
    """Function to pass the order that use choose to the scan_utils routine"""
    all_possibilities = ['-m', '-e', '-c', '-p', '-n', '-d', '--mu', 
                        '--eta', '--chi', '--phi', '--nu', '--del']
    
    if PV_PREFIX == "EMA:B:PB18":
        data = {'mu':'huber_mu', 'eta':'huber_eta', 'chi':'huber_chi',
            'phi':'huber_phi', 'nu':'huber_nu', 'del':'huber_del'}
    else:
        data = {'mu':'sol_m3', 'eta':'sol_m5', 'chi':'sol_m2',
                'phi':'sol_m1', 'nu':'sol_m4', 'del':'sol_m6'}

    simp_to_comp = {'mu':'mu', 'eta':'eta', 'chi':'chi',
                    'phi':'phi', 'nu':'nu', 'del':'del',
                    'm':'mu', 'e':'eta', 'c':'chi',
                    'p':'phi', 'n':'nu', 'd':'del'}

    motor_order = [data[simp_to_comp[i.split('-')[-1]]] for i in sysargv if i in all_possibilities]

    return motor_order

class DevNull:
    """Supress errors for the user"""
    def write(self, msg):
        pass
# sys.stderr = DevNull()

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
        return data

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


def write(dict_, filepath=DEFAULT):
    epics_put(dict_)
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)
        file.flush()
