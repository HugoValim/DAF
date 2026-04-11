#!/usr/bin/env python3


import argparse as ap

from daf.utils.print_utils import format_5_decimals
from daf.utils.decorators import cli_decorator
from daf.command_line.query.query_utils import QueryBase


class Where(QueryBase):
    """Class to show the current position, both in real and reciprocal space"""

    DESC = """Show current position in reciprocal space as well as all diffractometer's angles and pseudo-angles"""
    EPI = """
    Eg:
        daf.wh
            """

    _PSEUDO_NAMES = ("alpha", "beta", "psi", "tau", "qaz", "naz", "omega")
    _MOTOR_NAMES = ("del", "eta", "chi", "phi", "nu", "mu")

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()

        args = self.parser.parse_args()
        return args

    def print_position(self) -> None:
        """Print information about angles, pseudo-angles and HKL position based on the current .Experiment file"""
        self.hkl_now = list(self.calculate_hkl_from_angles())
        self.pseudo_dict_to_update = self.get_pseudo_angles_from_motor_angles()
        print("")
        print(
            "HKL now =   ",
            format_5_decimals(self.hkl_now[0]),
            format_5_decimals(self.hkl_now[1]),
            format_5_decimals(self.hkl_now[2]),
        )
        print("")
        for name in self._PSEUDO_NAMES:
            val = format_5_decimals(self.pseudo_dict_to_update[name])
            print(f"{name.capitalize():5}   =    {val}")
        print("")
        for name in self._MOTOR_NAMES:
            val = format_5_decimals(self.experiment_file_dict["motors"][name]["value"])
            print(f"{name.capitalize():4}     =    {val}")
        print("")

    def update_pseudo_angles_and_hkl(self):
        """Write calculated pseudo-angles and HKL to disk"""
        float_hkl = [float(i) for i in self.hkl_now]
        self.pseudo_dict_to_update["hklnow"] = float_hkl
        self.update_experiment_file(self.pseudo_dict_to_update)
        self.write_to_experiment_file(self.experiment_file_dict)

    def run_cmd(self) -> None:
        self.print_position()
        self.update_pseudo_angles_and_hkl()


@cli_decorator
def main() -> None:
    obj = Where()
    obj.run_cmd()


if __name__ == "__main__":
    main()
