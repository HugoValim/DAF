#!/usr/bin/env python3

import os

import argparse as ap

from daf.command_line.support.support_utils import SupportBase
import daf.utils.generate_daf_default as gdd
import daf.utils.daf_paths as dp
from daf.utils.decorators import cli_decorator


class Reset(SupportBase):

    DESC = """Reset experiment to default"""
    EPI = """
    Eg:
        daf.reset
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "-g",
            "--global",
            action="store_true",
            help="Force to reset the global file",
        )
        self.parser.add_argument(
            "--hard",
            action="store_true",
            help="if used, deletes all previous configuration",
        )

        args = self.parser.parse_args()
        return args

    def soft_reset(self) -> None:
        """Reset only the current experiment file to default"""
        data = self.build_current_file(
            self.experiment_file_dict["simulated"],
            self.experiment_file_dict["kafka_topic"],
            self.experiment_file_dict["scan_db"],
        )
        self.write_to_disc(
            data, fetch_motors=False, is_global=self.parsed_args_dict["global"]
        )

    def hard_reset(self) -> None:
        """Also remove all configuration files user home"""
        os.system('rm -fr "$HOME/.daf/"')

    def run_cmd(self) -> None:
        self.soft_reset()
        if self.parsed_args_dict["hard"]:
            self.hard_reset()


@cli_decorator
def main() -> None:
    obj = Reset()
    obj.run_cmd()


if __name__ == "__main__":
    main()
