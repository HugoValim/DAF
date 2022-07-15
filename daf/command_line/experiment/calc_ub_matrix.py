#!/usr/bin/env python3

import os
from os import path

import argparse as ap
import numpy as np
import yaml

from daf.utils.log import daf_log
from daf.utils import dafutilities as du
from daf.utils import daf_paths as dp
from daf.command_line.experiment.experiment_utils import ExperimentBase


class CalcUB(ExperimentBase):
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
            help="Store the current motor position with the given HKL",
        )
        self.parser.add_argument(
            "-U",
            "--Umatrix",
            metavar=("a11", "a12", "a13", "a21", "a22", "a23", "a31", "a32", "a33"),
            type=float,
            nargs=9,
            help="Sets U matrix",
        )
        self.parser.add_argument(
            "-UB",
            "--UBmatrix",
            metavar=("a11", "a12", "a13", "a21", "a22", "a23", "a31", "a32", "a33"),
            type=float,
            nargs=9,
            help="Sets UB matrix",
        )
        self.parser.add_argument(
            "-c2",
            "--Calc2",
            metavar=("R1", "R2"),
            type=int,
            nargs=2,
            help="Calculate UB for 2 reflections, user must give the reflections that will be used",
        )
        self.parser.add_argument(
            "-c3",
            "--Calc3",
            metavar=("R1", "R2", "R3"),
            type=int,
            nargs=3,
            help="Calculate UB for 3 reflections, user must give the reflections that will be used",
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
            help="Clear reflections by index",
        )
        parser.add_argument(
            "-ca",
            "--clear-all",
            action="store_true",
            help="Clear all stored reflections",
        )
        self.parser.add_argument(
            "-l", "--list", action="store_true", help="List stored reflections"
        )
        self.parser.add_argument(
            "-s", "--Show", action="store_true", help="Show U and UB"
        )
        self.parser.add_argument(
            "-p",
            "--Params",
            action="store_true",
            help="Lattice parameters if 3 reflection calculation had been done",
        )

        args = self.parser.parse_args()
        return args


    def set_ub(self, ub_list: list) -> None:
        """Set UB matrix based in the user input"""
        UB = np.array(ub_list).reshape(3, 3)
        self.experiment_file_dict["UB_mat"] = UB.tolist()
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
                "col1": center1.format(lb(U[0][0])),
                "col2": center2.format(lb(U[0][1])),
                "col3": center3.format(lb(U[0][2])),
            },
            {
                "ident": "U    =   ",
                "col1": center1.format(lb(U[1][0])),
                "col2": center2.format(lb(U[1][1])),
                "col3": center3.format(lb(U[1][2])),
            },
            {
                "ident": "",
                "col1": center1.format(lb(U[2][0])),
                "col2": center2.format(lb(U[2][1])),
                "col3": center3.format(lb(U[2][2])),
            },
        ]

        dict_ub_mat = [
            {
                "ident": "",
                "col1": center1.format(lb(UB[0][0])),
                "col2": center2.format(lb(UB[0][1])),
                "col3": center3.format(lb(UB[0][2])),
            },
            {
                "ident": "UB   = ",
                "col1": center1.format(lb(UB[1][0])),
                "col2": center2.format(lb(UB[1][1])),
                "col3": center3.format(lb(UB[1][2])),
            },
            {
                "ident": "",
                "col1": center1.format(lb(UB[2][0])),
                "col2": center2.format(lb(UB[2][1])),
                "col3": center3.format(lb(UB[2][2])),
            },
        ]

        u_to_print = daf.TablePrinter(fmt1, ul="")(dict_u_mat)
        ub_to_print = daf.TablePrinter(fmt1, ul="")(dict_ub_mat)

        return u_to_print, ub_to_print

    def create_new_configuration_file(self, file_name: str) -> None:
        """Create a new empty configuration counter file, counters should be added in advance."""
        yaml_file_name = self.YAML_PREFIX + file_name + self.YAML_SUFIX
        full_file_path = path.join(dp.SCAN_UTILS_USER_PATH, yaml_file_name)
        self.write_yaml([], full_file_path)

    def list_counter_in_a_configuration_file(self, file_name: str) -> None:
        """List all counters in a configuration file"""
        full_file_path = self.get_full_file_path(file_name)
        data = self.read_yaml(full_file_path)
        print("Counters in: {}".format(file_name))
        for counter in data:
            print(counter)

    def add_counters_to_a_file(self, file_name: str, counters: list) -> None:
        """Add counters to a config file"""
        full_file_path = self.get_full_file_path(file_name)
        data = self.read_yaml(full_file_path)
        if isinstance(data, list):
            for counter in counters:
                if counter not in data:
                    data.append(counter)
            self.write_yaml(data, full_file_path)
        else:
            list_ = []
            for counter in counters:
                if counter not in list_:
                    list_.append(counter)
            self.write_yaml(list_, full_file_path)

    def remove_counters_from_file(self, file_name: str, counters: list) -> None:
        """Remove counters from a configuragtion file"""
        full_file_path = self.get_full_file_path(file_name)
        data = self.read_yaml(full_file_path)
        for counter in counters:
            if counter in data:
                data.remove(counter)
        self.write_yaml(data, full_file_path)

    def set_main_counter(self, counter: str) -> None:
        """
        Sets de main counter that will be used in the scans. This will set the counter
        thats going to be shown in the main tab in the DAF live view (daf.live)
        """
        self.experiment_file_dict["main_scan_counter"] = counter
        self.write_flag = True

    def delete_configuration_file(self, file_name: str):
        """Delete a configuration file configuration. Sometimes it wont be possible to delete a sys conf file"""
        full_file_path = self.get_full_file_path(file_name)
        os.remove(full_file_path)

    def run_cmd(self, arguments: dict) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        if arguments["UBmatrix"]:
            self.set_ub(arguments["UBmatrix"])

        if arguments["new"]:
            self.create_new_configuration_file(arguments["new"])

        if arguments["add_counter"]:
            self.add_counters_to_a_file(
                arguments["add_counter"][0], arguments["add_counter"][1:]
            )

        if arguments["remove_counter"]:
            self.remove_counters_from_file(
                arguments["remove_counter"][0], arguments["remove_counter"][1:]
            )

        if arguments["main_counter"]:
            self.set_main_counter(arguments["main_counter"])

        if arguments["remove"]:
            for file in arguments["remove"]:
                self.delete_configuration_file(file)

        if arguments["list"]:
            self.list_configuration_files()

        if arguments["list_all_counters"]:
            self.list_all_counters()

        if isinstance(arguments["list_counters"], list):
            for file in arguments["list_counters"]:
                self.list_counter_in_a_configuration_file(file)

        if self.write_flag:
            du.write(self.experiment_file_dict)


@daf_log
def main() -> None:
    obj = CalcUB()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()

if args.Show:



if args.Params:
    dict_args = du.read()
    print("")
    print("a    =    {}".format(dict_args["lparam_a"]))
    print("b    =    {}".format(dict_args["lparam_b"]))
    print("c    =    {}".format(dict_args["lparam_c"]))
    print("alpha    =    {}".format(dict_args["lparam_alpha"]))
    print("beta    =    {}".format(dict_args["lparam_beta"]))
    print("gamma    =    {}".format(dict_args["lparam_gama"]))
    print("")


if args.reflection is not None:
    dict_args = du.read()
    ref = dict_args["reflections"]
    en = dict_args["PV_energy"] - dict_args["energy_offset"]
    if en < 50:
        en = float(xu.lam2en(en))
    args.reflection.append(en)
    ref.append(args.reflection)
    dict_args["reflections"] = ref
    du.write(dict_args)

if args.reflection_now is not None:
    dict_args = du.read()
    ref = dict_args["reflections"]
    h = args.reflection_now[0]
    k = args.reflection_now[1]
    l = args.reflection_now[2]
    mu = dict_args["Mu"]
    eta = dict_args["Eta"]
    chi = dict_args["Chi"]
    phi = dict_args["Phi"]
    nu = dict_args["Nu"]
    delta = dict_args["Del"]
    en = dict_args["PV_energy"] - dict_args["energy_offset"]
    if en < 50:
        en = float(xu.lam2en(en))
    ref_now = [h, k, l, mu, eta, chi, phi, nu, delta, en]
    ref.append(ref_now)
    dict_args["reflections"] = ref
    du.write(dict_args)

if args.list:
    dict_args = du.read()
    refs = dict_args["reflections"]
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

    pd = daf.TablePrinter(fmt, ul="")(data)
    print(pd)
    print("")

if args.clear_reflections is not None:
    dict_args = du.read()
    list_ = dict_args["reflections"]
    for idx in args.clear_reflections:
        list_.pop(idx - 1)
    dict_args["reflections"] = list_
    du.write(dict_args)

if args.clear_all:
    dict_args = du.read()
    dict_args["reflections"] = []
    du.write(dict_args)

if args.Umatrix:
    dict_args = du.read()
    U = np.array(args.Umatrix).reshape(3, 3)
    mode = [int(i) for i in dict_args["Mode"]]

    exp = daf.Control(*mode)

    if dict_args["Material"] in dict_args["user_samples"].keys():
        exp.set_material(
            dict_args["Material"], *dict_args["user_samples"][dict_args["Material"]]
        )

    else:
        exp.set_material(
            dict_args["Material"],
            dict_args["lparam_a"],
            dict_args["lparam_b"],
            dict_args["lparam_c"],
            dict_args["lparam_alpha"],
            dict_args["lparam_beta"],
            dict_args["lparam_gama"],
        )

    # exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    exp.set_exp_conditions(en=dict_args["PV_energy"] - dict_args["energy_offset"])
    exp.set_U(U)
    UB = exp.calcUB()
    dict_args[
        "U_mat"
    ] = (
        U.tolist()
    )  # yaml doesn't handle numpy arrays well, so using python's list is a better choice
    dict_args[
        "UB_mat"
    ] = (
        UB.tolist()
    )  # yaml doesn't handle numpy arrays well, so using python's list is a better choice
    du.write(dict_args)


if args.Calc2 is not None:
    dict_args = du.read()
    refs = dict_args["reflections"]
    mode = [int(i) for i in dict_args["Mode"]]

    exp = daf.Control(*mode)
    exp.set_material(
        dict_args["Material"],
        dict_args["lparam_a"],
        dict_args["lparam_b"],
        dict_args["lparam_c"],
        dict_args["lparam_alpha"],
        dict_args["lparam_beta"],
        dict_args["lparam_gama"],
    )
    exp.set_exp_conditions(en=dict_args["PV_energy"] - dict_args["energy_offset"])
    hkl1 = refs[args.Calc2[0] - 1][:3]
    angs1 = refs[args.Calc2[0] - 1][3:-1]
    hkl2 = refs[args.Calc2[1] - 1][:3]
    angs2 = refs[args.Calc2[1] - 1][3:-1]
    U, UB = exp.calc_U_2HKL(hkl1, angs1, hkl2, angs2)

    dict_args["U_mat"] = U.tolist()
    dict_args["UB_mat"] = UB.tolist()
    du.write(dict_args)

if args.Calc3 is not None:
    dict_args = du.read()
    refs = dict_args["reflections"]
    mode = [int(i) for i in dict_args["Mode"]]
    exp = daf.Control(*mode)
    # exp.set_material(dict_args['Material'])

    hkl1 = refs[args.Calc3[0] - 1][:3]
    angs1 = refs[args.Calc3[0] - 1][3:-1]
    e1 = refs[args.Calc3[0] - 1][9]
    hkl2 = refs[args.Calc3[1] - 1][:3]
    angs2 = refs[args.Calc3[1] - 1][3:-1]
    e2 = refs[args.Calc3[1] - 1][9]
    hkl3 = refs[args.Calc3[2] - 1][:3]
    angs3 = refs[args.Calc3[2] - 1][3:-1]
    e3 = refs[args.Calc3[2] - 1][9]
    e = (e1 + e2 + e3) / 3
    exp.set_exp_conditions(en=e)
    U, UB, rp = exp.calc_U_3HKL(hkl1, angs1, hkl2, angs2, hkl3, angs3)

    rpf = [
        float(i) for i in rp
    ]  # Problems when saving numpy64floats, better to use python's float
    dict_args["U_mat"] = U.tolist()
    dict_args["UB_mat"] = UB.tolist()
    dict_args["lparam_a"] = rpf[0]
    dict_args["lparam_b"] = rpf[1]
    dict_args["lparam_c"] = rpf[2]
    dict_args["lparam_alpha"] = rpf[3]
    dict_args["lparam_beta"] = rpf[4]
    dict_args["lparam_gama"] = rpf[5]
    du.write(dict_args)

if args.fit:
    dict_args = du.read()
    refs = dict_args["reflections"]
    mode = [int(i) for i in dict_args["Mode"]]

    exp = daf.Control(*mode)
    exp.set_material(
        dict_args["Material"],
        dict_args["lparam_a"],
        dict_args["lparam_b"],
        dict_args["lparam_c"],
        dict_args["lparam_alpha"],
        dict_args["lparam_beta"],
        dict_args["lparam_gama"],
    )
    exp.set_exp_conditions(en=dict_args["PV_energy"] - dict_args["energy_offset"])
    U = np.array(dict_args["U_mat"])
    if dict_args["Material"] in dict_args["user_samples"].keys():
        exp.set_material(
            dict_args["Material"], *dict_args["user_samples"][dict_args["Material"]]
        )

    else:
        exp.set_material(
            dict_args["Material"],
            dict_args["lparam_a"],
            dict_args["lparam_b"],
            dict_args["lparam_c"],
            dict_args["lparam_alpha"],
            dict_args["lparam_beta"],
            dict_args["lparam_gama"],
        )

    fitted = exp.fit_u_matrix(U, refs)
    lbd = [[float(lb(i)) for i in j] for j in fitted]
    print(np.array(lbd))

    dict_args["U_mat"] = U.tolist()
    # dict_args['UB_mat'] = UB.tolist()
    du.write(dict_args)
