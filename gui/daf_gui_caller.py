#!/usr/bin/env python3

import subprocess

subprocess.Popen(
    "pydm --hide-nav-bar ../gui/daf_gui.py",
    # stdout=subprocess.PIPE,
    # stderr=subprocess.PIPE,
    # stdin=subprocess.PIPE,
    shell=True,
)
