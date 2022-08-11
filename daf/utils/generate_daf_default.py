#!/usr/bin/env python3

from os import path

import numpy as np
import yaml


default = {
    "Mode": "2052",
    "Material": "Si",
    "IDir": [0, 1, 0],
    "IDir_print": [0, 1, 0],
    "NDir": [0, 0, 1],
    "NDir_print": [0, 0, 1],
    "RDir": [0, 0, 1],
    "Sampleor": "z+",
    "energy_offset": 0.0,
    # "bound_Mu": [-20.0, 160.0],
    # "bound_Eta": [-20.0, 160.0],
    # "bound_Chi": [-5.0, 95.0],
    # "bound_Phi": [-400.0, 400.0],
    # "bound_Nu": [-20.0, 160.0],
    # "bound_Del": [-20.0, 160.0],
    "hklnow": [0, 0, 0],
    "reflections": [],
    "Print_marker": "",
    "Print_cmarker": "",
    "Print_space": "",
    "hkl": "",
    "cons_Mu": 0.0,
    "cons_Eta": 0.0,
    "cons_Chi": 0.0,
    "cons_Phi": 0.0,
    "cons_Nu": 0.0,
    "cons_Del": 0.0,
    "cons_alpha": 0.0,
    "cons_beta": 0.0,
    "cons_psi": 0.0,
    "cons_omega": 0.0,
    "cons_qaz": 0.0,
    "cons_naz": 0.0,
    "motors": {
        "mu": {
            "pv": "SOL:S:m1",
            "mnemonic": "Mu",
            "value": 0,
            "bounds": [-20.0, 160.0],
        },
        "eta": {
            "pv": "SOL:S:m2",
            "mnemonic": "Eta",
            "value": 0,
            "bounds": [-20.0, 160.0],
        },
        "chi": {
            "pv": "SOL:S:m3",
            "mnemonic": "Chi",
            "value": 0,
            "bounds": [-5.0, 95.0],
        },
        "phi": {
            "pv": "SOL:S:m4",
            "mnemonic": "Phi",
            "value": 0,
            "bounds": [-400.0, 400.0],
        },
        "nu": {
            "pv": "SOL:S:m5",
            "mnemonic": "Nu",
            "value": 0,
            "bounds": [-20.0, 160.0],
        },
        "del": {
            "pv": "SOL:S:m6",
            "mnemonic": "Del",
            "value": 0,
            "bounds": [-20.0, 160.0],
        },
    },
    # "sample_z_pv": {"pv": "SOL:S:m7", "mnemonic": "sz"},  # sz (Sample z - Sample Stage 1 and 2)
    # "sample_x_pv": {"pv": "SOL:S:m8", "mnemonic": "sx"},  # sx (Sample x - Sample Stage 2)
    # "sample_rx_pv": {"pv": "SOL:S:m9", "mnemonic": "srx"},  #  srx (Sample Rx - Sample Stage 2)
    # "sample_y_pv": {"pv": "SOL:S:m10", "mnemonic": "sy"},  #  sy (Sample y - Sample Stage 2)
    # "sample_ry_pv": {"pv": "SOL:S:m11", "mnemonic": "sry"},  # sry (Sample Ry - Sample Stage 2)
    # "sample_x_s1_pv": {"pv": "SOL:S:m12", "mnemonic": "sx1"}, # sx1 (Sample x - Sample Stage 1)
    # "sample_y_s1_pv": {"pv": "SOL:S:m13", "mnemonic": "sy1"}, # sy1 (Sample y - Sample Stage 1)
    # "diffractomer_ux_pv": {"pv": "SOL:S:m14", "mnemonic": "diffux"},  #  diffux (Diffractometer Ux)
    # "diffractomer_uy_pv": {"pv": "SOL:S:m15", "mnemonic": "diffuy"},  #  diffuy (Diffractometer Uy)
    # "diffractomer_rx_pv": {"pv": "SOL:S:m16", "mnemonic": "diffrx"},  #  diffrx (Diffractometer Rx)
    # "theta_analyzer_crystal_pv": {"pv": "SOL:S:m17", "mnemonic": "thca"},  #  thca (Theta Crystal An.)
    # "2theta_analyzer_crystal_pv": {"pv": "SOL:S:m18", "mnemonic": "tthca"},  #  tthca (2Theta Crystal An.)
    "beamline_pvs": {
        "energy": {
            "pv": "SOL:S:m24",
            "mnemonic": "PV_energy",
            "value": 0,
        },  #  bl_energy_pv
    },
    "twotheta": 0.0,
    "theta": 0.0,
    "alpha": 0.0,
    "qaz": 90.0,
    "naz": 0.0,
    "tau": 0.0,
    "psi": 0.0,
    "beta": 0.0,
    "omega": 0.0,
    "U_mat": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
    "UB_mat": [
        [1.15690279e00, 0.0, 0.0],
        [0.0, 1.15690279e00, 0.0],
        [0.0, 0.0, 1.15690279e00],
    ],
    "lparam_a": 0.0,
    "lparam_b": 0.0,
    "lparam_c": 0.0,
    "lparam_alpha": 0.0,
    "lparam_beta": 0.0,
    "lparam_gama": 0.0,
    "Max_diff": 0.1,
    "scan_name": "scan_test",
    "separator": ",",
    "macro_flag": False,
    "macro_file": "macro",
    "setup": "default",
    "user_samples": {},
    "setup_desc": "This is DAF default setup",
    "default_counters": "config.daf_default.yml",
    "dark_mode": 0,
    "scan_stats": {},
    "PV_energy": 0.0,
    "scan_running": False,  # Flag to tell daf.live if a scan is running
    "scan_counters": [],  # Inform the counter for daf.live
    "current_scan_file": "",  # Tells daf.live which file to look after to plot the current scan
    "main_scan_counter": None,  # Defines the counter main counter to use in daf.live
    "main_scan_motor": "",  # Defines the xlabel motor for daf.live
    "simulated": True,  # Defines in DAF will use simulated motors or not
}


def generate_file(data=default, file_path="", file_name="default"):
    full_file_path = path.join(file_path, file_name)
    with open(full_file_path, "w") as stream:
        yaml.dump(data, stream, allow_unicode=False)
