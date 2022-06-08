#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.core.main import DAF
from daf.utils.print_utils import TablePrinter
from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
import daf.utils.dafutilities as du

class Status:

    DESC = """Show the experiment status"""
    EPI = """
    Eg:
        daf.status -a
        daf.status -m
        """

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.experiment_file_dict = du.read()
        self.exp = self.build_exp()

    def parse_command_line(self):
        self.parser = ap.ArgumentParser(
            formatter_class=ap.RawDescriptionHelpFormatter,
            description=self.DESC,
            epilog=self.EPI,
        )
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

    def build_exp(self):
        """Instantiate an instance of DAF main class setting all necessary parameters"""
        mode = [int(i) for i in self.experiment_file_dict["Mode"]]
        idir = self.experiment_file_dict["IDir_print"]
        ndir = self.experiment_file_dict["NDir_print"]
        rdir = self.experiment_file_dict["RDir"]
        Mu_bound = self.experiment_file_dict["bound_Mu"]
        Eta_bound = self.experiment_file_dict["bound_Eta"]
        Chi_bound = self.experiment_file_dict["bound_Chi"]
        Phi_bound = self.experiment_file_dict["bound_Phi"]
        Nu_bound = self.experiment_file_dict["bound_Nu"]
        Del_bound = self.experiment_file_dict["bound_Del"]

        exp = DAF(*mode)
        if (
            self.experiment_file_dict["Material"]
            in self.experiment_file_dict["user_samples"].keys()
        ):
            exp.set_material(
                self.experiment_file_dict["Material"],
                *self.experiment_file_dict["user_samples"][
                    self.experiment_file_dict["Material"]
                ]
            )
        else:
            exp.set_material(
                self.experiment_file_dict["Material"],
                self.experiment_file_dict["lparam_a"],
                self.experiment_file_dict["lparam_b"],
                self.experiment_file_dict["lparam_c"],
                self.experiment_file_dict["lparam_alpha"],
                self.experiment_file_dict["lparam_beta"],
                self.experiment_file_dict["lparam_gama"],
            )

        exp.set_exp_conditions(
            idir=idir,
            ndir=ndir,
            rdir=rdir,
            en=self.experiment_file_dict["PV_energy"]
            - self.experiment_file_dict["energy_offset"],
            sampleor=self.experiment_file_dict["Sampleor"],
        )
        exp.set_circle_constrain(
            Mu=Mu_bound,
            Eta=Eta_bound,
            Chi=Chi_bound,
            Phi=Phi_bound,
            Nu=Nu_bound,
            Del=Del_bound,
        )

        exp.set_constraints(
            Mu=self.experiment_file_dict["cons_Mu"],
            Eta=self.experiment_file_dict["cons_Eta"],
            Chi=self.experiment_file_dict["cons_Chi"],
            Phi=self.experiment_file_dict["cons_Phi"],
            Nu=self.experiment_file_dict["cons_Nu"],
            Del=self.experiment_file_dict["cons_Del"],
            alpha=self.experiment_file_dict["cons_alpha"],
            beta=self.experiment_file_dict["cons_beta"],
            psi=self.experiment_file_dict["cons_psi"],
            omega=self.experiment_file_dict["cons_omega"],
            qaz=self.experiment_file_dict["cons_qaz"],
            naz=self.experiment_file_dict["cons_naz"],
        )

        return exp

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
        print("Mu    =    {}".format(self.experiment_file_dict["bound_Mu"]))
        print("Eta   =    {}".format(self.experiment_file_dict["bound_Eta"]))
        print("Chi   =    {}".format(self.experiment_file_dict["bound_Chi"]))
        print("Phi   =    {}".format(self.experiment_file_dict["bound_Phi"]))
        print("Nu    =    {}".format(self.experiment_file_dict["bound_Nu"]))
        print("Del   =    {}".format(self.experiment_file_dict["bound_Del"]))
        print("")

    def show_all(self):
        """Show all information"""
        self.show_mode()
        self.show_expt()
        self.show_sample()
        self.show_u_and_ub()
        self.show_bounds()

    def run_cmd(self, arguments):
        """Method to print the user required information"""
        if arguments.mode:
            self.show_mode()

        if arguments.experiment:
            self.show_expt()

        if arguments.sample:
            self.show_sample()

        if arguments.umatrix:
            self.show_u_and_ub()

        if arguments.bounds:
            self.show_bounds()

        if arguments.all:
            self.show_all()


@daf_log
def main() -> None:
    obj = Status()
    obj.run_cmd(obj.parsed_args)


if __name__ == "__main__":
    main()


