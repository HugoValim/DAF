#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.print_utils import TablePrinter
from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.command_line.query.query_utils import QueryBase


class Status(QueryBase):

    DESC = """Show the experiment status"""
    EPI = """
    Eg:
        daf.status -a
        daf.status -m
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
            "--mode",
            action="store_true",
            help="show current operating mode of the diffractometer",
        )
        self.parser.add_argument(
            "-e",
            "--experiment",
            action="store_true",
            help="show experiment information",
        )
        self.parser.add_argument(
            "-s", "--sample", action="store_true", help="show sample information"
        )
        self.parser.add_argument(
            "-u",
            "--umatrix",
            action="store_true",
            help="show current orientation matrix",
        )
        self.parser.add_argument(
            "-b", "--bounds", action="store_true", help="show current setted bounds"
        )
        self.parser.add_argument(
            "-a", "--all", action="store_true", help="show all information"
        )
        args = self.parser.parse_args()
        return args

    def show_mode(self):
        """Show only the current mode of operation"""
        mode = self.exp.show(sh="mode")
        print(mode)
        print("")
        return mode

    def show_expt(self):
        """Show sampleor, wave length, energy, idir, ndir, rdir"""
        mode = self.exp.show(sh="expt")
        print(mode)
        print("")
        return mode

    def show_sample(self):
        """Show information about the sample, name and lattice parameters"""
        mode = self.exp.show(sh="sample")
        print(mode)
        print("")
        return mode

    def show_u_and_ub(self):
        """Show current U and UB matrix"""
        U = np.array(self.experiment_file_dict["U_mat"])
        UB = np.array(self.experiment_file_dict["UB_mat"])
        center1 = "|{:^11}"
        center2 = "{:^11}"
        center3 = "{:^11}|"
        fmt1 = [
            ("", "ident", 9),
            ("", "col1", 12),
            ("", "col2", 12),
            ("", "col3", 12),
        ]

        data1 = [
            {
                "ident": "",
                "col1": center1.format(format_5_decimals(U[0][0])),
                "col2": center2.format(format_5_decimals(U[0][1])),
                "col3": center3.format(format_5_decimals(U[0][2])),
            },
            {
                "ident": "U    =   ",
                "col1": center1.format(format_5_decimals(U[1][0])),
                "col2": center2.format(format_5_decimals(U[1][1])),
                "col3": center3.format(format_5_decimals(U[1][2])),
            },
            {
                "ident": "",
                "col1": center1.format(format_5_decimals(U[2][0])),
                "col2": center2.format(format_5_decimals(U[2][1])),
                "col3": center3.format(format_5_decimals(U[2][2])),
            },
        ]

        data2 = [
            {
                "ident": "",
                "col1": center1.format(format_5_decimals(UB[0][0])),
                "col2": center2.format(format_5_decimals(UB[0][1])),
                "col3": center3.format(format_5_decimals(UB[0][2])),
            },
            {
                "ident": "UB   = ",
                "col1": center1.format(format_5_decimals(UB[1][0])),
                "col2": center2.format(format_5_decimals(UB[1][1])),
                "col3": center3.format(format_5_decimals(UB[1][2])),
            },
            {
                "ident": "",
                "col1": center1.format(format_5_decimals(UB[2][0])),
                "col2": center2.format(format_5_decimals(UB[2][1])),
                "col3": center3.format(format_5_decimals(UB[2][2])),
            },
        ]

        Utp = TablePrinter(fmt1, ul="")(data1)
        UBtp = TablePrinter(fmt1, ul="")(data2)

        print("")
        print(Utp)
        print("")
        print(UBtp)
        print("")

        return Utp, UBtp

    def show_bounds(self):
        """Show current motor bounds"""
        print("")
        print(
            "Mu    =    {}".format(self.experiment_file_dict["motors"]["mu"]["bounds"])
        )
        print(
            "Eta   =    {}".format(self.experiment_file_dict["motors"]["eta"]["bounds"])
        )
        print(
            "Chi   =    {}".format(self.experiment_file_dict["motors"]["chi"]["bounds"])
        )
        print(
            "Phi   =    {}".format(self.experiment_file_dict["motors"]["phi"]["bounds"])
        )
        print(
            "Nu    =    {}".format(self.experiment_file_dict["motors"]["nu"]["bounds"])
        )
        print(
            "Del   =    {}".format(self.experiment_file_dict["motors"]["del"]["bounds"])
        )
        print("")

    def show_all(self):
        """Show all information"""
        self.show_mode()
        self.show_expt()
        self.show_sample()
        self.show_u_and_ub()
        self.show_bounds()

    def run_cmd(self):
        """Method to print the user required information"""
        if self.parsed_args_dict["mode"]:
            self.show_mode()

        if self.parsed_args_dict["experiment"]:
            self.show_expt()

        if self.parsed_args_dict["sample"]:
            self.show_sample()

        if self.parsed_args_dict["umatrix"]:
            self.show_u_and_ub()

        if self.parsed_args_dict["bounds"]:
            self.show_bounds()

        if self.parsed_args_dict["all"]:
            self.show_all()


@daf_log
def main() -> None:
    obj = Status()
    obj.run_cmd()


if __name__ == "__main__":
    main()
