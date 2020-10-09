#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import dafutilities as du
doc = """

Sets the bounds of the diffractometer angles

"""

epi = "Eg: daf.bound --Mu -180 180 --Nu -180 180"
    

parser = ap.ArgumentParser(description=doc, epilog=epi)

parser.add_argument('-m', '--bound_Mu', metavar='', type=float, nargs=2, help='Sets Mu bounds')
parser.add_argument('-e', '--bound_Eta', metavar='',type=float, nargs=2, help='Sets Eta bounds')
parser.add_argument('-c', '--bound_Chi', metavar='',type=float, nargs=2, help='Sets Chi bounds')
parser.add_argument('-p', '--bound_Phi', metavar='',type=float, nargs=2, help='Sets Phi bounds')
parser.add_argument('-n', '--bound_Nu', metavar='',type=float, nargs=2, help='Sets Nu bounds')
parser.add_argument('-d', '--bound_Del', metavar='',type=float, nargs=2, help='Sets Del bounds')
parser.add_argument('-l', '--list', action='store_true', help='List the current bounds')

args = parser.parse_args()
dic = vars(args)
# print([(i,j) for i,j in dic.items()])
# with open ('Experiment', 'w') as doc:
#     for i,j in dic.items():
#         doc.write(str(i)+': '+str(j)+'\n')
# ndir = list2str(args.NDir)

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

dict_args = du.dict_conv()      
        
if args.list:
    
    print('')
    print(f'Mu =      {dict_args["bound_Mu"]}')
    print(f'Eta =     {dict_args["bound_Eta"]}')
    print(f'Chi =     {dict_args["bound_Chi"]}')
    print(f'Phi =     {dict_args["bound_Phi"]}')
    print(f'Nu =      {dict_args["bound_Nu"]}')
    print(f'Del =     {dict_args["bound_Del"]}')
    print('')    
    



log = sys.argv.pop(0).split('command_line/')[1]         

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")