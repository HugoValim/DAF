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
   daf.mc -s default
   daf.mc -n new_config
   daf.mc -lc new_config
   daf.mc -r my_setup1 my_setup2 my_setup3
   daf.mc -rc new_config counter1 
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)
parser.add_argument('-s', '--set_default', metavar = 'config name', type=str, help='Set default counter file to be used in scans')
parser.add_argument('-n', '--new', metavar = 'config name', type=str, help='Create a new setup')
parser.add_argument('-r', '--remove', metavar = 'file', nargs = '*', help='Remove a setup')
parser.add_argument('-a', '--add_counter', metavar = 'counter', nargs = '*', help='Add a counter to a config file')
parser.add_argument('-rc', '--remove_counter', metavar = 'file', nargs = '*', help='Remove counters from a config file')
parser.add_argument('-l', '--list', action='store_true', help='List all setups, showing in which one you are')
parser.add_argument('-lc', '--list_counters', metavar = 'file', nargs = '*', help='List all setups, showing in which one you are')
parser.add_argument('-lac', '--list_all_counters', action='store_true', help='List all counters available')
parser.add_argument('-m', '--main-counter', metavar = 'counter', type=str, help='Set the main counter during a scan')

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()
du.log_macro(dict_args)
path = du.HOME + '/.config/scan-utils/'
sys_path = '/etc/xdg/scan-utils/'
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

if args.list:
    user_configs = os.listdir(du.HOME + '/.config/scan-utils')
    sys_configs = os.listdir('/etc/xdg/scan-utils')
    all_configs = user_configs + sys_configs
    configs = [i for i in all_configs if len(i.split('.')) == 3 and i.endswith('.yml')]
    configs.sort()
    for i in configs:
        print(i.split('.')[1])

if args.list_all_counters:
    with open('/etc/xdg/scan-utils/config.yml') as conf:
        config_data = yaml.safe_load(conf)
    counters = config_data['counters'].keys()
    for i in counters:
        print(i)   

if args.set_default:
    dict_args['default_counters'] = prefix + args.set_default + sufix
    du.write(dict_args)

if args.new:
    file_name = args.new
    os.system('touch $HOME/.config/scan-utils/{}'.format(prefix + file_name + sufix))

if isinstance (args.list_counters, list):
    file_name = args.list_counters[0]
    complete_file = prefix + file_name + sufix
    user_configs = os.listdir(path)
    sys_configs = os.listdir(sys_path)
    if complete_file in user_configs:
        path_to_use = path
    elif complete_file in sys_configs:
        path_to_use = sys_path

    data = read_yaml(filepath = path_to_use + complete_file)
    for counter in data:
        print(counter)

if args.add_counter:
    file_name = args.add_counter[0]
    complete_file = prefix + file_name + sufix
    user_configs = os.listdir(path)
    sys_configs = os.listdir(sys_path)
    if complete_file in user_configs:
        path_to_use = path
    elif complete_file in sys_configs:
        path_to_use = sys_path

    data = read_yaml(filepath = path_to_use + complete_file)

    if isinstance(data, list):
        for counter in args.add_counter[1:]:
            if counter not in data:
                data.append(counter)
        write_yaml(data, filepath = path_to_use + complete_file)
    else:
        list_ = []
        for counter in args.add_counter[1:]:
            if counter not in list_:
                list_.append(counter)
        write_yaml(list_, filepath = path_to_use + complete_file)

if args.remove_counter:
    file_name = args.remove_counter[0]
    complete_file = prefix + file_name + sufix
    user_configs = os.listdir(path)
    sys_configs = os.listdir(sys_path)
    if complete_file in user_configs:
        path_to_use = path
    elif complete_file in sys_configs:
        path_to_use = sys_path

    data = read_yaml(filepath = path_to_use + complete_file)
    
    if isinstance(data, list):
        for counter in args.remove_counter[1:]:
            if counter in data:
                data.remove(counter)

    write_yaml(data, filepath = path_to_use + complete_file)

if args.main_counter:
    dict_args['main_scan_counter'] = args.main_counter
    du.write(dict_args)


if args.remove:
    for file in args.remove:
        complete_file = prefix + file + sufix
        user_configs = os.listdir(path)
        sys_configs = os.listdir(sys_path)
        if complete_file in user_configs:
            path_to_use = path
        elif complete_file in sys_configs:
            path_to_use = sys_path
        os.system('rm -f "{}"'.format(path_to_use + complete_file))
