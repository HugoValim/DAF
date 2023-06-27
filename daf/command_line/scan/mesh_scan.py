#!/usr/bin/env python3

import sys

from daf.utils.decorators import cli_decorator
from daf.command_line.scan.daf_scan_utils import ScanBase
from daf.command_line.cli_base_utils import CLIBase


class MeshScan(ScanBase):

    DESC = """Perform a mesh scan using two of the diffractometer motors"""
    EPI = """
    Eg:
        daf.mesh -e -2 2 -d -2 6 100 .1
        daf.mesh -e -2 2 -d -2 6 100 .1 -np

        """

    def __init__(self):
        super().__init__(number_of_motors=1, scan_type="grid_scan")

    def parse_command_line(self):
        """The majority of the scans use this, but some not and have to overwrite this method"""
        CLIBase.parse_command_line(self)
        for motor in self.experiment_file_dict["motors"].keys():
            self.parser.add_argument(
                "-" + self.experiment_file_dict["motors"][motor]["cli_abbrev"],
                "--" + motor,
                metavar=("start", "end", "step"),
                type=float,
                nargs=3,
                help="Start and end for {}".format(motor),
            )
        self.common_cli_scan_arguments(step=False)
        args = self.parser.parse_args()
        return args

    def configure_scan_input(self):
        convert_last_element_to_int = lambda x: x[:-1] + [int(x[-1])]
        scan_data = {
            motor: convert_last_element_to_int(self.parsed_args_dict[motor])
            for motor in self.inputed_motors
        }
        scan_inputs = [
            scan_data,
            self.inputed_motors,
            self.experiment_file_dict["motors"],
            self.scan_type,
        ]
        return scan_inputs

    def run_cmd(self):
        """Method to print the user required information"""
        self.run_scan()


@cli_decorator
def main() -> None:
    obj = MeshScan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
