#!/usr/bin/env python3
"""Move the diffractometer by direct change in the angles with relative movement"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du

epi = '''
Eg:
    daf.ramv --Del 30 --Eta 15
    daf.ramv -d 30 -e 15
    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)
parser.add_argument('-m', '--mu', metavar='ang', type=float, help='Start and end for Mu')
parser.add_argument('-e', '--eta', metavar='ang', type=float, help='Start and end for Eta')
parser.add_argument('-c', '--chi', metavar='ang', type=float, help='Start and end for Chi')
parser.add_argument('-p', '--phi', metavar='ang', type=float, help='Start and end for Phi')
parser.add_argument('-n', '--nu', metavar='ang', type=float, help='Start and end for Nu')
parser.add_argument('-d', '--del', metavar='ang', type=float, help='Start and end for Del')

args = parser.parse_args()
dic = vars(args)

def write_angs():
    dict_args = du.read()
    du.log_macro(dict_args)
    mu_now = dict_args['Mu']
    eta_now = dict_args['Eta']
    chi_now = dict_args['Chi']
    phi_now = dict_args['Phi']
    nu_now = dict_args['Nu']
    del_now = dict_args['Del']

    motor_dict = {'mu':mu_now, 'eta':eta_now, 'chi':chi_now,
              'phi':phi_now, 'nu':nu_now, 'del':del_now}

    for motor in dic.keys():
        if dic[motor] is not None:
            dict_args[motor.capitalize()] = float(motor_dict[motor] + dic[motor])
    du.write(dict_args)
write_angs()

dict_args = du.read()
U = np.array(dict_args['U_mat'])
mode = [int(i) for i in dict_args['Mode']]
idir = dict_args['IDir']
ndir = dict_args['NDir']
rdir = dict_args['RDir']

exp = daf.Control(*mode)
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])
if dict_args['Material'] in dict_args['user_samples'].keys():
    exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])
else: 
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], 
                    dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], 
                    dict_args["lparam_gama"])
    
exp.set_U(U)
hklnow = exp.calc_from_angs(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])
hklnow = [float(i) for i in hklnow]
pseudo = exp.calc_pseudo(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])
pseudo_dict = {'alpha':pseudo[0], 'qaz':pseudo[1], 'naz':pseudo[2], 'tau':pseudo[3], 'psi':pseudo[4], 'beta':pseudo[5], 'omega':pseudo[6], 'hklnow':hklnow}

for j,k in pseudo_dict.items():
    if j in dict_args:
        if not isinstance(k, list):
            dict_args[j] = float(k)
        else:
            dict_args[j] = k
du.write(dict_args)
