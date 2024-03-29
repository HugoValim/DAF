#!/usr/bin/env python3

from os import path

import numpy as np
import yaml

from daf.utils.general_configs import VERSION

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
    "kafka_topic": "EMA_bluesky",  # Defines topic used in scans
    "scan_db": "temp",  # Defines DB used in scans
    "version": VERSION,
}


def generate_file(data=default, file_path="", file_name="default"):
    full_file_path = path.join(file_path, file_name)
    with open(full_file_path, "w") as stream:
        yaml.dump(data, stream, allow_unicode=False)
