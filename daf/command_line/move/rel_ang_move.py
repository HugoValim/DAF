#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.log import daf_log
from daf.command_line.move.move_utils import MoveBase


class RelAngleMove(MoveBase):
    DESC = """Move the diffractometer by direct change in the angles with relative movement"""

    EPI = """
    Eg:
        daf.ramv --del 30 --eta 15
        daf.ramv -d 30 -e 15
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()
        self.motor_inputs()
        args = self.parser.parse_args()
        return args

    def write_angles(self) -> dict:
        """Write the angles in a relative way"""
        mu_now = self.experiment_file_dict["motors"]["mu"]["value"]
        eta_now = self.experiment_file_dict["motors"]["eta"]["value"]
        chi_now = self.experiment_file_dict["motors"]["chi"]["value"]
        phi_now = self.experiment_file_dict["motors"]["phi"]["value"]
        nu_now = self.experiment_file_dict["motors"]["nu"]["value"]
        del_now = self.experiment_file_dict["motors"]["del"]["value"]
        motor_dict = {
            "mu": mu_now,
            "eta": eta_now,
            "chi": chi_now,
            "phi": phi_now,
            "nu": nu_now,
            "del": del_now,
        }
        motor_position_dict = {}
        for motor in self.parsed_args_dict.keys():
            if self.parsed_args_dict[motor] is not None:
                motor_position_dict[motor] = float(
                    motor_dict[motor] + float(self.parsed_args_dict[motor])
                )
        return motor_position_dict

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        motor_dict = self.write_angles()
        pseudo_dict = self.get_pseudo_angles_from_motor_angles()
        self.update_experiment_file(pseudo_dict)
        self.write_to_experiment_file(motor_dict, is_motor_set_point=True)


@daf_log
def main() -> None:
    obj = RelAngleMove()
    obj.run_cmd()


if __name__ == "__main__":
    main()
