#!/usr/bin/env python3
"""Manage counter configuration files"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import yaml
import dafutilities as du




epi = '''
Eg:
   daf.mc -c default
   daf.mc -s new_setup
   daf.mc -s
   daf.mc -r my_setup1 my_setup2 my_setup3
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-n', '--new', metavar = 'setup name', type=str, help='Create a new setup')
parser.add_argument('-r', '--remove', metavar = 'file', nargs = '*', help='Remove a setup')
parser.add_argument('-a', '--add_counter', metavar = 'counter', nargs = '*', help='Add a counter to a config file')
parser.add_argument('-rc', '--remove_counter', metavar = 'file', nargs = '*', help='Remove counters from a config file')
parser.add_argument('-l', '--list_counters', metavar = 'file', nargs = '*', help='List all setups, showing in which one you are')
parser.add_argument('-d', '--description', metavar = 'desc', nargs = 2, help='Add a description to this setup')

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()
path = du.HOME + '/.config/scan-utils/'
DEFAULT = path + 'config.yml'
prefix = 'config.'
sufix = '.yml'

def read_yaml(filepath = DEFAULT):
    with open(filepath) as file:
        data = yaml.safe_load(file)
        return data

def write_yaml(dict_, filepath=DEFAULT):
    with open(filepath, "w") as file:
        yaml.dump(dict_, file)

if args.new:
    file_name = args.new
    os.system('touch $HOME/.config/scan-utils/{}'.format(prefix + file_name + sufix))


if isinstance (args.list_counters, list):
    try:
        data = read_yaml(filepath = path + prefix + args.list_counters[0] + sufix)
        for counter in data:
            print(counter)
        
    except:
        data = read_yaml()
        for counter in data['counters'].keys():
            print(counter)

if args.add_counter:
    file_name = args.add_counter[0]
    data = read_yaml(filepath = path + prefix + file_name + sufix)
    
    if isinstance(data, list):
        for counter in args.add_counter[1:]:
            data.append(counter)

    write_yaml(data, filepath = path + prefix + file_name + sufix)

if args.remove_counter:
    file_name = args.remove_counter[0]
    data = read_yaml(filepath = path + prefix + file_name + sufix)
    
    if isinstance(data, list):
        for counter in args.remove_counter[1:]:
            data.remove(counter)

    write_yaml(data, filepath = path + prefix + file_name + sufix)

if args.remove:
    for file in args.remove:
        os.system('rm -f "$HOME/.config/scan-utils/{}"'.format(prefix + file + sufix))

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
