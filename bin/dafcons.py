#!/usr/bin/env python3
"""Function to constrain angles during the experiment"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



epi = '''
Eg:
    daf.cons --cons_del 30 --cons_naz 15
    daf.amv -d 30 -cnaz 15
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)


parser.add_argument('-m', '--cons_mu', metavar='ang', type=float, help='Constrain Mu, default: 0')
parser.add_argument('-e', '--cons_eta', metavar='ang', type=float, help='Constrain Eta, default: 0')
parser.add_argument('-c', '--cons_chi', metavar='ang', type=float, help='Constrain Chi, default: 0')
parser.add_argument('-p', '--cons_phi', metavar='ang', type=float, help='Constrain Phi, default: 0')
parser.add_argument('-n', '--cons_nu', metavar='ang', type=float, help='Constrain Nu, default: 0')
parser.add_argument('-d', '--cons_del', metavar='ang', type=float, help='Constrain Del, default: 0')
parser.add_argument('-a', '--cons_alpha', metavar='ang', type=float, help='Constrain alpha, default: 0')
parser.add_argument('-b', '--cons_beta', metavar='ang', type=float, help='Constrain beta, default: 0')
parser.add_argument('-psi', '--cons_psi', metavar='ang', type=float, help='Constrain psi, default: 0')
parser.add_argument('-o', '--cons_omega', metavar='ang', type=float, help='Constrain omega, default: 0')
parser.add_argument('-q', '--cons_qaz', metavar='ang', type=float, help='Constrain qaz, default: 0')
parser.add_argument('-cnaz', '--cons_naz', metavar='ang', type=float, help='Constrain naz, default: 0')
parser.add_argument('-r', '--Reset', action='store_true', help='Reset all contrained angles to default (0)')
parser.add_argument('-l', '--List', action='store_true', help='List constrained angles')

args = parser.parse_args()
dic = vars(args)


angs = ['cons_mu','cons_eta', 'cons_chi', 'cons_phi', 'cons_nu', 'cons_del', 'cons_alpha', 'cons_beta', 'cons_psi', 'cons_omega', 'cons_qaz', 'cons_naz']


dict_args = du.read()

for j,k in dic.items():
    if j in dict_args and k is not None:
        dict_args[j] = str(k)
du.write(dict_args)


if args.Reset:

    for j in angs:
        if j in dict_args:
            dict_args[j] = '0'
    du.write(dict_args)

dict_args = du.read()


if args.List:


    print('')
    print('Alpha =    {}'.format(dict_args["cons_alpha"]))
    print('Beta  =    {}'.format(dict_args["cons_beta"]))
    print('Psi   =    {}'.format(dict_args["cons_psi"]))
    print('Qaz   =    {}'.format(dict_args["cons_qaz"]))
    print('Naz   =    {}'.format(dict_args["cons_naz"]))
    print('Omega =    {}'.format(dict_args["cons_omega"]))
    print('')
    print('Mu    =    {}'.format(dict_args["cons_mu"]))
    print('Eta   =    {}'.format(dict_args["cons_eta"]))
    print('Chi   =    {}'.format(dict_args["cons_chi"]))
    print('Phi   =    {}'.format(dict_args["cons_phi"]))
    print('Nu    =    {}'.format(dict_args["cons_nu"]))
    print('Del   =    {}'.format(dict_args["cons_del"]))
    print('')

log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
