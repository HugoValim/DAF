#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
doc = """
     >detector<  >Reference<     >Sample<     >Sample<     >Sample<
        g_mode1      g_mode2      g_mode3      g_mode4      g_mode5
0             .            .  omega-fixed            X            X  0
1   Delta-fixed   Alpha=Beta    Eta-fixed    Eta-fixed    Eta-fixed  1
2      Nu-fixed  Alpha-fixed     Mu-fixed     Mu-fixed     Mu-fixed  2
3     Qaz-fixed   Beta-fixed    Chi-fixed    Chi-fixed    Chi-fixed  3
4     Naz-fixed    Psi-fixed    Phi-fixed    Phi-fixed    Phi-fixed  4
5          Zone            X    Eta=Del/2            X            X  5
6             X            X      Mu=Nu/2            X            X  6

"""
epi = "Eg: \n daf.mode 215, will set Nu fix, Alpha=Beta, Eta=Del/2"


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog = epi)

parser.add_argument('-m', '--Mode', type=str,help='Set the operation mode of the diffractometer, following the same modes as used in Spec')
parser.add_argument('-s', '--Show', action='store_true', help='Show current mode')

args = parser.parse_args()
dic = vars(args)

os.system("head -60 Experiment > Experiment1")
os.system("rm Experiment; mv Experiment1 Experiment")

if args.Mode:
    with open('Experiment', 'r+') as exp:
     
        lines = exp.readlines()
    
    
     
    
        for i, line in enumerate(lines):
            for j,k in dic.items():
        
                
    
     
    
                if line.startswith(str(j)):
    
                    lines[i] = str(j)+'='+str(k)+'\n'
                
              
                exp.seek(0)
                
              
    
    
        for line in lines:
            exp.write(line)

with open('Experiment', 'r') as exp:
    
    lines = exp.readlines()
    dict_args = {i.split('=')[0]:i.split('=')[1].split('\n')[0] for i in lines if i != '\n'}

if args.Show: 
    # mode = [int(i) for i in dict_args['Mode']]
    # print(mode)
    # expt = daf.Control(*mode)
    mode = dict_args['Mode']+'00'
 
    
    print('')
    # print(f'Mode =      {str(expt.col1)+str(expt.col2)+str(expt.col3)+str(expt.col4)+str(expt.col5)}')
    print(f'Mode =      {mode[:5]}')
    print('')    

log = sys.argv.pop(0).split('command_line/')[1]        

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] =='True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")