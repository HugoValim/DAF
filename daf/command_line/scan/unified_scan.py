#!/usr/bin/env python3
"""Unified motor scan command replacing ascans/dscans."""

import argparse as ap
import sys

from daf.utils.decorators import cli_decorator
from daf.command_line.cli_base_utils import CLIBase
from daf.command_line.scan.daf_scan_utils import ScanBase


class UnifiedScan(ScanBase):
    """Single CLI command for absolute/relative motor scans (1-6 motors)."""

    DESC = "Perform a scan in diffractometer motors"
    EPI = """
    Eg:
        daf.scan --type absolute --n-motors 1 --mu 1 10 100 .1
        daf.scan --type relative --n-motors 2 --mu -2 2 --eta -4 4 100 .1
        daf.scan --type absolute --n-motors 3 --mu 1 10 --eta 2 20 --chi 5 20 100 .1
    """

    def __init__(self) -> None:
        super().__init__(number_of_motors=None, scan_type=None)

    def parse_command_line(self) -> ap.Namespace:
        """Add --type, --n-motors, motor flags, and common scan arguments."""
        CLIBase.parse_command_line(self)
        self.parser.add_argument(
            "--type",
            choices=["absolute", "relative"],
            required=True,
            help="Scan type: absolute or relative",
        )
        self.parser.add_argument(
            "--n-motors",
            type=int,
            choices=[1, 2, 3, 4, 5, 6],
            required=True,
            help="Number of motors to scan (1-6)",
        )
        for motor in self.experiment_file_dict["motors"].keys():
            self.parser.add_argument(
                "-" + self.experiment_file_dict["motors"][motor]["cli_abbrev"],
                "--" + motor,
                metavar=("start", "end"),
                type=float,
                nargs=2,
                help="Start and end for {}".format(motor),
            )
        self.common_cli_scan_arguments()
        args = self.parser.parse_args()

        self.number_of_motors = args.n_motors
        self.scan_type = args.type

        inputed_motors = self.get_inputed_motor_order(sys.argv)
        if len(inputed_motors) != self.number_of_motors:
            self.parser.error(
                "Expected {} motors, got {}: {}".format(
                    self.number_of_motors, len(inputed_motors), inputed_motors
                )
            )

        return args

    def run_cmd(self) -> None:
        """Execute the configured scan."""
        self.run_scan()


@cli_decorator
def main() -> None:
    obj = UnifiedScan()
    obj.run_cmd()
