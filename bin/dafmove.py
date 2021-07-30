#!/usr/bin/env python3
"""Move in the reciprocal space by giving a HKL"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du

epi = '''
Eg:
    daf.mv 1 1 1
    daf.mv 1 0 0 -q
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('Move', metavar='H K L', type=float, nargs=3, help='Move to a desired HKL')
parser.add_argument('-q', '--quiet', action='store_false', help='Do not show the full output')


args = parser.parse_args()
dic = vars(args)


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

# print(type(dict_args['IDir']))
# print(type(idir))

exp = daf.Control(*mode)
exp.set_hkl(args.Move)

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


startvalue = [dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"]]

exp(sv = startvalue)
error = exp.qerror
# if error > 1e-4:
#     exp()


if args.quiet:
    exp.set_print_options(marker = '', column_marker='', space=14)
    print(exp)
angs = exp.export_angles()

exp_dict = {'Mu':angs[0], 'Eta':angs[1], 'Chi':angs[2], 'Phi':angs[3], 'Nu':angs[4], 'Del':angs[5], 'tt':angs[6],
            'theta':angs[7], 'alpha':angs[8], 'qaz':angs[9], 'naz':angs[10], 'tau':angs[11], 'psi':angs[12], 'beta':angs[13], 'omega':angs[14], 'hklnow':list(angs[15])}

# print(exp_dict['hklnow'])
# print(angs[15])

if float(angs[16]) < 1e-4:
    for j,k in exp_dict.items():
        if j in dict_args:
            dict_args[j] = str(k)
    du.write(dict_args)


else:
    print('Can\'t find the HKL {}'.format(args.Move))


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
