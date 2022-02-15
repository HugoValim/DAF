#!/usr/bin/env python3
"""Perform a scan using HKL coordinates"""

import argparse as ap
import sys
import os

import numpy as np
import pandas as pd
import yaml

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

import daf
import dafutilities as du
import scan_daf as sd

epi = '''
Eg: 
    daf.scan 1 1 1 1.1 1.1 1.1 100 -n my_scan
    daf.scan 1 1 1 1.1 1.1 1.1 1000 -n my_scan -sep \; -v
    daf.scan 1 1 1 1.1 1.1 1.1 100 -p -t 0.5
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('hkli', metavar=('Hi, Ki, Li'), type=float, nargs=3, help='Initial HKL for scan')
parser.add_argument('hklf', metavar=('Hf, Kf, Lf'), type=float, nargs=3, help='Final HKL for scan')
parser.add_argument('points', metavar='points', type=float, help='Number of points for the scan')
parser.add_argument('time', metavar='time', type=float, help='Acquisition time in each point in seconds.')
parser.add_argument('-n', '--scan_name', metavar='', type=str, default='daf_hkl_scan.csv', help='Name of the scan')
parser.add_argument('-s', '--step', metavar='', type=float, help='Step for the scan')
parser.add_argument('-sep', '--separator', metavar='', type=str, default = ',', help='Chose the separator of scan file, comma is default')
parser.add_argument('-m', '--max_diff', metavar='', type=float, default = 0,
                    help='Max difference of angles variation (default is 0.1), if 0 is given no verification will be done')
parser.add_argument('-v', '--verbose', action='store_true', help='Show full output')
parser.add_argument('-g', '--gui', action='store_true', help='Flag to tell if gui is calling this function')
parser.add_argument('-c', '--calc', action='store_true', help='Only calc the scan without perform it')
parser.add_argument('-x', '--xlabel', help='motor which position is shown in x axis (if not set, point index is shown instead)', default='points')
parser.add_argument('-o', '--output', help='output data to file output-prefix/<fileprefix>_nnnn', default=os.getcwd() + '/scan_daf')
parser.add_argument('-sp', '--show-plot', help='Do not plot de scan', action='store_const', const=PlotType.hdf, default=PlotType.none)
parser.add_argument('-cw', '--close-window', help='Close the scan window after it is done', default=False, action='store_true')

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()
du.log_macro(dict_args)

U = np.array(dict_args['U_mat'])
mode = [int(i) for i in dict_args['Mode']]
idir = dict_args['IDir']
ndir = dict_args['NDir']
rdir = dict_args['RDir']
Mu_bound = dict_args['bound_Mu']
Eta_bound = dict_args['bound_Eta']
Chi_bound = dict_args['bound_Chi']
Phi_bound = dict_args['bound_Phi']
Nu_bound = dict_args['bound_Nu']
Del_bound = dict_args['bound_Del']

exp = daf.Control(*mode)
if dict_args['Material'] in dict_args['user_samples'].keys():
    exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

else: 
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], 
                    dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], 
                    dict_args["lparam_gama"])

exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, 
                        en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
exp.set_U(U)
exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                    Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                    psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])

startvalues = [dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"]]
# dict_args['Max_diff'] = 0 ###ver esse role aqui
scan_points = exp.scan(args.hkli, args.hklf, int(args.points), diflimit = dic['max_diff'], 
                        name = dic['scan_name'], write=True, sep=dic['separator'], 
                        startvalues = startvalues, gui=args.gui)

angs = exp.export_angles()
exp_dict = {'Mu':angs[0], 'Eta':angs[1], 'Chi':angs[2], 'Phi':angs[3], 'Nu':angs[4], 'Del':angs[5], 'tt':angs[6],
            'theta':angs[7], 'alpha':angs[8], 'qaz':angs[9], 'naz':angs[10], 'tau':angs[11], 'psi':angs[12], 
            'beta':angs[13], 'omega':angs[14], 'hklnow':list(angs[15])}
exp_dict['hklnow'] = [float(i) for i in exp_dict['hklnow']]

if args.verbose:
    pd.options.display.max_rows = None
    pd.options.display.max_columns = 0
    print(exp)

# Do the real scan
if not args.calc:
    scan_points = pd.read_csv(dic['scan_name'])
    mu_points = [float(i) for i in scan_points["Mu"]] # Get only the points related to mu
    eta_points = [float(i) for i in scan_points["Eta"]] # Get only the points related to eta
    chi_points = [float(i) for i in scan_points["Chi"]] # Get only the points related to chi
    phi_points = [float(i) for i in scan_points["Phi"]] # Get only the points related to phi
    nu_points = [float(i) for i in scan_points["Nu"]] # Get only the points related to nu
    del_points = [float(i) for i in scan_points["Del"]] # Get only the points related to del

    if du.PV_PREFIX == "EMA:B:PB18":
        data = {'huber_mu':mu_points, 'huber_eta':eta_points, 'huber_chi':chi_points,
                'huber_phi':phi_points, 'huber_nu':nu_points, 'huber_del':del_points}

        xlabel_data = {'mu':'huber_mu', 'eta':'huber_eta', 'chi':'huber_chi',
            'phi':'huber_phi', 'nu':'huber_nu', 'del':'huber_del'}
    else:
        data = {'sol_m3':mu_points, 'sol_m5':eta_points, 'sol_m2':chi_points,
                'sol_m1':phi_points, 'sol_m4':nu_points, 'sol_m6':del_points}

        xlabel_data = {'mu':'sol_m3', 'eta':'sol_m5', 'chi':'sol_m2',
                'phi':'sol_m1', 'nu':'sol_m4', 'del':'sol_m6'}

    motors = [i for i in data.keys()]
    with open('.points.yaml', 'w') as stream:
        yaml.dump(data, stream, allow_unicode=False)

    if args.xlabel != 'points':
        xlabel = xlabel_data[args.xlabel]
    else:
        xlabel = 'points'    

    args = {'configuration': dict_args['default_counters'].split('.')[1], 'optimum': None, 'repeat': 1, 'sleep': 0, 'message': None, 
    'output': args.output, 'sync': True, 'snake': False, 'motor': motors, 'xlabel': xlabel, 
    'prescan': 'ls', 'postscan': 'pwd', 'plot_type': args.show_plot, 'relative': False, 'reset': False, 'step_mode': False, 
    'points_mode': False, 'start': None, 'end': None, 'step_or_points': None, 'time': [[args.time]], 'filename': '.points.yaml'}

    scan = sd.DAFScan(args, close_window=dic['close_window'])
    scan.run()
