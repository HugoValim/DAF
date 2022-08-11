#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.log import daf_log
from daf.command_line.move.move_utils import MoveBase


class AngleMove(MoveBase):
    DESC = """Move the diffractometer by direct change in the angles"""

    EPI = """
    Eg:
        daf.amv --Del 30 --Eta 15
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
        self.parser.add_argument(
            "-co",
            "--counter",
            metavar="counter",
            type=str,
            help="Choose the counter to be used",
        )
        args = self.parser.parse_args()
        return args

    def write_angles(self, parsed_args_dict: dict) -> dict:
        """Write the passed angle arguments"""
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

    def run_cmd(self, arguments) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        motor_dict = self.write_angles(arguments)
        pseudo_dict = self.get_pseudo_angles_from_motor_angles()
        motor_dict.update(pseudo_dict)  #  Concatenate both dictionaries
        self.write_to_experiment_file(motor_dict)


@daf_log
def main() -> None:
    obj = AngleMove()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
