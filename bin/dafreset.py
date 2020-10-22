#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import dafutilities as du

doc = """

Reset experiment to default

"""

epi = '''
Eg:
    daf.reset -a
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog = epi)

parser.add_argument('-a', '--All', action='store_true', help='Sets all inputs of the experiment to default')

args = parser.parse_args()
dic = vars(args)

if args.All:
    os.system(f"rm .Experiment")
    os.system(f"cp $EXP \.Experiment")
    os.system("cat $EXP > $EXPS/default ")

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
        

dict_args = du.dict_conv()
       
log = sys.argv.pop(0).split('command_line/')[1]         

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")


