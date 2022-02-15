#!/usr/bin/env python3

import os
import subprocess

subprocess.Popen("pydm --hide-nav-bar ../gui/live_view.py", 
                # stdout=subprocess.PIPE, 
                # stderr=subprocess.PIPE,
                # stdin=subprocess.PIPE,
                shell = True)
