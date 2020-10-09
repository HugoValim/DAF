#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



doc = """

Show the experiment status

"""

epi = "\n Eg: \n daf.move -mv 1 0 0, \n daf.move --Eta 15 -Del 30"


parser = ap.ArgumentParser(description=doc, epilog=epi)

parser.add_argument('-m', '--Mode', action='store_true', help='Show current mode of diffractometer')
parser.add_argument('-e', '--Experiment', action='store_true', help='Show experiment information')
parser.add_argument('-a', '--All', action='store_true', help='Show all information')


args = parser.parse_args()
dic = vars(args)

dict_args = du.dict_conv()
 
def ret_list(string):
    
    return [float(i) for i in string.strip('][').split(', ')]        

    

lb = lambda x: "{:.5f}".format(float(x))

mode = [int(i) for i in dict_args['Mode']]    
idir = ret_list(dict_args['IDir'])
ndir = ret_list(dict_args['NDir'])
Mu_bound = ret_list(dict_args['bound_Mu'])
Eta_bound = ret_list(dict_args['bound_Eta'])
Chi_bound = ret_list(dict_args['bound_Chi'])
Phi_bound = ret_list(dict_args['bound_Phi'])
Nu_bound = ret_list(dict_args['bound_Nu'])
Del_bound = ret_list(dict_args['bound_Del'])

exp = daf.Control(*mode)
# exp.set_hkl(args.Move)
exp.set_material(dict_args['Material'])
exp.set_exp_conditions(idir = idir, ndir = ndir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
# exp.set_U(U)
exp.set_constraints(Mu = float(dict_args['cons_Mu']), Eta = float(dict_args['cons_Eta']), Chi = float(dict_args['cons_Chi']), Phi = float(dict_args['cons_Phi']),
                    Nu = float(dict_args['cons_Nu']), Del = float(dict_args['cons_Del']), alpha = float(dict_args['cons_alpha']), beta = float(dict_args['cons_beta']),
                    psi = float(dict_args['cons_psi']), omega = float(dict_args['cons_omega']), qaz = float(dict_args['cons_qaz']), naz = float(dict_args['cons_naz']))

if args.Mode:
    mode = exp.show(sh = 'mode')
    print(mode)
    print('')



if args.Experiment:
    mode = exp.show(sh = 'expt')
    print(mode)
    print('')

if args.All:
    
    mode = exp.show(sh = 'mode')
    print(mode)
    print('')

    mode = exp.show(sh = 'expt')
    print(mode)
    print('')


    
log = sys.argv.pop(0).split('command_line/')[1]    

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")