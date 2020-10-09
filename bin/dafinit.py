#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os


doc = """

Initialize Diffractometer Angles Finder

"""

parser = ap.ArgumentParser(description=doc)

parser.add_argument('-6c', '--6cirlce', action='store_true', help='Set the 6-cirlce diffractometer geometry')

args = parser.parse_args()
dic = vars(args)


os.system("cp $EXP .")

# with open('Experiment', 'r+') as exp:
 
#     lines = exp.readlines()


 

#     for i, line in enumerate(lines):
#         for j,k in dic.items():
            

 

#             if line.startswith(str(j)):
#                 if k != None:
#                     lines[i] = str(j)+'='+str(k)+'\n'
          
#             exp.seek(0)
            
          


#     for line in lines:
#         exp.write(line)
        
        
log = sys.argv.pop(0).split('command_line/')[1]      

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

# if dict_args['macro_flag']:
#     os.system(f"echo {log} >> {dict_args['macro_name']}")