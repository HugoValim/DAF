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
import epics

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
    daf.lup -m -2 2 100 .1
    daf.dscan -m -2 2 100 .1
    daf.dscan -m -2 2 100 .1 -np -o my_file

    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)
parser.add_argument('-m', '--mu', action='store_true',  help='Use Mu motor in the scan')
parser.add_argument('-e', '--eta', action='store_true', help='Use Eta motor in the scan')
parser.add_argument('-c', '--chi', action='store_true', help='Use Chi motor in the scan')
parser.add_argument('-p', '--phi', action='store_true', help='Use Phi motor in the scan')
parser.add_argument('-n', '--nu', action='store_true',  help='Use Nu motor in the scan')
parser.add_argument('-d', '--del', action='store_true', help='Use Del motor in the scan')
parser.add_argument('start', metavar='start', type=float, help='Start point')
parser.add_argument('end', metavar='end', type=float, help='End point')
parser.add_argument('step', metavar='step', type=float, help='Number of steps')
parser.add_argument('time', metavar='time', type=float, help='Acquisition time in each point in seconds')
parser.add_argument('-cf', '--configuration-file', type=str, help='choose a counter configuration file', default='default')
parser.add_argument('-o', '--output', help='output data to file output-prefix/<fileprefix>_nnnn', default='scan_daf')
parser.add_argument('-np', '--no-plot', help='Do not plot de scan', action='store_const', const=PlotType.none, default=PlotType.pyqtgraph)
parser.add_argument('-cw', '--close-window', help='Close the scan window after it is done', default=False, action='store_true')

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

mu_now = dict_args['Mu']
eta_now = dict_args['Eta']
chi_now = dict_args['Chi']
phi_now = dict_args['Phi']
nu_now = dict_args['Nu']
del_now = dict_args['Del']

motor_dict = {'mu':mu_now, 'eta':eta_now, 'chi':chi_now,
              'phi':phi_now, 'nu':nu_now, 'del':del_now}

for key, val in dic.items():
    if val:
        motor = key
        break

start = motor_dict[motor] + args.start
end = motor_dict[motor] + args.end

args = {'motor' : [data[motor]], 'start' : [[start]], 'end': [[end]], 'step_or_points': [[args.step]], 
        'time': [[args.time]], 'configuration': dict_args['default_counters'].split('.')[1], 
        'optimum': None, 'repeat': 1, 'sleep': 0, 'message': None, 'output': args.output, 'sync': True, 
        'snake': False, 'xlabel': data[motor], 'prescan': 'ls', 'postscan': 'pwd', 
        'plot_type': args.no_plot, 'relative': False, 'reset': True, 'step_mode': False, 'points_mode': True}

scan = sd.DAFScan(args, close_window=dic['close_window'])
scan.run()
