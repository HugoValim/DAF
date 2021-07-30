#!/usr/bin/env python3
"""Move the diffractometer by direct change in the angles"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



epi = '''
Eg:
    daf.amv --Del 30 --Eta 15
    daf.amv -d 30 -e 15
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-m', '--Mu', metavar='ang', type=float, help='Sets Mu angle to a desired position')
parser.add_argument('-e', '--Eta', metavar='ang', type=float, help='Sets Eta angle to a desired position')
parser.add_argument('-c', '--Chi', metavar='ang', type=float, help='Sets Chi angle to a desired position')
parser.add_argument('-p', '--Phi', metavar='ang', type=float, help='Sets Phi angle to a desired position')
parser.add_argument('-n', '--Nu', metavar='ang', type=float, help='Sets Nu angle to a desired position')
parser.add_argument('-d', '--Del', metavar='ang', type=float, help='Sets Del angle to a desired position')
# parser.add_argument('-v', '--verbosity', action='store_true', help='Show full output')

args = parser.parse_args()
dic = vars(args)


dict_args = du.read()

for j,k in dic.items():
    if j in dict_args and k is not None:
        dict_args[j] = str(k)
du.write(dict_args)


dict_args = du.read()

U = np.array(dict_args['U_mat'])


mode = [int(i) for i in dict_args['Mode']]
idir = dict_args['IDir']
ndir = dict_args['NDir']
rdir = dict_args['RDir']

exp = daf.Control(*mode)
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])

if dict_args['Material'] in dict_args['user_samples'].keys():
    exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

else: 
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
# exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
exp.set_U(U)
hklnow = exp.calc_from_angs(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])
hklnow = list(hklnow)
pseudo = exp.calc_pseudo(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])

pseudo_dict = {'alpha':pseudo[0], 'qaz':pseudo[1], 'naz':pseudo[2], 'tau':pseudo[3], 'psi':pseudo[4], 'beta':pseudo[5], 'omega':pseudo[6], 'hklnow':hklnow}


for j,k in pseudo_dict.items():
    if j in dict_args:
        dict_args[j] = str(k)
du.write(dict_args)


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
