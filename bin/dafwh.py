#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
print(f'HKL now =   ', lb(hklnow[0]), lb(hklnow[1]), lb(hklnow[2]))
print('')
print(f'Alpha   =    {lb(dict_args["alpha"])}')
print(f'Beta    =    {lb(dict_args["beta"])}')
print(f'Psi     =    {lb(dict_args["psi"])}')
print(f'Tau     =    {lb(dict_args["tau"])}')
print(f'Qaz     =    {lb(dict_args["qaz"])}')
print(f'Naz     =    {lb(dict_args["naz"])}')
print(f'Omega   =    {lb(dict_args["omega"])}')
print('')
print(f'Del     =    {lb(dict_args["Del"])}')
print(f'Eta     =    {lb(dict_args["Eta"])}')
print(f'Chi     =    {lb(dict_args["Chi"])}')
print(f'Phi     =    {lb(dict_args["Phi"])}')
print(f'Nu      =    {lb(dict_args["Nu"])}')
print(f'Mu      =    {lb(dict_args["Mu"])}')
print('')    
    
log = sys.argv.pop(0).split('command_line/')[1]    

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")