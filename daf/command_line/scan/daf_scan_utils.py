import os
import sys
import signal
from abc import abstractmethod

import argparse as ap
import numpy as np
import yaml

from scan_utils import PlotType
from daf.core.main import DAF
import daf.utils.dafutilities as du
from daf.command_line.cli_base_utils import CLIBase
import scan_daf as sd

class ScanBase(CLIBase):
    def __init__(self, number_of_motors: int, *args, **kwargs):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.motor_map = self.create_motor_map()
        self.ordered_motors = self.get_inputed_motor_order(sys.argv, self.motor_map)
        self.scan_args = self.config_scan_inputs(
            self.parsed_args_dict, self.motor_map, self.ordered_motors, number_of_motors
        )
        signal.signal(signal.SIGINT, self.sigint_handler_utilities)

    def sigint_handler_utilities(self, signum, frame):
        """Function to handle ctrl + c and avoid breaking daf's .Experiment file"""
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.experiment_file_dict["scan_running"] = False
        du.write(self.experiment_file_dict)
        print("\n")
        exit(1)

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-m",
            "--mu",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for Mu",
        )
        self.parser.add_argument(
            "-e",
            "--eta",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for Eta",
        )
        self.parser.add_argument(
            "-c",
            "--chi",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for Chi",
        )
        self.parser.add_argument(
            "-p",
            "--phi",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for Phi",
        )
        self.parser.add_argument(
            "-n",
            "--nu",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for Nu",
        )
        self.parser.add_argument(
            "-d",
            "--del",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for Del",
        )
        self.parser.add_argument(
            "step", metavar="step", type=int, help="Number of steps"
        )
        self.parser.add_argument(
            "time",
            metavar="time",
            type=float,
            help="Acquisition time in each point in seconds",
        )
        self.parser.add_argument(
            "-cf",
            "--configuration",
            type=str,
            help="choose a counter configuration file",
            default="default",
        )
        self.parser.add_argument(
            "-o",
            "--output",
            help="output data to file output-prefix/<fileprefix>_nnnn",
            default=os.getcwd() + "/scan_daf",
        )
        self.parser.add_argument(
            "-x",
            "--xlabel",
            help="motor which position is shown in x axis (if not set, point index is shown instead)",
        )
        self.parser.add_argument(
            "-sp",
            "--show-plot",
            help="Do not plot de scan",
            action="store_const",
            const=PlotType.hdf,
            default=PlotType.none,
        )
        self.parser.add_argument(
            "-cw",
            "--close-window",
            help="Close the scan window after it is done",
            default=False,
            action="store_true",
        )
        args = self.parser.parse_args()
        return args

    @staticmethod
    def create_motor_map():
        """Create a map for the motors based in the PV prefix"""
        if du.PV_PREFIX == "EMA:B:PB18":
            data = {
                "mu": "huber_mu",
                "eta": "huber_eta",
                "chi": "huber_chi",
                "phi": "huber_phi",
                "nu": "huber_nu",
                "del": "huber_del",
            }
        else:
            data = {
                "mu": "sol_m3",
                "eta": "sol_m5",
                "chi": "sol_m2",
                "phi": "sol_m1",
                "nu": "sol_m4",
                "del": "sol_m6",
            }

        return data

    @staticmethod
    def get_inputed_motor_order(sysargv: sys.argv, motor_map: dict):
        """method to pass the order that use choose to the scan_utils routine"""
        all_possibilities = [
            "-m",
            "-e",
            "-c",
            "-p",
            "-n",
            "-d",
            "--mu",
            "--eta",
            "--chi",
            "--phi",
            "--nu",
            "--del",
        ]

        simp_to_comp = {
            "mu": "mu",
            "eta": "eta",
            "chi": "chi",
            "phi": "phi",
            "nu": "nu",
            "del": "del",
            "m": "mu",
            "e": "eta",
            "c": "chi",
            "p": "phi",
            "n": "nu",
            "d": "del",
        }

        motor_order = [
            motor_map[simp_to_comp[i.split("-")[-1]]]
            for i in sysargv
            if i in all_possibilities
        ]

        return motor_order

    def config_scan_inputs(
        self,
        arguments: dict,
        motor_map: dict,
        ordered_motors: list,
        number_of_motors: int,
    ) -> dict:
        """Generate all needed params for the scan based on the user input"""
        number_of_iters = 0
        motors = []
        data_for_scan = {}
        for key, val in arguments.items():
            if isinstance(val, list):
                motor = key
                motors.append(motor_map[motor])
                points = np.linspace(val[0], val[1], arguments["step"] + 1)
                points = [float(i) for i in points]
                data_for_scan[motor_map[motor]] = points
                number_of_iters += 1
            if number_of_iters == number_of_motors:
                break

        with open(".points.yaml", "w") as stream:
            yaml.dump(data_for_scan, stream, allow_unicode=False)

        if arguments["xlabel"] == None:
            xlabel = ordered_motors[0]
        else:
            xlabel = data[arguments["xlabel"]]

        scan_args = {
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
            "motor": ordered_motors,
            "xlabel": xlabel,
            "prescan": "ls",
            "postscan": "pwd",
            "plot_type": arguments["show_plot"],
            "relative": False,
            "reset": False,
            "step_mode": False,
            "points_mode": False,
            "start": None,
            "end": None,
            "step_or_points": None,
            "time": [[arguments["time"]]],
            "filename": ".points.yaml",
        }

        return scan_args

    def run_scan(self):
        """Run the scan"""
        scan = sd.DAFScan(self.scan_args)
        scan.run()
