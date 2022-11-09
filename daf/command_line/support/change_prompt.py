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
    DESC = """Change the shell prompt to \"DAF>\" """
    EPI = """
    Eg:
       daf.prompt
        """

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        args = self.parser.parse_args()
        return args

    @staticmethod
    def change_prompt() -> None:
        """If the --all option is passed open all DAF's GUIs as well"""
        sys.ps1 = "DAF> "

    def run_cmd(self, arguments: dict) -> None:
        self.change_prompt()


@daf_log
def main() -> None:
    obj = Init()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
