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

parser.add_argument('-6c', '--6cirlce', action='store_true', help='Set the 6-cirlce diffractometer geometry')

args = parser.parse_args()
dic = vars(args)


os.system('cp -nr "{}/../resources/." "$HOME/.daf/"'.format(os.path.dirname(os.path.realpath(__file__))))
os.system('cp -n "$HOME/.daf/default" .Experiment')

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

log = sys.argv.pop(0).split('command_line/')[1]
for i in sys.argv:
    log += ' ' + i
os.system("echo {} >> Log".format(log))
