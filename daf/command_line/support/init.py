#!/usr/bin/env python3
"""Initialize Diffractometer Angles Finder"""

import argparse as ap
import sys
import os
from os import path
import yaml
import subprocess

import daf.utils.dafutilities as du # This import has to be done here
import daf.utils.generate_daf_default as gf

class Init:

    DESC = """Initialize Diffractometer Angles Finder"""
    EPI = '''
    Eg:
       daf.init -s
       daf.init -a
        '''
    SCAN_UTILS_USER_PATH = du.HOME + '/.config/scan-utils/'
    DEFAULT_CONFIG = SCAN_UTILS_USER_PATH + 'config.yml'
    PATH_TO_DAF_CONFIG = du.HOME + "/.daf"

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.initialize_experiment_file()
        self.experiment_file_dict = self.get_experiment_file()
        self.build_user_config()
        self.build_daf_base_config()
        du.log_macro(self.experiment_file_dict)
        self.run_user_required_options(self.parsed_args)

    def parse_command_line(self):
        self.parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=self.DESC, epilog = self.EPI)
        self.parser.add_argument('-s', '--simulated', action='store_true', help='Initiate DAF in simulated mode')
        self.parser.add_argument('-a', '--all', action='store_true', help='Initiate all DAF GUIs as well')

        args = self.parser.parse_args()
        return args

    def initialize_experiment_file(self):
        os.system('mkdir -p "$HOME/.daf/"')
        gf.generate_default(self.PATH_TO_DAF_CONFIG + "/default")
        os.system('cp "$HOME/.daf/default" .Experiment')

    @staticmethod
    def get_experiment_file():
        dict_args = du.read()
        return dict_args
    
    
    def handle_simulated_option(self):
        self.experiment_file_dict['simulated'] = True
        du.write(self.experiment_file_dict)

    @staticmethod
    def build_user_config():
        os.system('mkdir -p $HOME/.config/scan-utils')
        os.system('cp /etc/xdg/scan-utils/config.default.yml "$HOME/.config/scan-utils/config.config.daf_default.yml"')

    @staticmethod
    def write_yaml(dict_, file_path = DEFAULT_CONFIG):
        with open(file_path, "w") as file:
            yaml.dump(dict_, file)
    
    def build_daf_base_config(self):
        daf_default = []
        self.write_yaml(daf_default, self.PATH_TO_DAF_CONFIG + 'config.daf_default.yml')

    @staticmethod
    def open_daf_guis():
        subprocess.Popen("daf.gui; daf.live", shell = True)

    def run_user_required_options(self, arguments):
        if arguments.simulated:
            self.handle_simulated_option()
        if arguments.all:
            self.open_daf_guis()

if __name__ == "__main__":
    obj = Init()


            
