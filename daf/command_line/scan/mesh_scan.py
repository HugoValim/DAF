#!/usr/bin/env python3

import sys

from daf.utils.log import daf_log
from daf.command_line.scan.daf_scan_utils import ScanBase


class MeshScan(ScanBase):

    DESC = """Perform a mesh scan using two of the diffractometer motors"""
    EPI = """
    Eg:
        daf.mesh -e -2 2 -d -2 6 100 .1
        daf.mesh -e -2 2 -d -2 6 100 .1 -np

        """

    def __init__(self):
        super().__init__(scan_type="mesh")

    def generate_data_for_scan(
        self,
        arguments: dict,
        number_of_motors: int,
        motor_map: dict,
        current_motor_pos: dict,
        scan_type: str,
    ) -> tuple:
        ordered_motors = self.get_inputed_motor_order(sys.argv, motor_map)
        start = []
        end = []
        step = []
        data_for_scan = {}
        inv_map = {v: k for k, v in motor_map.items()}
        for motor in ordered_motors:
            motor_daf_mapped = inv_map[motor]
            if isinstance(arguments[motor_daf_mapped], list):
                start.append(arguments[motor_daf_mapped][0])
                end.append(arguments[motor_daf_mapped][1])
                step.append(arguments["step"])
                data_for_scan[motor] = {}
                data_for_scan[motor]["start"] = start
                data_for_scan[motor]["end"] = end
                data_for_scan[motor]["step"] = step
        return data_for_scan, ordered_motors

    def config_scan_inputs(
        self,
        arguments: dict,
        motor_map: dict,
        number_of_motors: int,
        scan_type: str,
        data_for_scan: dict,
        ordered_motors: list,
        xlabel: str,
    ) -> dict:
        """
        Generate all needed params for the scan based on the user input.
        scan_type must be absolute (abs), relative or hkl_scan (hkl).
        """
        start = [data_for_scan[key]["start"] for key in data_for_scan.keys()]
        end = [data_for_scan[key]["end"] for key in data_for_scan.keys()]
        step = [data_for_scan[key]["step"] for key in data_for_scan.keys()]
        scan_args = {
            "motor": ordered_motors,
            "start": start,
            "end": end,
            "step_or_points": step,
            "time": [[arguments["time"]]],
            "configuration": self.experiment_file_dict["default_counters"].split(".")[
                1
            ],
            "optimum": None,
            "repeat": 1,
            "sleep": 0,
            "message": None,
            "output": arguments["output"],
            "sync": True,
            "snake": False,
            "xlabel": xlabel,
            "prescan": "ls",
            "postscan": "pwd",
            "plot_type": arguments["show_plot"],
            "relative": False,
            "reset": False,
            "step_mode": False,
            "points_mode": True,
        }

        return scan_args

    def configure_scan(self):
        data_for_scan, ordered_motors = self.generate_data_for_scan(
            self.parsed_args_dict,
            self.number_of_motors,
            self.motor_map,
            self.get_current_motor_pos(),
            self.scan_type,
        )
        if self.parsed_args_dict["xlabel"] is None:
            xlabel = ordered_motors[0]
        else:
            xlabel = self.motor_map[self.parsed_args_dict["xlabel"].lower()]
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

    def run_cmd(self):
        """Method to print the user required information"""
        self.run_scan()


@daf_log
def main() -> None:
    obj = MeshScan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
