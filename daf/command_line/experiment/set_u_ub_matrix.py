#!/usr/bin/env python3

import argparse as ap
import numpy as np
import yaml

from daf.utils.print_utils import TablePrinter
from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.utils import dafutilities as du
from daf.utils import daf_paths as dp
from daf.command_line.experiment.experiment_utils import ExperimentBase


class SetUUB(ExperimentBase):
    DESC = """Defines UB matrix and Calculate UB matrix from 2 or 3 reflections"""
    EPI = """
    Eg:
        daf.ub -r 1 0 0 0 5.28232 0 2 0 10.5647
        daf.ub -r 0 1 0 0 5.28232 2 92 0 10.5647
        daf.ub -c2 1 2
        daf.ub -c3 1 2 3
        daf.ub -U 1 0 0 0 1 0 0 0 1
        daf.ub -s
        daf.ub -s -p
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()
        self.write_flag = False

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-r",
            "--reflection",
            metavar=("H", "K", "L", "Mu", "Eta", "Chi", "Phi", "Nu", "Del"),
            type=float,
            nargs=9,
            help="HKL and angles for this reflection",
        )
        self.parser.add_argument(
            "-rn",
            "--reflection-now",
            metavar=("H", "K", "L"),
            type=float,
            nargs=3,
            help="store the current motor position with the given HKL",
        )
        self.parser.add_argument(
            "-u",
            "--u_matrix",
            metavar=("a11", "a12", "a13", "a21", "a22", "a23", "a31", "a32", "a33"),
            type=float,
            nargs=9,
            help="sets U matrix",
        )
        self.parser.add_argument(
            "-ub",
            "--ub_matrix",
            metavar=("a11", "a12", "a13", "a21", "a22", "a23", "a31", "a32", "a33"),
            type=float,
            nargs=9,
            help="sets UB matrix",
        )
        self.parser.add_argument(
            "-c2",
            "--calc_from_2_reflections",
            metavar=("R1", "R2"),
            type=int,
            nargs=2,
            help="calculate UB for 2 reflections, user must give the reflections that will be used",
        )
        self.parser.add_argument(
            "-c3",
            "--calc_from_3_reflections",
            metavar=("R1", "R2", "R3"),
            type=int,
            nargs=3,
            help="calculate UB for 3 reflections, user must give the reflections that will be used",
        )
        self.parser.add_argument(
            "-f", "--fit", action="store_true", help="fit reflections"
        )
        self.parser.add_argument(
            "-cr",
            "--clear-reflections",
            metavar="index",
            nargs="*",
            type=int,
            help="clear reflections by index",
        )
        self.parser.add_argument(
            "-ca",
            "--clear-all",
            action="store_true",
            help="clear all stored reflections",
        )
        self.parser.add_argument(
            "-l", "--list", action="store_true", help="list stored reflections"
        )
        self.parser.add_argument(
            "-s", "--show", action="store_true", help="show U and UB"
        )
        self.parser.add_argument(
            "-p",
            "--params",
            action="store_true",
            help="lattice parameters if 3 reflection calculation had been done",
        )

        args = self.parser.parse_args()
        return args

    def set_u_matrix(self, u_list: list) -> None:
        """Set U matrix based in the user input"""
        U = np.array(u_list).reshape(3, 3)
        self.exp.set_U(U)
        UB = self.exp.calcUB()
        self.experiment_file_dict[
            "U_mat"
        ] = (
            U.tolist()
        )  # yaml doesn't handle numpy arrays well, so using python's list is a better choice
        self.experiment_file_dict[
            "UB_mat"
        ] = (
            UB.tolist()
        )  # yaml doesn't handle numpy arrays well, so using python's list is a better choice
        self.write_flag = True

    def set_ub_matrix(self, ub_list: list) -> None:
        """Set UB matrix based in the user input"""
        UB = np.array(ub_list).reshape(3, 3)
        self.experiment_file_dict["UB_mat"] = UB.tolist()
        self.write_flag = True

    def store_reflections(self, inputed_reflection: list) -> None:
        """Function to a store a reflection in the reflections list"""
        ref = self.experiment_file_dict["reflections"]
        inputed_reflection.append(self.en)
        ref.append(inputed_reflection)
        self.experiment_file_dict["reflections"] = ref
        self.write_flag = True

    def store_current_reflection(self, reflection: list) -> None:
        """Store the current reflection using the current diffractometer position. The user should pass the HKL"""
        ref = self.experiment_file_dict["reflections"]
        h = reflection[0]
        k = reflection[1]
        l = reflection[2]
        mu = self.experiment_file_dict["motors"]["mu"]["value"]
        eta = self.experiment_file_dict["motors"]["eta"]["value"]
        chi = self.experiment_file_dict["motors"]["chi"]["value"]
        phi = self.experiment_file_dict["motors"]["phi"]["value"]
        nu = self.experiment_file_dict["motors"]["nu"]["value"]
        delta = self.experiment_file_dict["motors"]["del"]["value"]
        ref_now = [h, k, l, mu, eta, chi, phi, nu, delta, self.en]
        ref.append(ref_now)
        self.experiment_file_dict["reflections"] = ref
        self.write_flag = True

    def clear_stored_reflection(self, index_list: list) -> None:
        """Remove a reflection from the list of reflections"""
        reflection_list = self.experiment_file_dict["reflections"]
        for idx in index_list:
            reflection_list.pop(idx - 1)
        self.experiment_file_dict["reflections"] = reflection_list
        self.write_flag = True

    def clear_all_stored_reflections(self):
        """Clear all stored reflections"""
        self.experiment_file_dict["reflections"] = []
        self.write_flag = True

    def build_u_and_ub_print(self) -> tuple:
        """Build a pretty print to U and UB matrix, return their strings to be printed"""
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

        dict_u_mat = [
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

        dict_ub_mat = [
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

        u_to_print = TablePrinter(fmt1, ul="")(dict_u_mat)
        ub_to_print = TablePrinter(fmt1, ul="")(dict_ub_mat)

        return u_to_print, ub_to_print

    def list_stored_reflections(self) -> str:
        """List all stored reflections, return the formatted table to print"""
        refs = self.experiment_file_dict["reflections"]
        center = "{:^11}"
        space = 10
        fmt = [
            ("", "col1", space),
            ("", "col2", space),
            ("", "col3", space),
            ("", "col4", space),
            ("", "col5", space),
            ("", "col6", space),
            ("", "col7", space),
            ("", "col8", space),
            ("", "col9", space),
            ("", "col10", space),
            ("", "col11", space),
        ]
        data = [
            {
                "col1": center.format("Index"),
                "col2": center.format("H"),
                "col3": center.format("K"),
                "col4": center.format("L"),
                "col5": center.format("Mu"),
                "col6": center.format("Eta"),
                "col7": center.format("Chi"),
                "col8": center.format("Phi"),
                "col9": center.format("Nu"),
                "col10": center.format("Del"),
                "col11": center.format("Energy"),
            }
        ]

        for i in range(len(refs)):
            dict_ = {
                "col1": center.format(str(i + 1)),
                "col2": center.format(str(refs[i][0])),
                "col3": center.format(str(refs[i][1])),
                "col4": center.format(str(refs[i][2])),
                "col5": center.format(str(refs[i][3])),
                "col6": center.format(str(refs[i][4])),
                "col7": center.format(str(refs[i][5])),
                "col8": center.format(str(refs[i][6])),
                "col9": center.format(str(refs[i][7])),
                "col10": center.format(str(refs[i][8])),
                "col11": center.format(str(refs[i][9])),
            }
            data.append(dict_)

        formatted_list = TablePrinter(fmt, ul="")(data)
        return formatted_list

    def print_calculated_lattice_parameters(self):
        """Print the LP calculated when doing a calculation from 3 reflections"""
        print("")
        print("a    =    {}".format(self.experiment_file_dict["lparam_a"]))
        print("b    =    {}".format(self.experiment_file_dict["lparam_b"]))
        print("c    =    {}".format(self.experiment_file_dict["lparam_c"]))
        print("alpha    =    {}".format(self.experiment_file_dict["lparam_alpha"]))
        print("beta    =    {}".format(self.experiment_file_dict["lparam_beta"]))
        print("gamma    =    {}".format(self.experiment_file_dict["lparam_gama"]))
        print("")

    def calculate_u_mat_from_2_reflections(
        self, idx_reflection_1: int, idx_reflection_2: int
    ) -> None:
        """Calculate U matrix from 2 reflection and write it"""
        refs = self.experiment_file_dict["reflections"]

        index_first_reflection = idx_reflection_1 - 1
        hkl1 = refs[index_first_reflection][:3]
        angs1 = refs[index_first_reflection][3:-1]

        index_second_reflection = idx_reflection_2 - 1
        hkl2 = refs[index_second_reflection][:3]
        angs2 = refs[index_second_reflection][3:-1]

        U, UB = self.exp.calc_U_2HKL(hkl1, angs1, hkl2, angs2)
        self.experiment_file_dict["U_mat"] = U.tolist()
        self.experiment_file_dict["UB_mat"] = UB.tolist()
        self.write_flag = True

    def calculate_u_mat_from_3_reflections(
        self, idx_reflection_1: int, idx_reflection_2: int, idx_reflection_3: int
    ) -> None:
        """Calculate U matrix from 3 reflection and write it"""
        refs = self.experiment_file_dict["reflections"]

        index_first_reflection = idx_reflection_1 - 1
        hkl1 = refs[index_first_reflection][:3]
        angs1 = refs[index_first_reflection][3:-1]
        e1 = refs[index_first_reflection][9]

        index_second_reflection = idx_reflection_2 - 1
        hkl2 = refs[index_second_reflection][:3]
        angs2 = refs[index_second_reflection][3:-1]
        e2 = refs[index_second_reflection][9]

        index_third_reflection = idx_reflection_3 - 1
        hkl3 = refs[index_third_reflection][:3]
        angs3 = refs[index_third_reflection][3:-1]
        e3 = refs[index_third_reflection][9]

        average_energy = (e1 + e2 + e3) / 3
        self.exp.set_exp_conditions(en=average_energy)
        U, UB, calculated_lattice_parameters = self.exp.calc_U_3HKL(
            hkl1, angs1, hkl2, angs2, hkl3, angs3
        )
        float_lp = [
            float(i) for i in calculated_lattice_parameters
        ]  # Problems when saving numpy64floats, better to use python's float
        self.experiment_file_dict["U_mat"] = U.tolist()
        self.experiment_file_dict["UB_mat"] = UB.tolist()
        self.experiment_file_dict["lparam_a"] = float_lp[0]
        self.experiment_file_dict["lparam_b"] = float_lp[1]
        self.experiment_file_dict["lparam_c"] = float_lp[2]
        self.experiment_file_dict["lparam_alpha"] = float_lp[3]
        self.experiment_file_dict["lparam_beta"] = float_lp[4]
        self.experiment_file_dict["lparam_gama"] = float_lp[5]
        self.write_flag = True

    def fit_u_matrix(self) -> None:
        """Do a fit using several reflections to calculate UB"""
        refs = self.experiment_file_dict["reflections"]
        U = np.array(self.experiment_file_dict["U_mat"])
        fitted = self.exp.fit_u_matrix(U, refs)
        formated_fitted = [[float(format_5_decimals(i)) for i in j] for j in fitted]
        print(np.array(formated_fitted))
        self.experiment_file_dict["U_mat"] = U.tolist()
        # self.experiment_file_dict['UB_mat'] = UB.tolist()
        self.write_flag = True

    def run_cmd(self) -> None:
        """Method to be defined by each subclass, this is the method
        that should be run when calling the cli interface"""
        if self.parsed_args_dict["u_matrix"]:
            self.set_u_matrix(self.parsed_args_dict["u_matrix"])
        if self.parsed_args_dict["ub_matrix"]:
            self.set_ub_matrix(self.parsed_args_dict["ub_matrix"])
        if self.parsed_args_dict["reflection"] is not None:
            self.store_reflections(self.parsed_args_dict["reflection"])
        if self.parsed_args_dict["reflection_now"] is not None:
            self.store_current_reflection(self.parsed_args_dict["reflection_now"])
        if self.parsed_args_dict["clear_reflections"] is not None:
            self.clear_stored_reflection(self.parsed_args_dict["clear_reflections"])
        if self.parsed_args_dict["clear_all"]:
            self.clear_all_stored_reflections()
        if self.parsed_args_dict["calc_from_2_reflections"] is not None:
            self.calculate_u_mat_from_2_reflections(
                self.parsed_args_dict["calc_from_2_reflections"][0],
                self.parsed_args_dict["calc_from_2_reflections"][1],
            )
        if self.parsed_args_dict["calc_from_3_reflections"] is not None:
            self.calculate_u_mat_from_3_reflections(
                self.parsed_args_dict["calc_from_3_reflections"][0],
                self.parsed_args_dict["calc_from_3_reflections"][1],
                self.parsed_args_dict["calc_from_3_reflections"][2],
            )
        if self.parsed_args_dict["fit"]:
            self.fit_u_matrix()
        if self.parsed_args_dict["show"]:
            u_to_print, ub_to_print = self.build_u_and_ub_print()
            print("{} \n \n {} \n".format(u_to_print, ub_to_print))
        if self.parsed_args_dict["list"]:
            fomatted_table = self.list_stored_reflections()
            print("{} \n".format(fomatted_table))
        if self.parsed_args_dict["params"]:
            self.print_calculated_lattice_parameters()
        if self.write_flag:
            self.write_to_experiment_file(self.experiment_file_dict)


@daf_log
def main() -> None:
    obj = SetUUB()
    obj.run_cmd()


if __name__ == "__main__":
    main()
