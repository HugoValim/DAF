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

epi = '''
Eg:
    daf.status -a
    daf.status -m
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)

parser.add_argument('-m', '--Mode', action='store_true', help='Show current operating mode of the diffractometer')
parser.add_argument('-e', '--Experiment', action='store_true', help='Show experiment information')
parser.add_argument('-u', '--umatrix', action='store_true', help='Show current orientation matrix')
parser.add_argument('-b', '--bounds', action='store_true', help='Show current setted bounds')
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
rdir = ret_list(dict_args['RDir'])

Mu_bound = ret_list(dict_args['bound_Mu'])
Eta_bound = ret_list(dict_args['bound_Eta'])
Chi_bound = ret_list(dict_args['bound_Chi'])
Phi_bound = ret_list(dict_args['bound_Phi'])
Nu_bound = ret_list(dict_args['bound_Nu'])
Del_bound = ret_list(dict_args['bound_Del'])

exp = daf.Control(*mode)
# exp.set_hkl(args.Move)
exp.set_material(dict_args['Material'], float(dict_args["lparam_a"]), float(dict_args["lparam_b"]), float(dict_args["lparam_c"]), float(dict_args["lparam_alpha"]), float(dict_args["lparam_beta"]), float(dict_args["lparam_gama"]))
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir=rdir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
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

if args.umatrix:

    dict_args = du.dict_conv()

    Uw = dict_args['U_mat'].split(',')


    U1 = [float(i) for i in Uw[0].strip('][').split(' ') if i != '']
    U2 = [float(i) for i in Uw[1].strip('][').split(' ') if i != '']
    U3 = [float(i) for i in Uw[2].strip('][').split(' ') if i != '']
    U = np.array([U1, U2, U3])

    UBw = dict_args['UB_mat'].split(',')


    UB1 = [float(i) for i in UBw[0].strip('][').split(' ') if i != '']
    UB2 = [float(i) for i in UBw[1].strip('][').split(' ') if i != '']
    UB3 = [float(i) for i in UBw[2].strip('][').split(' ') if i != '']
    UB = np.array([UB1, UB2, UB3])

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


    # dict_args = du.dict_conv()

    Uw = dict_args['U_mat'].split(',')


    U1 = [float(i) for i in Uw[0].strip('][').split(' ') if i != '']
    U2 = [float(i) for i in Uw[1].strip('][').split(' ') if i != '']
    U3 = [float(i) for i in Uw[2].strip('][').split(' ') if i != '']
    U = np.array([U1, U2, U3])

    UBw = dict_args['UB_mat'].split(',')


    UB1 = [float(i) for i in UBw[0].strip('][').split(' ') if i != '']
    UB2 = [float(i) for i in UBw[1].strip('][').split(' ') if i != '']
    UB3 = [float(i) for i in UBw[2].strip('][').split(' ') if i != '']
    UB = np.array([UB1, UB2, UB3])

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

    print('')
    print('Mu    =    {}'.format(dict_args["bound_Mu"]))
    print('Eta   =    {}'.format(dict_args["bound_Eta"]))
    print('Chi   =    {}'.format(dict_args["bound_Chi"]))
    print('Phi   =    {}'.format(dict_args["bound_Phi"]))
    print('Nu    =    {}'.format(dict_args["bound_Nu"]))
    print('Del   =    {}'.format(dict_args["bound_Del"]))
    print('')


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
