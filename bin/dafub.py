#!/usr/bin/env python3
"""Defines UB matrix and Calculate UB matrix from 2 or 3 reflections"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import xrayutilities as xu

import dafutilities as du



epi = '''
Eg:
    daf.ub -r 1 0 0 0 5.28232 0 2 0 10.5647
    daf.ub -r 0 1 0 0 5.28232 2 92 0 10.5647
    daf.ub -c2 1 2
    daf.ub -c3 1 2 3
    daf.ub -U 1 0 0 0 1 0 0 0 1
    daf.ub -s
    daf.ub -s -p
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-r', '--reflection', metavar=('H', 'K', 'L', 'Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'), type=float, nargs=9, help='HKL and angles for this reflection')
parser.add_argument('-rn', '--reflection-now', action='store_true', help='HKL for the current position')
parser.add_argument('-U', '--Umatrix', metavar=('a11', 'a12', 'a13', 'a21', 'a22', 'a23', 'a31', 'a32', 'a33'), type=float, nargs=9, help='Sets U matrix')
parser.add_argument('-UB', '--UBmatrix', metavar=('a11', 'a12', 'a13', 'a21', 'a22', 'a23', 'a31', 'a32', 'a33'), type=float, nargs=9, help='Sets UB matrix')
parser.add_argument('-c2', '--Calc2', metavar=('R1', 'R2'),type=int, nargs=2, help='Calculate UB for 2 reflections, user must give the reflections that will be used')
parser.add_argument('-c3', '--Calc3', metavar=('R1', 'R2', 'R3'), type=int, nargs=3, help='Calculate UB for 3 reflections, user must give the reflections that will be used')
parser.add_argument('-f', '--fit', action='store_true', help='fit reflections')
parser.add_argument('-cr', '--clear-reflections', action='store_true', help='Clear all stored reflections')
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


if args.reflection is not None:
    dict_args = du.read()
    ref = dict_args['reflections']
    en = dict_args['Energy']
    if en < 50 :
        en = float(xu.lam2en(en))
    args.reflection.append(en)
    ref.append(args.reflection)
    dict_args['reflections'] = ref
    du.write(dict_args)

if args.reflection_now:
    dict_args = du.read()
    ref = dict_args['reflections']
    h = dict_args['hklnow'][0]
    k = dict_args['hklnow'][1]
    l = dict_args['hklnow'][2]
    mu = dict_args['Mu']
    eta = dict_args['Eta']
    chi = dict_args['Chi']
    phi = dict_args['Phi']
    nu = dict_args['Nu']
    delta = dict_args['Del']
    en = dict_args['Energy']
    if en < 50 :
        en = float(xu.lam2en(en))
    ref_now = [h, k, l, mu, eta, chi, phi, nu , delta, en]
    ref.append(ref_now)
    dict_args['reflections'] = ref
    du.write(dict_args)

if args.list:
    dict_args = du.read()
    refs = dict_args['reflections']
    center = "{:^11}"
    space = 10
    fmt = [
                    ('', 'col1', space),
                    ('', 'col2', space),
                    ('', 'col3', space),
                    ('', 'col4', space),
                    ('', 'col5', space),
                    ('', 'col6', space),
                    ('', 'col7', space),
                    ('', 'col8', space),
                    ('', 'col9', space),
                    ('', 'col10', space),
                    ('', 'col11', space)
                   ]
    data = [{'col1': center.format('Index'), 'col2': center.format('H'), 'col3': center.format('K'),
            'col4': center.format('L'), 'col5': center.format('Mu'), 'col6': center.format('Eta'),
            'col7': center.format('Chi'), 'col8': center.format('Phi'), 'col9': center.format('Nu'),
            'col10': center.format('Del'), 'col11': center.format('Energy')}]
    
    for i in range(len(refs)):
        dict_ = {'col1': center.format(str(i+1)), 'col2': center.format(str(refs[i][0])), 'col3': center.format(str(refs[i][1])),
                'col4': center.format(str(refs[i][2])), 'col5': center.format(str(refs[i][3])), 'col6': center.format(str(refs[i][4])),
                'col7': center.format(str(refs[i][5])), 'col8': center.format(str(refs[i][6])), 'col9': center.format(str(refs[i][7])),
                'col10': center.format(str(refs[i][8])), 'col11': center.format(str(refs[i][9]))}
        data.append(dict_)

    pd = daf.TablePrinter(fmt, ul='')(data)
    print(pd)
    print('')


if args.clear_reflections:
    dict_args = du.read()
    dict_args['reflections'] = []
    du.write(dict_args)

if args.Umatrix:
    dict_args = du.read()
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
    dict_args = du.read()
    refs = dict_args['reflections']
    mode = [int(i) for i in dict_args['Mode']]

    exp = daf.Control(*mode)
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    exp.set_exp_conditions(en = dict_args['Energy'])
    hkl1 = refs[args.Calc2[0] - 1][:3]
    angs1 = refs[args.Calc2[0] - 1][3:-1]
    hkl2 = refs[args.Calc2[1] - 1][:3]
    angs2 = refs[args.Calc2[1] - 1][3:-1]
    U, UB = exp.calc_U_2HKL(hkl1, angs1, hkl2, angs2)

    dict_args['U_mat'] = U.tolist()
    dict_args['UB_mat'] = UB.tolist()
    du.write(dict_args)

if  args.Calc3 is not None:
    dict_args = du.read()
    refs = dict_args['reflections']
    mode = [int(i) for i in dict_args['Mode']]
    exp = daf.Control(*mode)
    # exp.set_material(dict_args['Material'])
    
    hkl1 = refs[args.Calc3[0] - 1][:3]
    angs1 = refs[args.Calc3[0] - 1][3:-1]
    e1 = refs[args.Calc3[0] - 1][9]
    hkl2 = refs[args.Calc3[1] - 1][:3]
    angs2 = refs[args.Calc3[1] - 1][3:-1]
    e2 = refs[args.Calc3[1] - 1][9]
    hkl3 = refs[args.Calc3[2] - 1][:3]
    angs3 = refs[args.Calc3[2] - 1][3:-1]
    e3 = refs[args.Calc3[2] - 1][9]
    e = (e1 + e2 + e3)/3
    exp.set_exp_conditions(en = e)
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

if args.fit:
    dict_args = du.read()
    refs = dict_args['reflections']
    mode = [int(i) for i in dict_args['Mode']]

    exp = daf.Control(*mode)
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    exp.set_exp_conditions(en = dict_args['Energy'])
    U = np.array(dict_args['U_mat'])
    if dict_args['Material'] in dict_args['user_samples'].keys():
        exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

    else: 
        exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
    fitted = exp.fit_u_matrix(U, refs)
    lbd = [[float(lb(i)) for i in j] for j in fitted]
    print(np.array(lbd))

    dict_args['U_mat'] = U.tolist()
    # dict_args['UB_mat'] = UB.tolist()
    du.write(dict_args)


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
