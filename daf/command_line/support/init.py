#!/usr/bin/env python3
"""Initialize Diffractometer Angles Finder"""

import argparse as ap
import sys
import os
from os import path
import yaml
import subprocess

import daf.utils.dafutilities as du # This import has to be done here
import daf.utils.generate_daf_default as gdd
import daf.utils.daf_paths as dp
from daf.utils.log import daf_log

class Init:

    DESC = """Initialize Diffractometer Angles Finder"""
    EPI = '''
    Eg:
       daf.init -s
       daf.init -a
        '''

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.initialize_experiment_file()
        self.build_user_config()
        self.build_daf_base_config()
        self.run_user_required_options(self.parsed_args)
        daf_log()

    def parse_command_line(self):
        self.parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=self.DESC, epilog = self.EPI)
        self.parser.add_argument('-s', '--simulated', action='store_true', help='Initiate DAF in simulated mode')
        self.parser.add_argument('-a', '--all', action='store_true', help='Initiate all DAF GUIs as well')

        args = self.parser.parse_args()
        return args

    def initialize_experiment_file(self):
        os.system('mkdir -p "{}"'.format(dp.DAF_CONFIGS))
        gdd.generate_file(file_path=dp.DAF_CONFIGS, file_name="default.yml")
        

    def build_current_file(self, simulated):
        if simulated:
            data_sim = gdd.default
            data_sim["simulated"] = True
            gdd.generate_file(data=data_sim, file_name=".Experiment")
        else:
            gdd.generate_file(file_name=".Experiment")

    @staticmethod
    def build_user_config():
        os.system('mkdir -p $HOME/.config/scan-utils')
        os.system('cp /etc/xdg/scan-utils/config.default.yml "$HOME/.config/scan-utils/config.config.daf_default.yml"')

    @staticmethod
    def write_yaml(dict_, file_path = None):
        with open(file_path, "w") as file:
            yaml.dump(dict_, file)
    
    def build_daf_base_config(self):
        daf_default = []
        scan_utils_daf_default_path = path.join(dp.DAF_CONFIGS, 'config.daf_default.yml')
        self.write_yaml(daf_default, scan_utils_daf_default_path)

    @staticmethod
    def open_daf_guis():
        subprocess.Popen("daf.gui; daf.live", shell = True)

    def run_user_required_options(self, arguments):
        if arguments.simulated:
            simulated = True
        else:
            simulated = False
        self.build_current_file(simulated)
        if arguments.all:
            self.open_daf_guis()


if __name__ == "__main__":
    obj = Init()


            
