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


class GUIAll(SupportBase):
    DESC = """Opens all DAF's GUIs"""
    EPI = """
    Eg:
       daf.guiall
        """

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        args = self.parser.parse_args()
        return args

    @staticmethod
    def open_daf_guis() -> int:
        """If the --all option is passed open all DAF's GUIs as well"""
        proc = subprocess.Popen("daf.gui; daf.live", shell=True)
        return proc.pid

    def run_cmd(self) -> None:
        self.open_daf_guis()


@daf_log
def main() -> None:
    obj = GUIAll()
    obj.run_cmd()


if __name__ == "__main__":
    main()
