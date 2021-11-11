#!/usr/bin/env python3
"""Show where you are in reciprocal space as well as all angles and pseudo angles of diffractometer"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



epi = '''
Eg:
    daf.wh
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-s', '--status', action='store_true', help='Show where you are in space')

args = parser.parse_args()
dic = vars(args)

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
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])

# exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
exp.set_U(U)
hklnow = exp.calc_from_angs(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])
hklnow = list(hklnow)


lb = lambda x: "{:.5f}".format(float(x))

print('')
print('HKL now =   ', lb(hklnow[0]), lb(hklnow[1]), lb(hklnow[2]))
print('')
print('Alpha   =    {}'.format(lb(dict_args["alpha"])))
print('Beta    =    {}'.format(lb(dict_args["beta"])))
print('Psi     =    {}'.format(lb(dict_args["psi"])))
print('Tau     =    {}'.format(lb(dict_args["tau"])))
print('Qaz     =    {}'.format(lb(dict_args["qaz"])))
print('Naz     =    {}'.format(lb(dict_args["naz"])))
print('Omega   =    {}'.format(lb(dict_args["omega"])))
print('')
print('Del     =    {}'.format(lb(dict_args["Del"])))
print('Eta     =    {}'.format(lb(dict_args["Eta"])))
print('Chi     =    {}'.format(lb(dict_args["Chi"])))
print('Phi     =    {}'.format(lb(dict_args["Phi"])))
print('Nu      =    {}'.format(lb(dict_args["Nu"])))
print('Mu      =    {}'.format(lb(dict_args["Mu"])))
print('')

log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
