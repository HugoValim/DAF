#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.utils import dafutilities as du
from daf.command_line.move.move_utils import MoveBase


class HKLMove(MoveBase):
    DESC = """Move in the reciprocal space by giving a HKL"""
    EPI = """
    Eg:
        daf.mv 1 1 1
        daf.mv 1 0 0 -q
        daf.mv 1 1 1 -m '*' -cm 'I' -s 16

        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "hkl-position",
            metavar="H K L",
            type=float,
            nargs=3,
            help="H, K, L position to be moved",
        )
        self.parser.add_argument(
            "-q", "--quiet", action="store_true", help="do not show the full output"
        )
        self.parser.add_argument(
            "-m",
            "--marker",
            type=str,
            help="marker to be used in the print",
            default="",
        )
        self.parser.add_argument(
            "-cm",
            "--column-marker",
            type=str,
            help="column marker to be used in the print",
            default="",
        )
        self.parser.add_argument(
            "-s",
            "--size",
            type=int,
            help="size of the print, default is 14",
            default=14,
        )

        args = self.parser.parse_args()
        return args

    def write_angles_if_small_error(self, error: float) -> None:
        """Writes to .Experiment file if the minimization was successful"""
        if float(error) > 1e-4:
            print("Can't find the HKL {}".format(args.Move))
            return
        exp_dict = self.get_angles_from_calculated_exp()
        self.update_experiment_file(exp_dict)
        self.write_to_experiment_file(exp_dict, is_motor_set_point=True)

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        error = self.calculate_hkl(self.parsed_args_dict["hkl-position"])
        if not self.parsed_args_dict["quiet"]:
            self.exp.set_print_options(
                marker=self.parsed_args_dict["marker"],
                column_marker=self.parsed_args_dict["column_marker"],
                space=self.parsed_args_dict["size"],
            )
            print(self.exp)
        self.write_angles_if_small_error(error)


@daf_log
def main() -> None:
    obj = HKLMove()
    obj.run_cmd()


if __name__ == "__main__":
    main()
