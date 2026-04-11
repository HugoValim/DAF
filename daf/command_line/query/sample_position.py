#!/usr/bin/env python3


import argparse as ap

from daf.utils.print_utils import format_5_decimals
from daf.utils.decorators import cli_decorator
from daf.command_line.cli_base_utils import CLIBase


class SamplePos(CLIBase):
    """Class to show the current position, both in real and reciprocal space"""

    DESC = """Show current position in reciprocal space as well as all diffractometer's angles and pseudo-angles"""
    EPI = """
    Eg:
        daf.spos
            """

    _SAMPLE_MOTORS = (
        "sample_z", "sample_x", "sample_rx", "sample_y", "sample_ry",
        "sample_x_s1", "sample_y_s1", "diffractomer_ux", "diffractomer_uy",
        "diffractomer_rx", "theta_analyzer_crystal", "2theta_analyzer_crystal",
    )

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self):
        super().parse_command_line()

        args = self.parser.parse_args()
        return args

    def print_position(self) -> None:
        """Print information about angles, pseudo-angles and HKL position based on the current .Experiment file"""
        print("")
        for motor in self._SAMPLE_MOTORS:
            val = format_5_decimals(
                self.experiment_file_dict["motors"][motor]["value"]
            )
            print(f"{motor:26} =    {val}")
        print("")

    def run_cmd(self) -> None:
        self.print_position()


@cli_decorator
def main() -> None:
    obj = SamplePos()
    obj.run_cmd()


if __name__ == "__main__":
    main()
