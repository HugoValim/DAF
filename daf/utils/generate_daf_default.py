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
    "hklnow": [0, 0, 0],
    "reflections": [],
    "Print_marker": "",
    "Print_cmarker": "",
    "Print_space": "",
    "hkl": "",
    "cons_mu": 0.0,
    "cons_eta": 0.0,
    "cons_chi": 0.0,
    "cons_phi": 0.0,
    "cons_nu": 0.0,
    "cons_del": 0.0,
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
            "scan_utils_mnemonic": "sol_m1",
        },
        "eta": {
            "pv": "SOL:S:m2",
            "mnemonic": "Eta",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m2",
        },
        "chi": {
            "pv": "SOL:S:m3",
            "mnemonic": "Chi",
            "value": 0,
            "bounds": [-5.0, 95.0],
            "scan_utils_mnemonic": "sol_m3",
        },
        "phi": {
            "pv": "SOL:S:m4",
            "mnemonic": "Phi",
            "value": 0,
            "bounds": [-400.0, 400.0],
            "scan_utils_mnemonic": "sol_m4",
        },
        "nu": {
            "pv": "SOL:S:m5",
            "mnemonic": "Nu",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m5",
        },
        "del": {
            "pv": "SOL:S:m6",
            "mnemonic": "Del",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m6",
        },
        "sample_z": {  # sz (Sample z - Sample Stage 1 and 2)
            "pv": "SOL:S:m7",
            "mnemonic": "sz",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m7",
        },
        "sample_x": {  # sx (Sample x - Sample Stage 2)
            "pv": "SOL:S:m8",
            "mnemonic": "sx",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m8",
        },
        "sample_rx": {  #  srx (Sample Rx - Sample Stage 2)
            "pv": "SOL:S:m9",
            "mnemonic": "srx",
            "value": 0,
            "bounds": [-5.0, 95.0],
            "scan_utils_mnemonic": "sol_m9",
        },
        "sample_y": {  #  sy (Sample y - Sample Stage 2)
            "pv": "SOL:S:m10",
            "mnemonic": "sy",
            "value": 0,
            "bounds": [-400.0, 400.0],
            "scan_utils_mnemonic": "sol_m10",
        },
        "sample_ry": {  # sry (Sample Ry - Sample Stage 2)
            "pv": "SOL:S:m11",
            "mnemonic": "sry",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m11",
        },
        "sample_x_s1": {  # sx1 (Sample x - Sample Stage 1)
            "pv": "SOL:S:m12",
            "mnemonic": "sx1",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m12",
        },
        "sample_y_s1": {  # sy1 (Sample y - Sample Stage 1)
            "pv": "SOL:S:m13",
            "mnemonic": "sy1",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m13",
        },
        "diffractomer_ux": {  #  diffux (Diffractometer Ux)
            "pv": "SOL:S:m14",
            "mnemonic": "diffux",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m14",
        },
        "diffractomer_uy": {  #  diffuy (Diffractometer Uy)
            "pv": "SOL:S:m15",
            "mnemonic": "diffuy",
            "value": 0,
            "bounds": [-5.0, 95.0],
            "scan_utils_mnemonic": "sol_m15",
        },
        "diffractomer_rx": {  #  diffrx (Diffractometer Rx)
            "pv": "SOL:S:m16",
            "mnemonic": "diffrx",
            "value": 0,
            "bounds": [-400.0, 400.0],
            "scan_utils_mnemonic": "sol_m16",
        },
        "theta_analyzer_crystal": {  #  thca (Theta Crystal An.)
            "pv": "SOL:S:m17",
            "mnemonic": "thca",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m17",
        },
        "2theta_analyzer_crystal": {  #  tthca (2Theta Crystal An.)
            "pv": "SOL:S:m18",
            "mnemonic": "tthca",
            "value": 0,
            "bounds": [-20.0, 160.0],
            "scan_utils_mnemonic": "sol_m18",
        },
    },
    "beamline_pvs": {
        "energy": {
            "pv": "energy_sim",
            "mnemonic": "PV_energy",
            "value": 10000,
            "simulated": True
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
    "simulated": False,  # Defines in DAF will use simulated motors or not
}


def generate_file(data=default, file_path="", file_name="default"):
    full_file_path = path.join(file_path, file_name)
    with open(full_file_path, "w") as stream:
        yaml.dump(data, stream, allow_unicode=False)
