#!/usr/bin/env python3
"""Create setups that helps the user to save their previou configuration configuration"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du




epi = '''
Eg:
   daf.setup -c default
   daf.setup -s new_setup
   daf.setup -s
   daf.setup -r my_setup1 my_setup2 my_setup3
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-n', '--new', metavar = 'setup name', type=str, help='Create a new setup')
parser.add_argument('-c', '--checkout', metavar = '[file]', type=str, help='Change current setup to another')
parser.add_argument('-s', '--save', metavar = 'file', nargs = '?', const = 'no_args', help='Save the current setup, if only -s is passed them de command will overwrite de current setup')
parser.add_argument('-r', '--remove', metavar = 'file', nargs = '*', help='Remove a setup')
parser.add_argument('-l', '--list', action='store_true', help='List all setups, showing in which one you are')
parser.add_argument('-d', '--description', metavar = 'desc', nargs = 2, help='Add a description to this setup')
parser.add_argument('-i', '--info', metavar = 'setup', type=str, help='Print detailed information about a specific setup')

args = parser.parse_args()
dic = vars(args)

if args.new:

    dict_args = du.read()
    setup_now = dict_args['setup']
    os.system('cat {}/../resources/default > $HOME/.daf/{}'.format(os.path.dirname(os.path.realpath(__file__)), args.new))


if args.checkout:
    
    dict_args = du.read()
    setup_now = dict_args['setup']


    # os.system('cp .Experiment "$HOME/.daf/{}"'.format(setup_now))
    os.system("cat /home/ABTLUS/hugo.campos/.daf/{} > .Experiment".format(args.checkout))

    dict_args = du.read()

    dict_args['setup'] = str(args.checkout)


    du.write(dict_args)



if args.save:
    
    dict_args = du.read()
    setup_now = dict_args['setup']
    
    if args.save == 'no_args':
        os.system('cp .Experiment "$HOME/.daf/{}"'.format(setup_now))

    else:

        os.system('cp .Experiment "$HOME/.daf/{}"'.format(args.save))


if args.list:

    dict_args = du.read()
    setup_now = dict_args['setup']

    os.system("ls -A1 --ignore=*.py $HOME/.daf/ | sed 's/^/   /' | sed '/   {}$/c >  {}' ".format(setup_now, setup_now))

if args.remove:

    dict_args = du.read()
    setup_now = dict_args['setup']
    
    for i in args.remove:
        if setup_now != i:
            os.system('rm -f "$HOME/.daf/{}"'.format(i))
        else:
            print('')
            print('Leave the setup before removing it')
            print('')

if args.description:

    if args.description[0] != ".":
        dict_args = du.read(filepath= du.HOME + '/.daf/' + args.description[0])
        dict_args['setup_desc'] = args.description[1]
        du.write(dict_args, filepath = du.HOME + '/.daf/' + args.description[0])

    else:
        dict_args = du.read()
        dict_args['setup_desc'] = args.description
        du.write(dict_args)


if args.info:

    dict_args = du.read()
    if dict_args['setup'] == args.info:
        desc = dict_args['setup_desc']
        print(desc)

    else:
        dict_args = du.read(filepath= du.HOME + '/.daf/' + args.info)
        desc = dict_args['setup_desc']
        print(desc)



log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
