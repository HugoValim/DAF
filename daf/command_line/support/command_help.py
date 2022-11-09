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


class ShellColors:
    NO_COLOR = "\033[39;49m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class CommandHelp(SupportBase):
    DESC = """Print an overview of alldaf commands"""
    EPI = """
    Eg:
      daf.help
        """

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        args = self.parser.parse_args()
        return args

    @staticmethod
    def print_all_commands() -> None:
        """If the --all option is passed open alldaf's GUIs as well"""
        print()
        print("{}SUPPORT".format(ShellColors.WHITE))
        print(
            "{}daf.init{} - Initializedaf, creating the required files".format(
                ShellColors.WHITE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.reset{} - Reset configurations to default".format(
                ShellColors.WHITE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.prompt{} - Setdaf prompt, must be used wth source".format(
                ShellColors.WHITE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.setup{} - Managedaf setups".format(
                ShellColors.WHITE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.newsample{} - Create new folder and initializedaf in it".format(
                ShellColors.WHITE, ShellColors.NO_COLOR
            )
        )
        print()
        print("{}GUIs".format(ShellColors.PURPLE))
        print(
            "{}daf.gui{} - Launchdaf's main GUI".format(
                ShellColors.PURPLE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.live{} - Launchdaf's live plot".format(
                ShellColors.PURPLE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.rmap{} - Lanch a graphical resciprocal space map".format(
                ShellColors.PURPLE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.guiall{} - Opens alldaf's GUIs".format(
                ShellColors.PURPLE, ShellColors.NO_COLOR
            )
        )
        print()
        print("{}CONFIGURE THE EXPERIMENT".format(ShellColors.GREEN))
        print(
            "{}daf.expt{} - Set sample, energy and reference vectors".format(
                ShellColors.GREEN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.mode{} - Set the mode of operation".format(
                ShellColors.GREEN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.bounds{} - Set diffractometer angles bounds".format(
                ShellColors.GREEN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.cons{} - Function to constrain angles and pseudo-angles during the experiment".format(
                ShellColors.GREEN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.ub{} - Set or calculate UB matrix from 2 or 3 reflections".format(
                ShellColors.GREEN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.mc{} - Manage counters to be used in scans".format(
                ShellColors.GREEN, ShellColors.NO_COLOR
            )
        )
        print()
        print("{}QUERY INFORMATION".format(ShellColors.YELLOW, ShellColors.NO_COLOR))
        print(
            "{}daf.status{} - Show the experiment status".format(
                ShellColors.YELLOW, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.wh{} - Show the current position in the reciprocal space, angles and pseudo-angles".format(
                ShellColors.YELLOW, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.ca{} - Calculate the diffractometer angles needed to reach a given HKL position".format(
                ShellColors.YELLOW, ShellColors.NO_COLOR
            )
        )
        print()
        print("{}MOVE MOTORS".format(ShellColors.BLUE, ShellColors.NO_COLOR))
        print(
            "{}daf.amv{} - Move the diffractometer motors by direct change in the angles".format(
                ShellColors.BLUE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.ramv{} - Move the diffractometer motors by a relative change in the angles".format(
                ShellColors.BLUE, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.mv{} - Move in the reciprocal space by giving a HKL position".format(
                ShellColors.BLUE, ShellColors.NO_COLOR
            )
        )
        print()
        print("{}SCANS".format(ShellColors.CYAN, ShellColors.NO_COLOR))
        print(
            "{}daf.scan{} - Perform a scan in HKL coordinates".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.rfscan{} - Perform a scan in HKL coordinates by providing a csv file generated bydaf.scan".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.tscan{} - Perform an infinite time scan for the configured counters".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.ascan{} - Perform an absolute scan in one of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.a2scan{} - Perform an absolute scan using two of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.a3scan{} - Perform an absolute scan using three of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.a4scan{} - Perform an absolute scan using four of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.a5scan{} - Perform an absolute scan using five of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.a6scan{} - Perform an absolute scan using six of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.lup{} - Perform an relative scan in one of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.dscan{} - Perform an relative scan in one of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.d2scan{} - Perform an relative scan in two of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.d3scan{} - Perform an relative scan in three of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.d4scan{} - Perform an relative scan in four of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.d5scan{} - Perform an relative scan in five of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.d6scan{} - Perform an relative scan in six of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print(
            "{}daf.mesh{} - Perform a mesh scan using two of the diffractometer motors".format(
                ShellColors.CYAN, ShellColors.NO_COLOR
            )
        )
        print()

    def run_cmd(self) -> None:
        self.print_all_commands()


@daf_log
def main() -> None:
    obj = CommandHelp()
    obj.run_cmd()


if __name__ == "__main__":
    main()
