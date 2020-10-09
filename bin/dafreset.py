#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os


doc = """

Reset experiment to default

"""

parser = ap.ArgumentParser(description=doc)

parser.add_argument('-a', '--All', action='store_true', help='Sets all inputs of the experiment to default')

args = parser.parse_args()
dic = vars(args)

os.system("head -60 Experiment > Experiment1")
os.system("rm Experiment; mv Experiment1 Experiment")
if args.All:
    os.system(f"rm Experiment")
    os.system(f"cp $EXP .")

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
        

with open('Experiment', 'r') as exp:
    
    lines = exp.readlines()
    dict_args = {i.split('=')[0]:i.split('=')[1].split('\n')[0] for i in lines if i != '\n'}  
       
log = sys.argv.pop(0).split('command_line/')[1]         

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")


