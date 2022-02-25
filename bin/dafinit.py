#!/usr/bin/env python3
"""Initialize Diffractometer Angles Finder"""

import argparse as ap
import sys
import os
import dafutilities as du
import yaml

epi = '''
Eg:
   daf.init -6c
    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog = epi)
parser.add_argument('-s', '--simulated', action='store_true', help='Initiate DAF in simulated mode')

args = parser.parse_args()
dic = vars(args)


os.system('cp -nr "{}/../resources/." "$HOME/.daf/"'.format(os.path.dirname(os.path.realpath(__file__))))
os.system('cp -n "$HOME/.daf/default" .Experiment')
# os.system('export PS1="DAF> "')

dict_args = du.read()
du.log_macro(dict_args)

if args.simulated:
    dict_args['simulated'] = True
    du.write(dict_args)

if not os.path.isdir(du.HOME + '/.config/scan-utils'):
	os.system('mkdir $HOME/.config/scan-utils')
os.system('cp -n /etc/xdg/scan-utils/config.default.yml "$HOME/.config/scan-utils/config.config.daf_default.yml"')

path = du.HOME + '/.config/scan-utils/'
DEFAULT = path + 'config.yml'

def write_yaml(dict_, filepath=DEFAULT):
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)

daf_default = []
write_yaml(daf_default, path + 'config.daf_default.yml')
