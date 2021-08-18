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
os.system('cp -n /etc/xdg/scan-utils/config.yml "$HOME/.config/scan-utils/config.yml"')
os.system('cp -n /etc/xdg/scan-utils/config.default.yml "$HOME/.config/scan-utils/config.config.daf_default.yml"')

path = du.HOME + '/.config/scan-utils/'
DEFAULT = path + 'config.yml'

def read_yaml(filepath = DEFAULT):
    with open(filepath) as file:
        data = yaml.safe_load(file)
        return data

def write_yaml(dict_, filepath=DEFAULT):
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)

debug_dict = {'debug1' : {'type' : 'real', 'pv' : 'SOL:S:m1', 'readback' : 'SOL:S:m1.RBV', 'description' : 'debug motor', 'tags' : 'debug'},
              'debug2' : {'type' : 'real', 'pv' : 'SOL:S:m2', 'readback' : 'SOL:S:m2.RBV', 'description' : 'debug motor', 'tags' : 'debug'},
              'debug3' : {'type' : 'real', 'pv' : 'SOL:S:m3', 'readback' : 'SOL:S:m3.RBV', 'description' : 'debug motor', 'tags' : 'debug'},
              'debug4' : {'type' : 'real', 'pv' : 'SOL:S:m4', 'readback' : 'SOL:S:m4.RBV', 'description' : 'debug motor', 'tags' : 'debug'},
              'debug5' : {'type' : 'real', 'pv' : 'SOL:S:m5', 'readback' : 'SOL:S:m5.RBV', 'description' : 'debug motor', 'tags' : 'debug'},
              'debug6' : {'type' : 'real', 'pv' : 'SOL:S:m6', 'readback' : 'SOL:S:m6.RBV', 'description' : 'debug motor', 'tags' : 'debug'}
}

config = read_yaml()

for key in debug_dict:
	config['motors'][key] = debug_dict[key]

write_yaml(config)


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

# if dict_args['macro_flag']:
#    os.system("echo {} >> {}".format(log, dict_args['macro_name']))
