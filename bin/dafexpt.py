#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os


doc = """

Describe the experiment inputs

"""

parser = ap.ArgumentParser(description=doc)

parser.add_argument('-m', '--Material', metavar='', type=str, help='Set the material that is going to be used in the experiment')
parser.add_argument('-i', '--IDir', metavar='', type=int, nargs=3,help='Set the plane paralel to the incident beam')
parser.add_argument('-n', '--NDir', metavar='', type=int, nargs=3,help='Set the plane perpendicular to the incident beam')
parser.add_argument('-s', '--Sampleor', metavar='', type=str,help='Set the sample orientation at the Phi axis')
parser.add_argument('-e', '--Energy', metavar='', type=float, help='Set the energy of the experiment, wavelength can also be given')
args = parser.parse_args()
dic = vars(args)


os.system("head -60 Experiment > Experiment1")
os.system("rm Experiment; mv Experiment1 Experiment")
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

with open('Experiment', 'r') as exp:
    
    lines = exp.readlines()
    dict_args = {i.split('=')[0]:i.split('=')[1].split('\n')[0] for i in lines if i != '\n'}      
        
log = sys.argv.pop(0).split('command_line/')[1]         

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")