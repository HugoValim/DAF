#!/usr/bin/env python3

import argparse as ap
import sys
import os
from os import path
import yaml
import subprocess

from daf.command_line.support.support_utils import SupportBase
import daf.utils.generate_daf_default as gdd
from daf.utils import dafutilities as du
from daf.utils.daf_paths import DAFPaths as dp
from daf.utils.decorators import cli_decorator
from daf.utils.build_container import run_container


class Init(SupportBase):
    DESC = """Initialize Diffractometer Angles Finder"""
    EPI = """
    Eg:
       daf.init -s
       daf.init -a
        """
    DEFAULT_COUNTERS = [
        "ring_current",
    ]

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.initialize_experiment_file()
        self.build_user_config()
        self.build_daf_base_config()
        self.io = du.DAFIO(read=False)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "-s",
            "--simulated",
            action="store_true",
            help="initiate DAF in simulated mode",
        )
        self.parser.add_argument(
            "-a", "--all", action="store_true", help="initiate all DAF GUIs as well"
        )
        self.parser.add_argument(
            "-g",
            "--global",
            action="store_true",
            help="only initialize the global configuration",
        )
        self.parser.add_argument(
            "-k",
            "--kafka-topic",
            metavar="topic",
            type=str,
            help="kafka topic to be used in scans",
        )
        self.parser.add_argument(
            "-db",
            "--scan-db",
            metavar="topic",
            # default="temp",
            type=str,
            help="db name to be used in scans",
        )

        args = self.parser.parse_args()
        return args

    @staticmethod
    def initialize_experiment_file() -> None:
        """Build the .daf dir in the user home, also add the DAF default experiment file to it"""
        os.system('mkdir -p "{}"'.format(dp.DAF_CONFIGS))

    def build_user_config(self) -> None:
        """Build the scan-utils configuration"""
        os.system("mkdir -p {}".format(dp.SCAN_CONFIGS))
        gdd.generate_file(
            data=self.DEFAULT_COUNTERS,
            file_path=dp.SCAN_CONFIGS,
            file_name="config.daf_default.yml",
        )

    def build_daf_base_config(self):
        """Build the counter configuration file in the user's home configuration dir"""
        daf_default = []
        scan_utils_daf_default_path = path.join(
            dp.DAF_CONFIGS, "config.daf_default.yml"
        )
        self.write_yaml(daf_default, scan_utils_daf_default_path)

    def build_global_experiment_file(self):
        """Build the global configuration file if it is not built yet"""        
        if not os.path.isfile(dp.GLOBAL_EXPERIMENT_DEFAULT):
            data = self.build_current_file(self.parsed_args_dict["simulated"])
            self.write_to_disc(data, is_global=True, fetch_motors=False)

    @staticmethod
    def open_daf_guis() -> None:
        """If the --all option is passed open all DAF's GUIs as well"""
        subprocess.Popen("daf.gui; daf.live", shell=True)

    def run_cmd(self) -> None:
        if self.parsed_args_dict["simulated"]:
            run_container()
        data = self.build_current_file(self.parsed_args_dict["simulated"])
        self.write_to_disc(data, is_global=self.parsed_args_dict["global"])
        if self.parsed_args_dict["all"]:
            self.open_daf_guis()
        self.build_global_experiment_file()

@cli_decorator
def main() -> None:
    obj = Init()
    obj.run_cmd()


if __name__ == "__main__":
    main()
