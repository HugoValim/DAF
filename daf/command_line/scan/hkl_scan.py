#!/usr/bin/env python3

import numpy as np
import pandas as pd

from daf.utils.log import daf_log
from daf.command_line.cli_base_utils import CLIBase
from daf.command_line.scan.daf_scan_utils import ScanBase


class HKLScan(ScanBase):

    DESC = """Perform a scan using HKL coordinates"""
    EPI = """
    Eg:
        daf.scan 1 1 1 1.1 1.1 1.1 100 0.1 -n my_scan
        daf.scan 1 1 1 1.1 1.1 1.1 1000 0.1 -n my_scan -x eta -v
        daf.scan 1 1 1 1.1 1.1 1.1 100 0.1 -p -t 0.5
        """

    def __init__(self):
        super().__init__(scan_type="hkl")

    def parse_command_line(self):
        CLIBase.parse_command_line(self)
        self.parser.add_argument(
            "hkli",
            metavar=("Hi, Ki, Li"),
            type=float,
            nargs=3,
            help="Initial HKL for scan",
        )
        self.parser.add_argument(
            "hklf",
            metavar=("Hf, Kf, Lf"),
            type=float,
            nargs=3,
            help="Final HKL for scan",
        )
        self.parser.add_argument(
            "-n",
            "--scan_name",
            metavar="",
            type=str,
            default="daf_hkl_scan.csv",
            help="Name of the scan",
        )
        self.parser.add_argument(
            "-s", "--step", metavar="", type=float, help="Step for the scan"
        )
        self.parser.add_argument(
            "-sep",
            "--separator",
            metavar="",
            type=str,
            default=",",
            help="Chose the separator of scan file, comma is default",
        )
        self.parser.add_argument(
            "-m",
            "--max_diff",
            metavar="",
            type=float,
            default=0,
            help="Max difference of angles variation (default is 0.1), if 0 is given no verification will be done",
        )
        self.parser.add_argument(
            "-v", "--verbose", action="store_true", help="Show full output"
        )
        self.parser.add_argument(
            "-c",
            "--calc",
            action="store_true",
            help="Only calc the scan without perform it",
        )
        self.common_cli_scan_arguments()
        args = self.parser.parse_args()
        return args

    def generate_data_for_scan(self, motor_map: dict) -> np.array:
        """Generate the scan path for scans"""
        self.exp = self.build_exp()
        start_values = [i for i in self.get_current_motor_pos().values()]
        scan_points = self.exp.scan(
            self.parsed_args_dict["hkli"],
            self.parsed_args_dict["hklf"],
            self.parsed_args_dict["step"],
            diflimit=self.parsed_args_dict["max_diff"],
            name=self.parsed_args_dict["scan_name"],
            write=True,
            sep=self.parsed_args_dict["separator"],
            startvalues=start_values,
        )
        mu_points = [
            float(i) for i in scan_points["Mu"]
        ]  # Get only the points related to mu
        eta_points = [
            float(i) for i in scan_points["Eta"]
        ]  # Get only the points related to eta
        chi_points = [
            float(i) for i in scan_points["Chi"]
        ]  # Get only the points related to chi
        phi_points = [
            float(i) for i in scan_points["Phi"]
        ]  # Get only the points related to phi
        nu_points = [
            float(i) for i in scan_points["Nu"]
        ]  # Get only the points related to nu
        del_points = [
            float(i) for i in scan_points["Del"]
        ]  # Get only the points related to del
        data_for_scan = {
            motor_map["mu"]: mu_points,
            motor_map["eta"]: eta_points,
            motor_map["chi"]: chi_points,
            motor_map["phi"]: phi_points,
            motor_map["nu"]: nu_points,
            motor_map["del"]: del_points,
        }
        ordered_motors = [i for i in data_for_scan.keys()]

        return data_for_scan, ordered_motors

    def configure_scan(self):
        """Basically, a wrapper for configure_scan_inputs. It may differ from scan to scan"""
        data_for_scan, ordered_motors = self.generate_data_for_scan(self.motor_map)
        if self.parsed_args_dict["xlabel"] is not None:
            xlabel = self.motor_map[self.parsed_args_dict["xlabel"].lower()]
        else:
            xlabel = "points"
        scan_args = self.config_scan_inputs(
            self.parsed_args_dict,
            self.motor_map,
            self.number_of_motors,
            self.scan_type,
            data_for_scan,
            ordered_motors,
            xlabel,
        )
        return scan_args

    def print_scan_data_frame(self):
        """Print the csv file generated by DAF as a pandas DataFrame"""
        pd.options.display.max_rows = None
        pd.options.display.max_columns = 0
        print(self.exp)

    def run_cmd(self) -> None:
        """
        Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface
        """
        if self.parsed_args_dict["verbose"]:
            self.print_scan_data_frame()
        if not self.parsed_args_dict["calc"]:
            self.run_scan()


@daf_log
def main() -> None:
    obj = HKLScan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
