#!/usr/bin/env python3
"""Show the experiment status"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



epi = '''
Eg:
    daf.status -a
    daf.status -m
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-m', '--Mode', action='store_true', help='Show current operating mode of the diffractometer')
parser.add_argument('-e', '--Experiment', action='store_true', help='Show experiment information')
parser.add_argument('-s', '--Sample', action='store_true', help='Show sample information')
parser.add_argument('-u', '--umatrix', action='store_true', help='Show current orientation matrix')
parser.add_argument('-b', '--bounds', action='store_true', help='Show current setted bounds')
parser.add_argument('-a', '--All', action='store_true', help='Show all information')


args = parser.parse_args()
dic = vars(args)

dict_args = du.read()


lb = lambda x: "{:.5f}".format(float(x))

mode = [int(i) for i in dict_args['Mode']]
idir = dict_args['IDir_print']
ndir = dict_args['NDir_print']
rdir = dict_args['RDir']

Mu_bound = dict_args['bound_Mu']
Eta_bound = dict_args['bound_Eta']
Chi_bound = dict_args['bound_Chi']
Phi_bound = dict_args['bound_Phi']
Nu_bound = dict_args['bound_Nu']
Del_bound = dict_args['bound_Del']

exp = daf.Control(*mode)
# exp.set_hkl(args.Move)
if dict_args['Material'] in dict_args['user_samples'].keys():
    exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

else: 
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
# exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir=rdir, en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
# exp.set_U(U)
exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                    Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                    psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])


if args.Mode:
    mode = exp.show(sh = 'mode')
    print(mode)
    print('')


if args.Experiment:
    mode = exp.show(sh = 'expt')
    print(mode)
    print('')

if args.Sample:
    mode = exp.show(sh = 'sample')
    print(mode)
    print('')

if args.umatrix:

    dict_args = du.read()

    U = np.array(dict_args['U_mat'])

    UB = np.array(dict_args['UB_mat'])

    center1 = "|{:^11}"
    center2 = "{:^11}"
    center3 = "{:^11}|"
    fmt1 = [
                    ('', 'ident',  9),
                    ('', 'col1',   12),
                    ('', 'col2',   12),
                    ('', 'col3',   12),

                   ]

    data1 = [{'ident':'', 'col1': center1.format(lb(U1[0])), 'col2':center2.format(lb(U1[1])), 'col3':center3.format(lb(U1[2]))},
             {'ident':'U    =   ','col1': center1.format(lb(U2[0])), 'col2':center2.format(lb(U2[1])), 'col3':center3.format(lb(U2[2]))},
             {'ident':'','col1': center1.format(lb(U3[0])), 'col2':center2.format(lb(U3[1])), 'col3':center3.format(lb(U3[2]))}
             ]

    data2 = [{'ident':'','col1': center1.format(lb(UB1[0])), 'col2':center2.format(lb(UB1[1])), 'col3':center3.format(lb(UB1[2]))},
             {'ident':'UB   = ','col1': center1.format(lb(UB2[0])), 'col2':center2.format(lb(UB2[1])), 'col3':center3.format(lb(UB2[2]))},
             {'ident':'','col1': center1.format(lb(UB3[0])), 'col2':center2.format(lb(UB3[1])), 'col3':center3.format(lb(UB3[2]))}
             ]

    Utp = daf.TablePrinter(fmt1, ul='')(data1)
    UBtp = daf.TablePrinter(fmt1, ul='')(data2)

    print('')
    print(Utp)
    print('')
    print(UBtp)
    print('')

if args.bounds:

    print('')
    print('Mu    =    {}'.format(dict_args["bound_Mu"]))
    print('Eta   =    {}'.format(dict_args["bound_Eta"]))
    print('Chi   =    {}'.format(dict_args["bound_Chi"]))
    print('Phi   =    {}'.format(dict_args["bound_Phi"]))
    print('Nu    =    {}'.format(dict_args["bound_Nu"]))
    print('Del   =    {}'.format(dict_args["bound_Del"]))
    print('')

if args.All:

    mode = exp.show(sh = 'mode')
    print(mode)
    print('')

    mode = exp.show(sh = 'expt')
    print(mode)
    print('')

    mode = exp.show(sh = 'sample')
    print(mode)
    print('')


    # dict_args = du.read()

    U = np.array(dict_args['U_mat'])

    UB = np.array(dict_args['UB_mat'])

    center1 = "|{:^11}"
    center2 = "{:^11}"
    center3 = "{:^11}|"
    fmt1 = [
                    ('', 'ident',  9),
                    ('', 'col1',   12),
                    ('', 'col2',   12),
                    ('', 'col3',   12),

                   ]

    data1 = [{'ident':'', 'col1': center1.format(lb(U[0][0])), 'col2':center2.format(lb(U[0][1])), 'col3':center3.format(lb(U[0][2]))},
             {'ident':'U    =   ','col1': center1.format(lb(U[1][0])), 'col2':center2.format(lb(U[1][1])), 'col3':center3.format(lb(U[1][2]))},
             {'ident':'','col1': center1.format(lb(U[2][0])), 'col2':center2.format(lb(U[2][1])), 'col3':center3.format(lb(U[2][2]))}
             ]

    data2 = [{'ident':'','col1': center1.format(lb(UB[0][0])), 'col2':center2.format(lb(UB[0][1])), 'col3':center3.format(lb(UB[0][2]))},
             {'ident':'UB   = ','col1': center1.format(lb(UB[1][0])), 'col2':center2.format(lb(UB[1][1])), 'col3':center3.format(lb(UB[1][2]))},
             {'ident':'','col1': center1.format(lb(UB[2][0])), 'col2':center2.format(lb(UB[2][1])), 'col3':center3.format(lb(UB[2][2]))}
             ]

    Utp = daf.TablePrinter(fmt1, ul='')(data1)
    UBtp = daf.TablePrinter(fmt1, ul='')(data2)

    print('')
    print(Utp)
    print('')
    print(UBtp)
    print('')

    print('')
    print('Mu bounds    =    {}'.format(dict_args["bound_Mu"]))
    print('Eta bounds   =    {}'.format(dict_args["bound_Eta"]))
    print('Chi bounds   =    {}'.format(dict_args["bound_Chi"]))
    print('Phi bounds   =    {}'.format(dict_args["bound_Phi"]))
    print('Nu bounds    =    {}'.format(dict_args["bound_Nu"]))
    print('Del bounds   =    {}'.format(dict_args["bound_Del"]))
    print('')


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
