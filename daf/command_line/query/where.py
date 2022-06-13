#!/usr/bin/env python3


import argparse as ap

from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.command_line.query.query_utils import QueryBase


class Where(QueryBase):
    """Class to show the current position, both in real and reciprocal space"""

    DESC = """Show current position in reciprocal space as well as all diffractometer's angles and pseudo-angles"""
    EPI = """
    Eg:
        daf.wh
            """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()

        args = self.parser.parse_args()
        return args

    def calc_hkl(self, exp_file_dict: dict) -> list:
        """Calculate the current HKL position based in the .Experiment file information"""
        hkl_now = self.exp.calc_from_angs(
            exp_file_dict["Mu"],
            exp_file_dict["Eta"],
            exp_file_dict["Chi"],
            exp_file_dict["Phi"],
            exp_file_dict["Nu"],
            exp_file_dict["Del"],
        )
        return list(hkl_now)

    def print_position(self, exp_file_dict: dict) -> None:
        """Print information about angles, pseudo-angles and HKL position based on the current .Experiment file"""
        hkl_now = self.calc_hkl(exp_file_dict)
        print("")
        print(
            "HKL now =   ",
            format_5_decimals(hkl_now[0]),
            format_5_decimals(hkl_now[1]),
            format_5_decimals(hkl_now[2]),
        )
        print("")
        print("Alpha   =    {}".format(format_5_decimals(exp_file_dict["alpha"])))
        print("Beta    =    {}".format(format_5_decimals(exp_file_dict["beta"])))
        print("Psi     =    {}".format(format_5_decimals(exp_file_dict["psi"])))
        print("Tau     =    {}".format(format_5_decimals(exp_file_dict["tau"])))
        print("Qaz     =    {}".format(format_5_decimals(exp_file_dict["qaz"])))
        print("Naz     =    {}".format(format_5_decimals(exp_file_dict["naz"])))
        print("Omega   =    {}".format(format_5_decimals(exp_file_dict["omega"])))
        print("")
        print("Del     =    {}".format(format_5_decimals(exp_file_dict["Del"])))
        print("Eta     =    {}".format(format_5_decimals(exp_file_dict["Eta"])))
        print("Chi     =    {}".format(format_5_decimals(exp_file_dict["Chi"])))
        print("Phi     =    {}".format(format_5_decimals(exp_file_dict["Phi"])))
        print("Nu      =    {}".format(format_5_decimals(exp_file_dict["Nu"])))
        print("Mu      =    {}".format(format_5_decimals(exp_file_dict["Mu"])))
        print("")

    def run_cmd(self, arguments: dict) -> None:
        self.print_position(self.experiment_file_dict)


@daf_log
def main() -> None:
    obj = Where()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
