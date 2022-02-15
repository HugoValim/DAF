#!/usr/bin/env python3
"""Perform a mesh scan using two of the diffractometer motors"""

import sys
import os
import subprocess

import numpy as np
import yaml
import argparse as ap

# scan-utils imports
# from scan_utils.hdf5_writer import HDF5Writer
# from scan_utils import cleanup, die
# from scan_utils import Configuration, processUserField, get_counters_in_config
# from scan_utils.scan_pyqtgraph_plot import PlotScan
# from scan_utils.scan_hdf_plot import PlotHDFScan
from scan_utils import PlotType
# from scan_utils import WriteType
# from scan_utils import DefaultParser
# from scan_utils.scan import ScanOperationCLI

import dafutilities as du
import scan_daf as sd

epi = '''
Eg:
    daf.mesh -e -2 2 -d -2 6 100 .1
    daf.mesh -e -2 2 -d -2 6 100 .1 -np

    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)
parser.add_argument('-m', '--mu', metavar='ang', type=float, nargs=2, help='Start and end for Mu')
parser.add_argument('-e', '--eta', metavar='ang', type=float, nargs=2, help='Start and end for Eta')
parser.add_argument('-c', '--chi', metavar='ang', type=float, nargs=2, help='Start and end for Chi')
parser.add_argument('-p', '--phi', metavar='ang', type=float, nargs=2, help='Start and end for Phi')
parser.add_argument('-n', '--nu', metavar='ang', type=float, nargs=2, help='Start and end for Nu')
parser.add_argument('-d', '--del', metavar='ang', type=float, nargs=2, help='Start and end for Del')
parser.add_argument('step', metavar='step', type=int, help='Number of steps')
parser.add_argument('time', metavar='time', type=float, help='Acquisition time in each point in seconds')
parser.add_argument('-x', '--xlabel', help='motor which position is shown in x axis (if not set, point index is shown instead)', default='points')
parser.add_argument('-cf', '--configuration', type=str, help='choose a counter configuration file', default='default')
parser.add_argument('-o', '--output', help='output data to file output-prefix/<fileprefix>_nnnn', default=os.getcwd() + '/scan_daf')
parser.add_argument('-sp', '--show-plot', help='Do not plot de scan', action='store_const', const=PlotType.hdf, default=PlotType.none)
parser.add_argument('-cw', '--close-window', help='Close the scan window after it is done', default=False, action='store_true')

"""
BUG FOR STATS CALCULATIONS, BECAUSE IT EXPECTS A 1D VECTOR

"""

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()
du.log_macro(dict_args)

if du.PV_PREFIX == "EMA:B:PB18":
    data = {'mu':'huber_mu', 'eta':'huber_eta', 'chi':'huber_chi',
            'phi':'huber_phi', 'nu':'huber_nu', 'del':'huber_del'}

else:
    data = {'mu':'sol_m3', 'eta':'sol_m5', 'chi':'sol_m2',
            'phi':'sol_m1', 'nu':'sol_m4', 'del':'sol_m6'}

n = 0
motors = []
start = []
end = []
step = []
for key, val in dic.items():
    if isinstance(val, list):
        motor = key
        motors.append(data[motor])
        start.append(val[0])
        end.append(val[1])
        step.append(args.step)
        n += 1
    if n == 2:
        break

if args.xlabel != 'points':
    xlabel = data[args.xlabel]
else:
    xlabel = 'points'

args = {'motor' : motors, 'start' : [start], 'end': [end], 'step_or_points': [step], 'time': [[args.time]], 
        'configuration': dict_args['default_counters'].split('.')[1], 'optimum': None, 'repeat': 1, 'sleep': 0, 
        'message': None, 'output': args.output, 'sync': True, 'snake': False, 'xlabel': xlabel, 'prescan': 'ls', 
        'postscan': 'pwd', 'plot_type': args.show_plot, 'relative': False, 'reset': False, 'step_mode': False, 'points_mode': True}

scan = sd.DAFScan(args, close_window=dic['close_window'])
scan.run()
