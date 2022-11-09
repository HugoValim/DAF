motors = {
    "mu": {
        "pv": "EMA:B:PB18:m3",
        "mnemonic": "Mu",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_mu",
    },
    "eta": {
        "pv": "EMA:B:PB18:m5",
        "mnemonic": "Eta",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_eta",
    },
    "chi": {
        "pv": "EMA:B:PB18:m2",
        "mnemonic": "Chi",
        "value": 0,
        "bounds": [-5.0, 95.0],
        "scan_utils_mnemonic": "huber_chi",
    },
    "phi": {
        "pv": "EMA:B:PB18:m1",
        "mnemonic": "Phi",
        "value": 0,
        "bounds": [-400.0, 400.0],
        "scan_utils_mnemonic": "huber_phi",
    },
    "nu": {
        "pv": "EMA:B:PB18:m4",
        "mnemonic": "Nu",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_nu",
    },
    "del": {
        "pv": "EMA:B:PB18:m6",
        "mnemonic": "Del",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_del",
    },
    "sample_z": {  # sz (Sample z - Sample Stage 1 and 2)
        "pv": "EMA:B:PB17:m5",
        "mnemonic": "sz",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_sample_Uy",
    },
    "sample_x": {  # sx (Sample x - Sample Stage 2)
        "pv": "EMA:B:PB17:m14",
        "mnemonic": "sx",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_sample_Ux",
    },
    "sample_rx": {  #  srx (Sample Rx - Sample Stage 2)
        "pv": "EMA:B:PB17:m17",
        "mnemonic": "srx",
        "value": 0,
        "bounds": [-5.0, 95.0],
        "scan_utils_mnemonic": "huber_sample_Rx",
    },
    "sample_y": {  #  sy (Sample y - Sample Stage 2)
        "pv": "EMA:B:PB17:m6",
        "mnemonic": "sy",
        "value": 0,
        "bounds": [-400.0, 400.0],
        "scan_utils_mnemonic": "huber_sample_Uz",
    },
    "sample_ry": {  # sry (Sample Ry - Sample Stage 2)
        "pv": "EMA:B:PB17:m8",
        "mnemonic": "sry",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_sample_Rz",
    },
    "sample_x_s1": {  # sx1 (Sample x - Sample Stage 1)
        "pv": "EMA:B:PB17:m4",
        "mnemonic": "sx1",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "sol_m12",
    },
    "sample_y_s1": {  # sy1 (Sample y - Sample Stage 1)
        "pv": "EMA:B:PB17:m7",
        "mnemonic": "sy1",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_s1_Uz",
    },
    "diffractomer_ux": {  #  diffux (Diffractometer Ux)
        "pv": "EMA:B:PB17:m3",
        "mnemonic": "diffux",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "huber_base_Ux",
    },
    "diffractomer_uy": {  #  diffuy (Diffractometer Uy)
        "pv": "EMA:B:PB17:CS1:m1",
        "mnemonic": "diffuy",
        "value": 0,
        "bounds": [-5.0, 95.0],
        "scan_utils_mnemonic": "sol_m15",
    },
    "diffractomer_rx": {  #  diffrx (Diffractometer Rx)
        "pv": "EMA:B:PB17:CS1:m8",
        "mnemonic": "diffrx",
        "value": 0,
        "bounds": [-400.0, 400.0],
        "scan_utils_mnemonic": "sol_m16",
    },
    "theta_analyzer_crystal": {  #  thca (Theta Crystal An.)
        "pv": "EMA:B:PB18:m7",
        "mnemonic": "thca",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "sol_m17",
    },
    "2theta_analyzer_crystal": {  #  tthca (2Theta Crystal An.)
        "pv": "EMA:B:PB18:m8",
        "mnemonic": "tthca",
        "value": 0,
        "bounds": [-20.0, 160.0],
        "scan_utils_mnemonic": "sol_m18",
    },
}