#!/usr/bin/env python3
"""Print a color-formatted overview of all DAF CLI commands."""

import argparse as ap

from daf.command_line.support.support_utils import SupportBase
from daf.utils.decorators import cli_decorator


# --------------------------------------------------------------------
# ANSI terminal colors (Linux/macOS compatible)
# --------------------------------------------------------------------
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


# Short alias matching the original module's usage
C = ShellColors
C.NONE = ShellColors.NO_COLOR


# --------------------------------------------------------------------
# Command registry — (category, color, cmd_name, description)
# --------------------------------------------------------------------
_COMMAND_GROUPS = (
    # (category_header, color, [(cmd, description), ...])
    (
        "SUPPORT",
        C.WHITE,
        (
            ("daf.init", "Initialize daf, creating the required files"),
            ("daf.reset", "Reset configurations to default"),
            ("daf.prompt", "Set daf prompt, must be used with source"),
            ("daf.setup", "Manage daf setups"),
            ("daf.newsample", "Create new folder and initialize daf in it"),
        ),
    ),
    (
        "GUIs",
        C.PURPLE,
        (
            ("daf.gui", "Launch daf's main GUI"),
            ("daf.live", "Launch daf's live plot"),
            ("daf.rmap", "Launch a graphical reciprocal space map"),
            ("daf.guiall", "Open all daf's GUIs"),
        ),
    ),
    (
        "CONFIGURE THE EXPERIMENT",
        C.GREEN,
        (
            ("daf.expt", "Set sample, energy and reference vectors"),
            ("daf.mode", "Set the mode of operation"),
            ("daf.bounds", "Set diffractometer angles bounds"),
            ("daf.cons", "Constrain angles and pseudo-angles during the experiment"),
            ("daf.ub", "Set or calculate UB matrix from 2 or 3 reflections"),
            ("daf.mc", "Manage counters to be used in scans"),
        ),
    ),
    (
        "QUERY INFORMATION",
        C.YELLOW,
        (
            ("daf.status", "Show the experiment status"),
            (
                "daf.wh",
                "Show the current position in reciprocal space, angles and pseudo-angles",
            ),
            (
                "daf.ca",
                "Calculate the diffractometer angles needed to reach a given HKL position",
            ),
        ),
    ),
    (
        "MOVE MOTORS",
        C.BLUE,
        (
            (
                "daf.amv",
                "Move the diffractometer motors by direct change in the angles",
            ),
            (
                "daf.ramv",
                "Move the diffractometer motors by a relative change in the angles",
            ),
            ("daf.mv", "Move in the reciprocal space by giving a HKL position"),
        ),
    ),
    (
        "SCANS",
        C.CYAN,
        (
            ("daf.scan", "Perform a scan in HKL coordinates"),
            ("daf.rfscan", "Perform a scan in HKL coordinates from a CSV file"),
            ("daf.tscan", "Perform an infinite time scan for the configured counters"),
            ("daf.ascan", "Perform an absolute scan in one diffractometer motor"),
            ("daf.a2scan", "Perform an absolute scan using two diffractometer motors"),
            (
                "daf.a3scan",
                "Perform an absolute scan using three diffractometer motors",
            ),
            ("daf.a4scan", "Perform an absolute scan using four diffractometer motors"),
            ("daf.a5scan", "Perform an absolute scan using five diffractometer motors"),
            ("daf.a6scan", "Perform an absolute scan using six diffractometer motors"),
            ("daf.lup", "Perform a relative scan in one diffractometer motor"),
            ("daf.dscan", "Perform a relative scan in one diffractometer motor"),
            ("daf.d2scan", "Perform a relative scan in two diffractometer motors"),
            ("daf.d3scan", "Perform a relative scan in three diffractometer motors"),
            ("daf.d4scan", "Perform a relative scan in four diffractometer motors"),
            ("daf.d5scan", "Perform a relative scan in five diffractometer motors"),
            ("daf.d6scan", "Perform a relative scan in six diffractometer motors"),
            ("daf.mesh", "Perform a mesh scan using two diffractometer motors"),
        ),
    ),
)


class CommandHelp(SupportBase):
    DESC = """Print an overview of all daf commands"""
    EPI = """
    Eg:
      daf.help
        """

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        return self.parser.parse_args()

    def _print_group(self, header: str, color: str, commands: tuple) -> None:
        """Print a single command group with colored header and command rows."""
        print()
        print(f"{color}{header}{C.NONE}")
        for cmd, desc in commands:
            print(f"{color}{cmd}{C.NONE} - {desc}")

    @staticmethod
    def print_all_commands() -> None:
        """Print all DAF CLI commands grouped by category."""
        for header, color, commands in _COMMAND_GROUPS:
            print()
            print(f"{color}{header}{C.NONE}")
            for cmd, desc in commands:
                print(f"{color}{cmd}{C.NONE} - {desc}")
        print()

    def run_cmd(self) -> None:
        self.print_all_commands()


@cli_decorator
def main() -> None:
    CommandHelp().run_cmd()


if __name__ == "__main__":
    main()
