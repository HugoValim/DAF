#!/usr/bin/env python3

import argparse as ap
import sys
import os
from os import path
import yaml
import subprocess

from daf.command_line.support.support_utils import SupportBase
import daf.utils.generate_daf_default as gdd
import daf.utils.daf_paths as dp
from daf.utils.log import daf_log


class Init(SupportBase):

    DESC = """Initialize Diffractometer Angles Finder"""
    EPI = """
    Eg:
       daf.init -s
       daf.init -a
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.initialize_experiment_file()
        self.build_user_config()
        self.build_daf_base_config()

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "-s",
            "--simulated",
            action="store_true",
            help="Initiate DAF in simulated mode",
        )
        self.parser.add_argument(
            "-a", "--all", action="store_true", help="Initiate all DAF GUIs as well"
        )

        args = self.parser.parse_args()
        return args

    @staticmethod
    def initialize_experiment_file() -> None:
        """Build the .daf dir in the user home, also add the DAF default experiment file to it"""
        os.system('mkdir -p "{}"'.format(dp.DAF_CONFIGS))
        gdd.generate_file(file_path=dp.DAF_CONFIGS, file_name="default.yml")

    @staticmethod
    def build_current_file(simulated: bool) -> None:
        """Create the .Experiment file in the current dir"""
        if simulated:
            data_sim = gdd.default
            data_sim["simulated"] = True
            gdd.generate_file(data=data_sim, file_name=".Experiment")
        else:
            gdd.generate_file(file_name=".Experiment")

    @staticmethod
    def build_user_config() -> None:
        """Build the scan-utils configuration"""
        os.system("mkdir -p $HOME/.config/scan-utils")
        # os.system('cp /etc/xdg/scan-utils/config.default.yml "$HOME/.config/scan-utils/config.daf_default.yml"')

    @staticmethod
    def write_yaml(dict_, file_path=None) -> None:
        """Method to write to a yaml file"""
        with open(file_path, "w") as file:
            yaml.dump(dict_, file)

    def build_daf_base_config(self):
        """Build the counter configuration file in the user's home configuration dir"""
        daf_default = []
        scan_utils_daf_default_path = path.join(
            dp.DAF_CONFIGS, "config.daf_default.yml"
        )
        self.write_yaml(daf_default, scan_utils_daf_default_path)

    @staticmethod
    def open_daf_guis() -> None:
        """If the --all option is passed open all DAF's GUIs as well"""
        subprocess.Popen("daf.gui; daf.live", shell=True)

    def run_cmd(self, arguments: dict) -> None:
        self.build_current_file(arguments["simulated"])
        if arguments["all"]:
            self.open_daf_guis()


@daf_log
def main() -> None:
    obj = Init()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
