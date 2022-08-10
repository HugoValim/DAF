#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.utils import dafutilities as du
from daf.command_line.move.move_utils import MoveBase


class RelAngleMove(MoveBase):
    DESC = """Move the diffractometer by direct change in the angles with relative movement"""

    EPI = """
    Eg:
        daf.ramv --Del 30 --Eta 15
        daf.ramv -d 30 -e 15
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-m",
            "--Mu",
            metavar="ang",
            type=float,
            help="sets Mu angle to a desired position",
        )
        self.parser.add_argument(
            "-e",
            "--Eta",
            metavar="ang",
            type=float,
            help="sets Eta angle to a desired position",
        )
        self.parser.add_argument(
            "-c",
            "--Chi",
            metavar="ang",
            type=float,
            help="sets Chi angle to a desired position",
        )
        self.parser.add_argument(
            "-p",
            "--Phi",
            metavar="ang",
            type=float,
            help="sets Phi angle to a desired position",
        )
        self.parser.add_argument(
            "-n",
            "--Nu",
            metavar="ang",
            type=float,
            help="sets Nu angle to a desired position",
        )
        self.parser.add_argument(
            "-d",
            "--Del",
            metavar="ang",
            type=float,
            help="sets Del angle to a desired position",
        )

        args = self.parser.parse_args()
        return args

    def write_angles(self, parsed_args_dict: dict) -> None:
        """Write the angles in a relative way"""
        mu_now = self.experiment_file_dict["motors"]["mu"]["value"]
        eta_now = self.experiment_file_dict["motors"]["eta"]["value"]
        chi_now = self.experiment_file_dict["motors"]["chi"]["value"]
        phi_now = self.experiment_file_dict["motors"]["phi"]["value"]
        nu_now = self.experiment_file_dict["motors"]["nu"]["value"]
        del_now = self.experiment_file_dict["motors"]["del"]["value"]
        motor_dict = {
            "Mu": mu_now,
            "Eta": eta_now,
            "Chi": chi_now,
            "Phi": phi_now,
            "Nu": nu_now,
            "Del": del_now,
        }
        motor_position_dict = {}
        for motor in parsed_args_dict.keys():
            if parsed_args_dict[motor] is not None:
                motor_position_dict[motor] = float(
                    motor_dict[motor] + parsed_args_dict[motor]
                )
        self.write_to_experiment_file(motor_position_dict)

    def run_cmd(self, arguments) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        self.write_angles(arguments)
        pseudo_dict = self.get_pseudo_angles_from_motor_angles()
        self.write_to_experiment_file(pseudo_dict)


@daf_log
def main() -> None:
    obj = RelAngleMove()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
