#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import dafutilities as du

doc = """

Creates a macro for run many commands from a txt file

"""

parser = ap.ArgumentParser(description=doc)
parser.add_argument('-i', '--Initialize', action='store_true', help='Start recording your commands')
parser.add_argument('-s', '--Stop', action='store_true', help='Stop the macro')
parser.add_argument('-n', '--name', metavar='',type=str, help='Sets macro file name')
parser.add_argument('-e', '--Execute', metavar='',type=str, help='Execute a recorded macro')

args = parser.parse_args()
dic = vars(args)

dict_args = du.dict_conv()

if args.Initialize:

    os.system(f"echo '#!/usr/bin/env bash' > {args.name}")
    os.system(f"chmod 755 {args.name}")
    
    with open('Experiment', 'r+') as exp:
     
        lines = exp.readlines()
    
    
     
    
        for i, line in enumerate(lines):
            
                
    
     
    
            if line.startswith('macro_flag'):
                    lines[i] ='macro_flag=True\n'
            
            if line.startswith('macro_file'):
                    lines[i] ='macro_file='+args.name+'\n'
                    
          
            exp.seek(0)
            
          
    
    
        for line in lines:
            exp.write(line)
        
if args.Stop:
    
    with open('Experiment', 'r+') as exp:
     
        lines = exp.readlines()
    
    
     
    
        for i, line in enumerate(lines):
            
                
    
     
    
            if line.startswith('macro_flag'):
                    lines[i] ='macro_flag=False\n'
            
            if line.startswith('macro_file'):
                    lines[i] ='macro_file=macro'
                    
          
            exp.seek(0)
            
          
    
    
        for line in lines:
            exp.write(line)

if args.Execute:
    os.system(f"./{args.Execute}")

    
log = sys.argv.pop(0).split('command_line/')[1]         

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")