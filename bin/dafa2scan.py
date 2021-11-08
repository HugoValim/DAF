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
    daf.a2scan -d 1 10 -e 1 20  100 .1
    daf.a2scan -d 1 10 -e 1 20  100 .1 -o my_scan

    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)


parser.add_argument('-m', '--mu', metavar='ang', type=float, nargs=2, help='Start and end for Mu')
parser.add_argument('-e', '--eta', metavar='ang', type=float, nargs=2, help='Start and end for Eta')
parser.add_argument('-c', '--chi', metavar='ang', type=float, nargs=2, help='Start and end for Chi')
parser.add_argument('-p', '--phi', metavar='ang', type=float, nargs=2, help='Start and end for Phi')
parser.add_argument('-n', '--nu', metavar='ang', type=float, nargs=2, help='Start and end for Nu')
parser.add_argument('-d', '--del', metavar='ang', type=float, nargs=2, help='Start and end for Del')
parser.add_argument('step', metavar='step', type=int, help='Number of steps')
parser.add_argument('time', metavar='time', type=float, help='Acquisition time in each point in seconds', default=0.1)
parser.add_argument('-cf', '--configuration', type=str, help='choose a counter configuration file', default='default')
parser.add_argument('-o', '--output', help='output data to file output-prefix/<fileprefix>_nnnn', default='scan_daf')
parser.add_argument('-x', '--xlabel', help='motor which position is shown in x axis (if not set, point index is shown instead)', default='points')
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
data_for_scan = {}
for key, val in dic.items():
    if isinstance(val, list):
        motor = key
        motors.append(data[motor])
        points = np.linspace(val[0], val[1], args.step + 1)
        points = [float(i) for i in points]
        data_for_scan[data[motor]] = points
        n += 1
    if n == 2:
        break

with open('.points.yaml', 'w') as stream:
    yaml.dump(data_for_scan, stream, allow_unicode=False)

if args.no_plot:
    ptype = PlotType.none
else:
    ptype = PlotType.hdf

args = {'configuration': dict_args['default_counters'].split('.')[1], 'optimum': None, 'repeat': 1, 'sleep': 0, 'message': None, 
'output': args.output, 'sync': True, 'snake': False, 'motor': motors, 'xlabel': args.xlabel, 
'prescan': 'ls', 'postscan': 'pwd', 'plot_type': ptype, 'relative': False, 'reset': False, 'step_mode': False, 
'points_mode': False, 'start': None, 'end': None, 'step_or_points': None, 'time': [[args.time]], 'filename': '.points.yaml'}

scan = sd.DAFScan(args)
scan.run()

log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
