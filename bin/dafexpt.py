#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import dafutilities as du

doc = """

Describe the experiment inputs

"""
epi = '''
Eg: 
    daf.expt --Material Si --Energy 8000
    daf.expt -m Si -e 8000
    daf.expt -s x+ 
    daf.expt -i 1 0 0 -n 0 1 0    
    '''
    
parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog = epi)

parser.add_argument('-m', '--Material', metavar='samp', type=str, help='Sets the material that is going to be used in the experiment')
parser.add_argument('-i', '--IDir', metavar=('x', 'y', 'z'), type=int, nargs=3,help='Sets the plane paralel to the incident beam')
parser.add_argument('-n', '--NDir', metavar=('x', 'y', 'z'), type=int, nargs=3,help='Sets the plane perpendicular to the incident beam')
parser.add_argument('-s', '--Sampleor', metavar='or', type=str,help='Sets the sample orientation at Phi axis')
parser.add_argument('-e', '--Energy', metavar='en', type=float, help='Sets the energy of the experiment (KeV), wavelength can also be given (\u212B)')
args = parser.parse_args()
dic = vars(args)



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

dict_args = du.dict_conv()
        
log = sys.argv.pop(0).split('command_line/')[1]         

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")