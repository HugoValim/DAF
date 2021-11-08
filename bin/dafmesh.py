#!/usr/bin/env python3
"""Perform an relative scan in one of the diffractometer motors"""

import sys
import os
import subprocess
import numpy as np
import dafutilities as du
import scan_daf as sd
import yaml
import argparse as ap

# scan-utils imports
from scan_utils.hdf5_writer import HDF5Writer
from scan_utils import cleanup, die
from scan_utils import Configuration, processUserField, get_counters_in_config
from scan_utils.scan_pyqtgraph_plot import PlotScan
from scan_utils.scan_hdf_plot import PlotHDFScan
from scan_utils import PlotType
from scan_utils import WriteType
from scan_utils import DefaultParser
from scan_utils.scan import ScanOperationCLI

epi = '''
Eg:
    daf.rscan m -2 2 100 .1
    daf.rscan mu 2 4 100 .1 -o my_scan

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
parser.add_argument('-cf', '--configuration', type=str, help='choose a counter configuration file', default='default')
parser.add_argument('-o', '--output', help='output data to file output-prefix/<fileprefix>_nnnn')
parser.add_argument('-np', '--no-plot', help='Do not plot de scan', action='store_true')

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()


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

if args.no_plot:
    ptype = PlotType.none
else:
    ptype = PlotType.hdf

args = {'motor' : motors, 'start' : [start], 'end': [end], 'step_or_points': [step], 'time': [[args.time]], 'configuration': dict_args['default_counters'].split('.')[1], 
        'optimum': None, 'repeat': 1, 'sleep': 0, 'message': None, 'output': args.output, 'sync': True, 'snake': False, 'xlabel': data[motor], 'prescan': 'ls', 'postscan': 'pwd', 
        'plot_type': ptype, 're1lative': False, 'reset': False, 'step_mode': False, 'points_mode': True}

scan = sd.DAFScan()
scan.run()

log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
