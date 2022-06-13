#!/usr/bin/env python3
"""Perform an infinite time scan for the configured counters, i should be stopped with Ctrl+c"""

import sys
import os
import subprocess

import numpy as np
import yaml
import argparse as ap

from scan_utils import PlotType

import dafutilities as du
import timescan_daf as td

epi = """
Eg:
    daf.tscan .1
    daf.tscan .1 -d 1

    """

parser = ap.ArgumentParser(
    formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi
)

parser.add_argument(
    "time", metavar="time", type=float, help="Acquisition time in each point in seconds"
)
parser.add_argument(
    "-d",
    "--delay",
    metavar="delay",
    type=float,
    help="Delay between each point in seconds",
    default=0,
)
parser.add_argument(
    "-cf",
    "--configuration",
    type=str,
    help="choose a counter configuration file",
    default="default",
)
parser.add_argument(
    "-o",
    "--output",
    help="output data to file output-prefix/<fileprefix>_nnnn",
    default=os.getcwd() + "/scan_daf",
)
parser.add_argument(
    "-sp",
    "--show-plot",
    help="Do not plot de scan",
    action="store_const",
    const=PlotType.hdf,
    default=PlotType.none,
)
parser.add_argument(
    "-cw",
    "--close-window",
    help="Close the scan window after it is done",
    default=False,
    action="store_true",
)

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()
du.log_macro(dict_args)

args = {
    "configuration": dict_args["default_counters"].split(".")[1],
    "optimum": None,
    "repeat": 1,
    "sleep": 0,
    "message": None,
    "output": args.output,
    "sync": True,
    "snake": False,
    "motor": None,
    "xlabel": "points",
    "prescan": "ls",
    "postscan": "pwd",
    "plot_type": args.show_plot,
    "relative": False,
    "reset": False,
    "step_mode": False,
    "points_mode": False,
    "start": None,
    "end": None,
    "step_or_points": None,
    "time": [[args.time]],
    "filename": None,
}

scan = td.DAFTimeScan(args, close_window=dic["close_window"], delay=dic["delay"])
scan.run()
