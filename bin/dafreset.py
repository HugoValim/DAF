#!/usr/bin/env python3
"""Reset experiment to default"""

import argparse as ap
import sys
import os
# import dafutilities as du

epi = '''
Eg:
    daf.reset -a
    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog = epi)
parser.add_argument('-a', '--All', action='store_true', help='Sets all inputs of the experiment to default')
parser.add_argument('--hard', action='store_true', help='If used deletes all setups before reseting them')

args = parser.parse_args()
dic = vars(args)

if args.All:
    if args.hard:
        os.system('rm -fr "$HOME/.daf/"')
    os.system('cp -r "{}/../resources/." "$HOME/.daf/"'.format(os.path.dirname(os.path.realpath(__file__))))
    os.system('cp "$HOME/.daf/default" .Experiment')

# dict_args = du.read()
# du.log_macro(dict_args)