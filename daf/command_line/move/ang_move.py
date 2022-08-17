#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.log import daf_log
from daf.command_line.move.move_utils import MoveBase


class AngleMove(MoveBase):
    DESC = """Move the diffractometer by direct change in the angles"""

    EPI = """
    Eg:
        daf.amv --del 30 --eta 15
        daf.amv -d 30 -e 15
        daf.amv -d CEN
        daf.amv -d MAX -co roi1
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()
        self.motor_inputs()
        self.parser.add_argument(
            "-co",
            "--counter",
            metavar="counter",
            type=str,
            help="choose the counter to be used when inputing CEN or MAX",
        )
        args = self.parser.parse_args()
        return args

    def write_angles(self, parsed_args_dict: dict) -> dict:
        """Write the passed angle self.parsed_args_dict"""
        dict_ = self.experiment_file_dict["scan_stats"]
        if dict_:
            if parsed_args_dict["counter"] is not None:
                CEN = dict_[parsed_args_dict["counter"]]["FWHM_at"]
                MAX = dict_[parsed_args_dict["counter"]]["peak_at"]
                stat_dict = {"CEN": CEN, "MAX": MAX}
            elif self.experiment_file_dict["main_scan_counter"]:
                CEN = dict_[self.experiment_file_dict["main_scan_counter"]]["FWHM_at"]
                MAX = dict_[self.experiment_file_dict["main_scan_counter"]]["peak_at"]
                stat_dict = {"CEN": CEN, "MAX": MAX}
            else:
                values_view = dict_.keys()
                value_iterator = iter(values_view)
                first_key = next(value_iterator)
                CEN = dict_[first_key]["FWHM_at"]
                MAX = dict_[first_key]["peak_at"]
                stat_dict = {"CEN": CEN, "MAX": MAX}

        dict_parsed_with_counter_stats = {
            key: (stat_dict[value] if (value == "CEN" or value == "MAX") else value)
            for key, value in parsed_args_dict.items()
        }
        return dict_parsed_with_counter_stats

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        motor_dict = self.write_angles(self.parsed_args_dict)
        pseudo_dict = self.get_pseudo_angles_from_motor_angles()
        self.update_experiment_file(pseudo_dict)
        self.write_to_experiment_file(motor_dict, is_motor_set_point=True)


@daf_log
def main() -> None:
    obj = AngleMove()
    obj.run_cmd()


if __name__ == "__main__":
    main()
