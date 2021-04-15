#!/usr/bin/env python3

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du


doc = """

Function to constrain angles during the experiment

"""

epi = '''
Eg:
    daf.cons --cons_Del 30 --cons_naz 15
    daf.amv -d 30 -cnaz 15
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)


parser.add_argument('-m', '--cons_Mu', metavar='ang', type=float, help='Constrain Mu, default: 0')
parser.add_argument('-e', '--cons_Eta', metavar='ang', type=float, help='Constrain Eta, default: 0')
parser.add_argument('-c', '--cons_Chi', metavar='ang', type=float, help='Constrain Chi, default: 0')
parser.add_argument('-p', '--cons_Phi', metavar='ang', type=float, help='Constrain Phi, default: 0')
parser.add_argument('-n', '--cons_Nu', metavar='ang', type=float, help='Constrain Nu, default: 0')
parser.add_argument('-d', '--cons_Del', metavar='ang', type=float, help='Constrain Del, default: 0')
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


angs = ['cons_Mu','cons_Eta', 'cons_Chi', 'cons_Phi', 'cons_Nu', 'cons_Del', 'cons_alpha', 'cons_beta', 'cons_psi', 'cons_omega', 'cons_qaz', 'cons_naz']


with open('.Experiment', 'r+') as exp:

    lines = exp.readlines()


    for i, line in enumerate(lines):
        for j,k in dic.items():


            if line.startswith(str(j)):
                if k != None:
                    lines[i] = str(j)+'='+str(k)+'\n'

            exp.seek(0)


    for line in lines:
        exp.write(line)


if args.Reset:

    with open('.Experiment', 'r+') as exp:

        lines = exp.readlines()


        for i, line in enumerate(lines):
            for j in angs:


                if line.startswith(str(j)):
                        lines[i] = str(j)+'=0'+'\n'

                exp.seek(0)


        for line in lines:
            exp.write(line)

dict_args = du.dict_conv()


if args.List:


    print('')
    print('Alpha =    {}'.format(dict_args["cons_alpha"]))
    print('Beta  =    {}'.format(dict_args["cons_beta"]))
    print('Psi   =    {}'.format(dict_args["cons_psi"]))
    print('Qaz   =    {}'.format(dict_args["cons_qaz"]))
    print('Naz   =    {}'.format(dict_args["cons_naz"]))
    print('Omega =    {}'.format(dict_args["cons_omega"]))
    print('')
    print('Mu    =    {}'.format(dict_args["cons_Mu"]))
    print('Eta   =    {}'.format(dict_args["cons_Eta"]))
    print('Chi   =    {}'.format(dict_args["cons_Chi"]))
    print('Phi   =    {}'.format(dict_args["cons_Phi"]))
    print('Nu    =    {}'.format(dict_args["cons_Nu"]))
    print('Del   =    {}'.format(dict_args["cons_Del"]))
    print('')

log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
