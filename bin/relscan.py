#!/usr/bin/env python3
"""Perform an relative scan in one of the diffractometer motors"""

import sys
import os
import subprocess
import numpy as np
import dafutilities as du
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
    daf.rscan m -2 2 100 .1
    daf.rscan mu 2 4 100 .1 -o my_scan

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

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()

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

args = {'motor' : [data[motor]], 'start' : [[start]], 'end': [[end]], 'step_or_points': [[args.step]], 'time': [[args.time]], 'configuration': dict_args['default_counters'].split('.')[1], 
        'optimum': None, 'repeat': 1, 'sleep': 0, 'message': None, 'output': args.output, 'sync': True, 'snake': False, 'xlabel': data[motor], 'prescan': 'ls', 'postscan': 'pwd', 
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

        m = epics.Motor(du.PVS[motor.capitalize()])
        m.move(motor_dict[motor])

scan = DAFScan()
scan.run()



log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
