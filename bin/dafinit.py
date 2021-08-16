#!/usr/bin/env python3
"""Initialize Diffractometer Angles Finder"""

import argparse as ap
import sys
import os



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
log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

# if dict_args['macro_flag']:
#    os.system("echo {} >> {}".format(log, dict_args['macro_name']))
