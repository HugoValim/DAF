#!/usr/bin/env python3
"""Perform an absolute scan in one of the diffractometer motors"""

import sys
import os
import subprocess
import numpy as np
import dafutilities as du
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
    daf.ascan m 1 10 100 .1
    daf.ascan mu 1 10 100 .1 -o my_scan

    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('motor', metavar='motor', type=str, help='Motor to be used in the scan. Use m/mu, e/eta, c/chi, p/phi, n/nu, d/del')
parser.add_argument('start', metavar='start', type=float, help='Start point')
parser.add_argument('end', metavar='end', type=float, help='End point')
parser.add_argument('step', metavar='step', type=float, help='Number of steps')
parser.add_argument('time', metavar='time', type=float, help='Acquisition time in each point in seconds')
parser.add_argument('-c', '--configuration', type=str, help='choose a counter configuration file', default='default')
parser.add_argument('-o', '--output', help='output data to file output-prefix/<fileprefix>_nnnn')

args = parser.parse_args()
dic = vars(args)

dict_args = du.read()

for j,k in dic.items():
    if j in dict_args and k is not None:
        dict_args[j] = str(k)
du.write(dict_args, is_scan = True)

dict_args = du.read()

if du.PV_PREFIX == "EMA:B:PB18":
    data = {'m':'huber_mu', 'mu':'huber_mu', 'e':'huber_eta', 'eta':'huber_eta', 'c':'huber_chi', 'chi':'huber_chi',
            'p':'huber_phi', 'phi':'huber_phi', 'n':'huber_nu', 'nu':'huber_nu', 'd':'huber_del', 'del':'huber_del'}

else:
    data = {'m':'sol_m3', 'e':'sol_m5', 'c':'sol_m2',
            'p':'sol_m1', 'n':'sol_m4', 'd':'sol_m6'}

args = {'motor' : [data[args.motor]], 'start' : [[args.start]], 'end': [[args.end]], 'step_or_points': [[args.step + 1]], 'time': [[args.time]], 'configuration': dict_args['default_counters'].split('.')[1], 
        'optimum': None, 'repeat': 1, 'sleep': 0, 'message': None, 'output': args.output, 'sync': True, 'snake': False, 'xlabel': data[args.motor], 'prescan': 'ls', 'postscan': 'pwd', 
        'plot_type': PlotType.hdf, 'relative': False, 'reset': False, 'step_mode': False, 'points_mode': True}

class DAFScan(ScanOperationCLI):

    def __init__(self):
        super().__init__(**args)

    def on_operation_end(self):
        """Routine to be done after this scan operation."""
        if self.plot_type == PlotType.pyqtgraph:
            self.pyqtgraph_plot.operation_ends()
        if self.plot_type == PlotType.hdf:
            self.hdf_plot.operation_ends()
        if bool(self.reset):
            print('[scan-utils] Reseting devices positions.')
            self.reset_motors()
scan = DAFScan()
scan.run()

log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
