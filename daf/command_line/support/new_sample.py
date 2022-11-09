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


class NewSample(SupportBase):
    DESC = """Creates a folder to a new sample and open all GUIs"""
    EPI = """
    Eg:
       daf.newsample
       daf.newsample -k
        """

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "folder_name",
            metavar=("folder"),
            type=str,
            help="folder name for the new sample, a full path mey be inputted",
        )
        self.parser.add_argument(
            "-k",
            "--kill",
            action="store_true",
            help="kill other running DAF GUIs",
        )

        args = self.parser.parse_args()
        return args

    @staticmethod
    def create_and_initialize_new_sample_folder(folder_name: str) -> None:
        """Build the .daf dir in the user home, also add the DAF default experiment file to it"""
        os.mkdir(folder_name)
        os.chmod(folder_name, 0o777)
        os.chdir(folder_name)
        subprocess.Popen("daf.init -a", shell=True)

    @staticmethod
    def kill_other_guis() -> None:
        """If the --all option is passed open all DAF's GUIs as well"""
        subprocess.Popen(
            "ps axu | grep daf_gui.py | awk {'print $2'} | head -n -1 | xargs kill -9",
            shell=True,
        )
        subprocess.Popen(
            "ps axu | grep live_view.py | awk {'print $2'} | head -n -1 | xargs kill -9",
            shell=True,
        )

    def run_cmd(self) -> None:
        self.create_and_initialize_new_sample_folder(
            self.parsed_args_dict["folder_name"]
        )
        if self.parsed_args_dict["kill"]:
            self.kill_other_guis()


@daf_log
def main() -> None:
    obj = NewSample()
    obj.run_cmd()


if __name__ == "__main__":
    main()
