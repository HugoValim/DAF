#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os


doc = """

Initialize Diffractometer Angles Finder

"""

epi = '''
Eg: 
   daf.init -6c 
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog = epi)

parser.add_argument('-6c', '--6cirlce', action='store_true', help='Set the 6-cirlce diffractometer geometry')

args = parser.parse_args()
dic = vars(args)


os.system("cp $EXP \.Experiment")


log = sys.argv.pop(0).split('command_line/')[1]      

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

# if dict_args['macro_flag']:
#     os.system(f"echo {log} >> {dict_args['macro_name']}")