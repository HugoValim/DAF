#!/usr/bin/env python3

import os

import argparse as ap

from daf.command_line.support.support_utils import SupportBase
import daf.utils.generate_daf_default as gdd
import daf.utils.daf_paths as dp
from daf.utils.log import daf_log


class Reset(SupportBase):

    DESC = """Reset experiment to default"""
    EPI = """
    Eg:
        daf.reset -a
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Sets all inputs of the experiment to default",
        )
        self.parser.add_argument(
            "--hard",
            action="store_true",
            help="If used deletes all setups before reseting them",
        )

        args = self.parser.parse_args()
        return args

    def soft_reset(self) -> None:
        """Reset only the current experiment file to default"""
        if self.experiment_file_dict["simulated"]:
            data_sim = gdd.default
            data_sim["simulated"] = True
            gdd.generate_file(data=data_sim, file_name=".Experiment")
        else:
            gdd.generate_file(file_name=".Experiment")

    def hard_reset(self) -> None:
        """Also remove all configuration files user home"""
        self.soft_reset()
        os.system('rm -fr "$HOME/.daf/"')

    def run_cmd(self) -> None:
        if self.parsed_args_dict["all"]:
            self.soft_reset()
        if self.parsed_args_dict["hard"]:
            self.hard_reset()


@daf_log
def main() -> None:
    obj = Reset()
    obj.run_cmd()


if __name__ == "__main__":
    main()
