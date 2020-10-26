#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



doc = """

Create setups that helps the user to save their previou configuration configuration

"""


epi = '''
Eg: 
   daf.setup -c default
   daf.setup -s new_setup
   daf.setup -s
   daf.setup -r my_setup1 my_setup2 my_setup3
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)


parser.add_argument('-c', '--change', metavar = '[file]', type=str, help='Change current setup to another')
parser.add_argument('-s', '--save', metavar = 'file', nargs = '?', const = 'no_args', help='Save the current setup, if only -s is passed them de command will overwrite de current setup')
parser.add_argument('-r', '--remove', metavar = 'file', nargs = '*', help='Remove a setup')
parser.add_argument('-l', '--list', action='store_true', help='List all setups, showing in which one you are')

args = parser.parse_args()
dic = vars(args)




if args.change:
    os.system(f"cat $EXPS/{args.change} > \.Experiment")

    with open('.Experiment', 'r+') as exp:
 
        lines = exp.readlines()


 

        for i, line in enumerate(lines):
                
    
     
    
            if line.startswith('setup'):
  
                lines[i] = 'setup='+str(args.change)+'\n'
              
                exp.seek(0)
                


 

        for line in lines:
            exp.write(line)


     


dict_args = du.dict_conv()
setup_now = dict_args['setup']

if args.save:
    if args.save == 'no_args':
        os.system(f"cat .Experiment > $EXPS/{setup_now}")
    
    else:
        
        os.system(f"cat .Experiment > $EXPS/{args.save}")



if args.list:
    os.system(f"ls -A1 $EXPS | sed 's/^/   /' | sed '/   {setup_now}$/c \u27A4  {setup_now}' ")

if args.remove:
    
    for i in args.remove:
        if setup_now != i: 
            os.system(f"rm $EXPS/{i}")
        else:
            print('')
            print('Leave the setup before removing it')
            print('')
    
    
    

log = sys.argv.pop(0).split('command_line/')[1]    

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")