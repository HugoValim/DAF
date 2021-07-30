#!/usr/bin/env python3
"""Perform a scan using HKL coordinates"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du
import pandas as pd


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
parser.add_argument('-n', '--scan_name', metavar='', type=str, help='Name of the scan')
parser.add_argument('-s', '--step', metavar='', type=float, help='Step for the scan')
parser.add_argument('-sep', '--separator', metavar='', type=str, help='Chose the separator of scan file, comma is default')
parser.add_argument('-m', '--Max_diff', metavar='', type=float, help='Max difference of angles variation (default is 0.1), if 0 is given no verification will be done')
parser.add_argument('-v', '--verbose', action='store_true', help='Show full output')
parser.add_argument('-p', '--perform', action='store_true', help='Perform the scan')
parser.add_argument('-t', '--time', metavar='', type=float, help='Acquisition time in each point in seconds. Default is 0.01s')
parser.add_argument('-x', '--xlabel', help='motor which position is shown in x axis (if not set, point index is shown instead)', default='points')
parser.add_argument('-c', '--configuration', type=str, help='choose a counter configuration file', default='default')

args = parser.parse_args()
dic = vars(args)


dict_args = du.read()

for j,k in dic.items():
    if j in dict_args and k is not None:
        dict_args[j] = str(k)
du.write(dict_args, is_scan = True)


dict_args = du.read()

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
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
# exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['Energy'], sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
exp.set_U(U)
exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                    Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                    psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])


startvalues = [dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"]]

dict_args['Max_diff'] = 0 ###ver esse role aqui

scan_points = exp.scan(args.hkli, args.hklf, int(args.points), diflimit = dict_args['Max_diff'], name = dict_args['scan_name'], write=True, sep=dict_args['separator'], startvalues = startvalues)

if args.verbose:
    pd.options.display.max_rows = None
    pd.options.display.max_columns = 0

    print(exp)

angs = exp.export_angles()
exp_dict = {'Mu':angs[0], 'Eta':angs[1], 'Chi':angs[2], 'Phi':angs[3], 'Nu':angs[4], 'Del':angs[5], 'tt':angs[6],
            'theta':angs[7], 'alpha':angs[8], 'qaz':angs[9], 'naz':angs[10], 'tau':angs[11], 'psi':angs[12], 
            'beta':angs[13], 'omega':angs[14], 'hklnow':list(angs[15])}
exp_dict['hklnow'] = [float(i) for i in exp_dict['hklnow']]


if args.perform:

    if args.time == None:
        time = 0.01
    else:
        time = args.time

    os.system("daf.rfscan -f {} -t {} -x {} -c {}".format(dict_args['scan_name'], time, args.xlabel, args.configuration))



if float(angs[16]) < 1e-4:
    for j,k in exp_dict.items():
        if j in dict_args:
            dict_args[j] = str(k)
    # du.write(dict_args, is_scan = True)


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
