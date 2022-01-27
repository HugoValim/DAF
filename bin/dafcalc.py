#!/usr/bin/env python3
"""Calculate the diffractometer angles needed to reach a given HKL position"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du

epi = '''
Eg:
    daf.ca 1 1 1
    daf.ca 1 0 0 -q
    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)
parser.add_argument('Move', metavar='H K L', type=float, nargs=3, help='Move to a desired HKL')
parser.add_argument('-q', '--quiet', action='store_false', help='Do not show the full output')

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
exp.set_hkl(args.Move)
if dict_args['Material'] in dict_args['user_samples'].keys():
    exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

else: 
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
# exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
exp.set_U(U)
exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                    Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                    psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])
startvalue = [dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"]]
exp(sv = startvalue)
error = exp.qerror
angs = exp.export_angles()

if args.quiet:
    exp.set_print_options(marker = '', column_marker='', space=14)
    print(exp)
if float(angs[16]) > 1e-4:
    print('Can\'t find the HKL {}'.format(args.Move))
