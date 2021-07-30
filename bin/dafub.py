#!/usr/bin/env python3
"""Defines UB matrix and Calculate UB matrix from 2 or 3 reflections"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



epi = '''
Eg:
    daf.ub -r1 1 0 0 0 5.28232 0 2 0 10.5647
    daf.ub -r2 0 1 0 0 5.28232 2 92 0 10.5647
    daf.ub -c2 1 2
    daf.ub -c2 2 3
    daf.ub -U 1 0 0 0 1 0 0 0 1
    daf.up -s
    daf.up -s -p
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-r1', '--hkl1', metavar=('H', 'K', 'L', 'Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'), type=float, nargs=9, help='HKL and angles for first reflection')
parser.add_argument('-r2', '--hkl2', metavar=('H', 'K', 'L', 'Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'), type=float, nargs=9, help='HKL and angles for second reflection')
parser.add_argument('-r3', '--hkl3', metavar=('H', 'K', 'L', 'Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'),type=float, nargs=9, help='HKL and angles for third reflection')
parser.add_argument('-U', '--Umatrix', metavar=('a11', 'a12', 'a13', 'a21', 'a22', 'a23', 'a31', 'a32', 'a33'), type=float, nargs=9, help='Sets U matrix')
parser.add_argument('-UB', '--UBmatrix', metavar=('a11', 'a12', 'a13', 'a21', 'a22', 'a23', 'a31', 'a32', 'a33'), type=float, nargs=9, help='Sets UB matrix')
parser.add_argument('-c2', '--Calc2', metavar=('R1', 'R2'),type=int, nargs=2, help='Calculate UB for 2 reflections, user must give the reflections that will be used')
parser.add_argument('-c3', '--Calc3', action='store_true', help='Calculate UB for 3 reflections, the right energy must be setted in this case')
parser.add_argument('-l', '--list', action='store_true', help='List stored reflections')
parser.add_argument('-s', '--Show', action='store_true', help='Show U and UB')
parser.add_argument('-p', '--Params', action='store_true', help='Lattice parameters if 3 reflection calculation had been done')


args = parser.parse_args()
dic = vars(args)


dict_args = du.read()

for j,k in dic.items():
    if j in dict_args and k is not None:
        dict_args[j] = k
du.write(dict_args)


if args.UBmatrix:
    UB = np.array(args.UBmatrix).reshape(3,3)
    #dict_args['U'] = str(U[0]) + ',' + str(U[1]) + ',' + str(U[2])
    dict_args['UB_mat'] = UB.tolist()
    du.write(dict_args)


lb = lambda x: "{:.5f}".format(float(x))


if args.Show:

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


if args.Params:

    dict_args = du.read()

    print('')
    print('a    =    {}'.format(dict_args["lparam_a"]))
    print('b    =    {}'.format(dict_args["lparam_b"]))
    print('c    =    {}'.format(dict_args["lparam_c"]))
    print('alpha    =    {}'.format(dict_args["lparam_alpha"]))
    print('beta    =    {}'.format(dict_args["lparam_beta"]))
    print('gamma    =    {}'.format(dict_args["lparam_gama"]))
    print('')



dict_args = du.read()

if dict_args['hkl1'] != '':
    r1 = dict_args['hkl1']
    hkl1 = r1[:3]
    angs1 = r1[3:9]
else:
    hkl1 = None


if dict_args['hkl2'] != '':
    r2 = dict_args['hkl2']
    hkl2 = r2[:3]
    angs2 = r2[3:9]
else:
    hkl2 = None

if dict_args['hkl3'] != '':
    r3 = dict_args['hkl3']
    hkl3 = r3[:3]
    angs3 = r3[3:9]
else:
    hkl3 = None

if args.list:
    print('')
    if hkl1:
        print('HKL1: {}  {}'.format(hkl1, angs1))
    if hkl2:
        print('HKL2: {}  {}'.format(hkl2, angs2))
    if hkl3:
        print('HKL3: {}  {}'.format(hkl3, angs3))

    print('')

if args.Umatrix:
    U = np.array(args.Umatrix).reshape(3,3)
    mode = [int(i) for i in dict_args['Mode']]

    exp = daf.Control(*mode)

    if dict_args['Material'] in dict_args['user_samples'].keys():
        exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

    else: 
        exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
    # exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    exp.set_exp_conditions(en = float(dict_args['Energy']))
    exp.set_U(U)
    UB = exp.calcUB()
    dict_args['U_mat'] = U.tolist() # yaml doesn't handle numpy arrays well, so using python's list is a better choice
    dict_args['UB_mat'] = UB.tolist() # yaml doesn't handle numpy arrays well, so using python's list is a better choice
    du.write(dict_args)


if  args.Calc2 is not None:
    mode = [int(i) for i in dict_args['Mode']]

    exp = daf.Control(*mode)
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    exp.set_exp_conditions(en = dict_args['Energy'])

    if args.Calc2[0] == 1 and args.Calc2[1] == 2:
        U, UB = exp.calc_U_2HKL(hkl1, angs1, hkl2, angs2)

    elif args.Calc2[0] == 1 and args.Calc2[1] == 3:
        U, UB = exp.calc_U_2HKL(hkl1, angs1, hkl3, angs3)

    elif args.Calc2[0] == 2 and args.Calc2[1] == 3:
        U, UB = exp.calc_U_2HKL(hkl2, angs2, hkl3, angs3)



    dict_args['U_mat'] = U.tolist()
    dict_args['UB_mat'] = UB.tolist()
    du.write(dict_args)

if  args.Calc3:
    mode = [int(i) for i in dict_args['Mode']]

    exp = daf.Control(*mode)
    # exp.set_material(dict_args['Material'])
    exp.set_exp_conditions(en = dict_args['Energy'])

    U, UB, rp = exp.calc_U_3HKL(hkl1, angs1, hkl2, angs2, hkl3, angs3)

    rpf = [float(i) for i in rp]# Problems when saving numpy64floats, better to use python's float

    dict_args['U_mat'] = U.tolist()
    dict_args['UB_mat'] = UB.tolist()
    dict_args['lparam_a'] = rpf[0]
    dict_args['lparam_b'] = rpf[1]
    dict_args['lparam_c'] = rpf[2]
    dict_args['lparam_alpha'] = rpf[3]
    dict_args['lparam_beta'] = rpf[4]
    dict_args['lparam_gama'] = rpf[5]
    du.write(dict_args)


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
