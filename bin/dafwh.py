#!/usr/bin/env python3

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du


doc = """

Show where you are in reciprocal space as well as all angles and pseudo angles of diffractometer

"""

epi = '''
Eg:
    daf.wh
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)

parser.add_argument('-s', '--status', action='store_true', help='Show where you are in space')

args = parser.parse_args()
dic = vars(args)

dict_args = du.dict_conv()

def ret_list(string):

    return [float(i) for i in string.strip('][').split(', ')]


lb = lambda x: "{:.5f}".format(float(x))

hklnow = ret_list(dict_args["hklnow"])

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
