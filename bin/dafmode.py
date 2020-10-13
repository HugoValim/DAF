#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import dafutilities as du

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
epi = '''
Eg:
    daf.mode 215, will set Nu fix, Alpha=Beta, Eta=Del/2
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog = epi)

parser.add_argument('Mode', type=str,help='Set the operation mode of the diffractometer, following the same modes as used in Spec, the mode should be passed without spaces')


args = parser.parse_args()
dic = vars(args)


dict_args = du.dict_conv()

with open('.Experiment', 'r+') as exp:  
 
    lines = exp.readlines()


 

    for i, line in enumerate(lines):
        for j,k in dic.items():
    
            

 

            if line.startswith(str(j)):

                lines[i] = str(j)+'='+str(k)+'\n'
            
          
            exp.seek(0)
            
          


    for line in lines:
            exp.write(line)




log = sys.argv.pop(0).split('command_line/')[1]        

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] =='True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")