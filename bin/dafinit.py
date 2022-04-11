#!/usr/bin/env python3
"""Initialize Diffractometer Angles Finder"""

import argparse as ap
import sys
import os
import yaml
import subprocess

epi = '''
Eg:
   daf.init -s
   daf.init -a
    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog = epi)
parser.add_argument('-s', '--simulated', action='store_true', help='Initiate DAF in simulated mode')
parser.add_argument('-a', '--all', action='store_true', help='Initiate all DAF GUIs as well')

args = parser.parse_args()
dic = vars(args)



os.system('cp -nr "{}/../resources/." "$HOME/.daf/"'.format(os.path.dirname(os.path.realpath(__file__))))
os.system('cp -n "$HOME/.daf/default" .Experiment')

import dafutilities as du
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

if args.all:
    # os.system('cp -n "$HOME/.daf/default" .Experiment')
    subprocess.Popen("daf.gui; daf.live", shell = True)
