#!/usr/bin/env python3

import argparse as ap
import numpy as np
import yaml

from daf.utils.print_utils import TablePrinter
from daf.utils.print_utils import format_5_decimals
from daf.utils.decorators import cli_decorator
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

    _MOTOR_NAMES = ("mu", "eta", "chi", "phi", "nu", "del")

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
        """Set U matrix from a flat 9-element list."""
        U = np.array(u_list).reshape(3, 3)
        self.exp.set_U(U)
        UB = self.exp.calcUB()
        self.experiment_file_dict["U_mat"] = U.tolist()
        self.experiment_file_dict["UB_mat"] = UB.tolist()
        self.write_flag = True

    def set_ub_matrix(self, ub_list: list) -> None:
        """Set UB matrix from a flat 9-element list."""
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
        hkl = reflection[:3]
        motor_vals = [self.experiment_file_dict["motors"][m]["value"] for m in self._MOTOR_NAMES]
        ref_now = hkl + tuple(motor_vals) + (self.en,)
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

    def _build_matrix_dict(self, matrix: np.ndarray, label: str) -> list:
        """Build a dict row for TablePrinter from a 3x3 matrix."""
        fmt = "{:^11}"
        rows = []
        for i in range(3):
            ident = f"{label} = " if i == 1 else ""
            rows.append({
                "ident": ident,
                "col1": fmt.format(format_5_decimals(matrix[i][0])),
                "col2": fmt.format(format_5_decimals(matrix[i][1])),
                "col3": (fmt + "|").format(format_5_decimals(matrix[i][2])),
            })
        return rows

    def build_u_and_ub_print(self) -> tuple:
        """Build formatted strings for U and UB matrices."""
        U = np.array(self.experiment_file_dict["U_mat"])
        UB = np.array(self.experiment_file_dict["UB_mat"])
        fmt = [("", "ident", 9), ("", "col1", 12), ("", "col2", 12), ("", "col3", 12)]

        u_to_print = TablePrinter(fmt, ul="")(self._build_matrix_dict(U, "U"))
        ub_to_print = TablePrinter(fmt, ul="")(self._build_matrix_dict(UB, "UB"))
        return u_to_print, ub_to_print

    def list_stored_reflections(self) -> str:
        """List all stored reflections as a formatted table."""
        refs = self.experiment_file_dict["reflections"]
        center = "{:^11}"
        space = 10
        headers = ("Index", "H", "K", "L", "Mu", "Eta", "Chi", "Phi", "Nu", "Del", "Energy")
        fmt = [("", f"col{i+1}", space) for i in range(11)]

        data = [{"col1": center.format(headers[0]),
                 "col2": center.format(headers[1]),
                 "col3": center.format(headers[2]),
                 "col4": center.format(headers[3]),
                 "col5": center.format(headers[4]),
                 "col6": center.format(headers[5]),
                 "col7": center.format(headers[6]),
                 "col8": center.format(headers[7]),
                 "col9": center.format(headers[8]),
                 "col10": center.format(headers[9]),
                 "col11": center.format(headers[10])}]

        for i, ref in enumerate(refs):
            row = {"col1": center.format(str(i + 1))}
            for j in range(10):
                row[f"col{j+2}"] = center.format(str(ref[j]))
            data.append(row)

        return TablePrinter(fmt, ul="")(data)

    def print_calculated_lattice_parameters(self):
        """Print the LP calculated when doing a calculation from 3 reflections"""
        lp = self.experiment_file_dict
        for key in ("a", "b", "c", "alpha", "beta", "gama"):
            print(f"{key:5} = {lp[f'lparam_{key}']}")

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
        float_lp = [float(i) for i in calculated_lattice_parameters]
        self.experiment_file_dict["U_mat"] = U.tolist()
        self.experiment_file_dict["UB_mat"] = UB.tolist()
        lp_keys = ("lparam_a", "lparam_b", "lparam_c", "lparam_alpha", "lparam_beta", "lparam_gama")
        for key, val in zip(lp_keys, float_lp):
            self.experiment_file_dict[key] = val
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


@cli_decorator
def main() -> None:
    obj = SetUUB()
    obj.run_cmd()


if __name__ == "__main__":
    main()
