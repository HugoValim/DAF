#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du


doc = """

Function to constrain angles during the experiment

"""

epi = "\n Eg: \n daf.move -mv 1 0 0, \n daf.move --Eta 15 -Del 30"


parser = ap.ArgumentParser(description=doc, epilog=epi)



parser.add_argument('-m', '--cons_Mu', metavar='', type=float, help='Constrain Mu, default: 0')
parser.add_argument('-e', '--cons_Eta', metavar='', type=float, help='Constrain Eta, default: 0')
parser.add_argument('-c', '--cons_Chi', metavar='', type=float, help='Constrain Chi, default: 0')
parser.add_argument('-p', '--cons_Phi', metavar='', type=float, help='Constrain Phi, default: 0')
parser.add_argument('-n', '--cons_Nu', metavar='', type=float, help='Constrain Nu, default: 0')
parser.add_argument('-d', '--cons_Del', metavar='', type=float, help='Constrain Del, default: 0')
parser.add_argument('-a', '--cons_alpha', metavar='', type=float, help='Constrain alpha, default: 0')
parser.add_argument('-b', '--cons_beta', metavar='', type=float, help='Constrain beta, default: 0')
parser.add_argument('-psi', '--cons_psi', metavar='', type=float, help='Constrain psi, default: 0')
parser.add_argument('-o', '--cons_omega', metavar='', type=float, help='Constrain omega, default: 0')
parser.add_argument('-q', '--cons_qaz', metavar='', type=float, help='Constrain qaz, default: 0')
parser.add_argument('-cnaz', '--cons_naz', metavar='', type=float, help='Constrain naz, default: 0')
parser.add_argument('-r', '--Reset', action='store_true', help='Reset all contrained angles to default (0)')
parser.add_argument('-l', '--List', action='store_true', help='List constrained angles')

args = parser.parse_args()
dic = vars(args)


angs = ['cons_Mu','cons_Eta', 'cons_Chi', 'cons_Phi', 'cons_Nu', 'cons_Del', 'cons_alpha', 'cons_beta', 'cons_psi', 'cons_omega', 'cons_qaz', 'cons_naz']


with open('Experiment', 'r+') as exp:
 
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
    
    with open('Experiment', 'r+') as exp:
 
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
    print(f'Alpha =   {dict_args["cons_alpha"]}')
    print(f'Beta =    {dict_args["cons_beta"]}')
    print(f'Psi =     {dict_args["cons_psi"]}')
    print(f'Qaz =     {dict_args["cons_qaz"]}')
    print(f'Naz =     {dict_args["cons_naz"]}')
    print(f'Omega =   {dict_args["cons_omega"]}')
    print('')
    print(f'Mu =      {dict_args["cons_Mu"]}')
    print(f'Eta =     {dict_args["cons_Eta"]}')
    print(f'Chi =     {dict_args["cons_Chi"]}')
    print(f'Phi =     {dict_args["cons_Phi"]}')
    print(f'Nu =      {dict_args["cons_Nu"]}')
    print(f'Del =     {dict_args["cons_Del"]}')
    print('')    
    
log = sys.argv.pop(0).split('command_line/')[1]    

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")