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
import daf.command_line.scan.scan_daf as sd


class ScanBase(CLIBase):
    def __init__(
        self, *args, number_of_motors: int = None, scan_type: str = None, **kwargs
    ):
        super().__init__()
        self.number_of_motors = number_of_motors
        self.scan_type = scan_type
        if scan_type == "relative" or scan_type == "rel":
            self.reset_motors_pos_on_scan_end = True
        else:
            self.reset_motors_pos_on_scan_end = False
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.motor_map = self.create_motor_map()
        self.scan_args = self.configure_scan()
        signal.signal(signal.SIGINT, self.sigint_handler_utilities)

    def sigint_handler_utilities(self, signum: signal, frame: "function") -> None:
        """Function to handle ctrl + c and avoid breaking daf's .Experiment file"""
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.experiment_file_dict["scan_running"] = False
        self.write_to_experiment_file({})
        print("\n")
        exit(1)

    def parse_command_line(self):
        """The majority of the scans use this, but some not and have to overwrite this method"""
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
            "-sz",
            "--sample_z",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for sample_z",
        )
        self.parser.add_argument(
            "-sx",
            "--sample_x",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for sample_x",
        )
        self.parser.add_argument(
            "-srx",
            "--sample_rx",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for sample_rx",
        )
        self.parser.add_argument(
            "-sy",
            "--sample_y",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for sample_y",
        )
        self.parser.add_argument(
            "-sry",
            "--sample_ry",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for sample_ry",
        )
        self.parser.add_argument(
            "-sx1",
            "--sample_x_s1",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for sample_x_s1",
        )
        self.parser.add_argument(
            "-sy1",
            "--sample_y_s1",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for sample_y_s1",
        )
        self.parser.add_argument(
            "-diffux",
            "--diffractomer_ux",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for diffractomer_ux",
        )
        self.parser.add_argument(
            "-diffuy",
            "--diffractomer_uy",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for diffractomer_uy",
        )
        self.parser.add_argument(
            "-diffrx",
            "--diffractomer_rx",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for diffractomer_rx",
        )
        self.parser.add_argument(
            "-thca",
            "--theta_analyzer_crystal",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for theta_analyzer_crystal",
        )
        self.parser.add_argument(
            "-tthca",
            "--2theta_analyzer_crystal",
            metavar="ang",
            type=float,
            nargs=2,
            help="Start and end for 2theta_analyzer_crystal",
        )
        self.common_cli_scan_arguments()
        args = self.parser.parse_args()
        return args

    def common_cli_scan_arguments(self, step=True) -> None:
        """This are the arguments that are common to all daf scans"""
        if step:
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
        self.parser.add_argument(
            "-rm",
            "--reset-motors",
            help="flag to tell if the motor should be reseted to their default position",
            default=self.reset_motors_pos_on_scan_end,
            action="store_true",
        )

    def create_motor_map(self) -> dict:
        """Create a map for the motors based in the PV prefix"""
        data = {
            "mu": self.experiment_file_dict["motors"]["mu"]["scan_utils_mnemonic"],
            "eta": self.experiment_file_dict["motors"]["eta"]["scan_utils_mnemonic"],
            "chi": self.experiment_file_dict["motors"]["chi"]["scan_utils_mnemonic"],
            "phi": self.experiment_file_dict["motors"]["phi"]["scan_utils_mnemonic"],
            "nu": self.experiment_file_dict["motors"]["nu"]["scan_utils_mnemonic"],
            "del": self.experiment_file_dict["motors"]["del"]["scan_utils_mnemonic"],
            "sample_z": self.experiment_file_dict["motors"]["sample_z"][
                "scan_utils_mnemonic"
            ],
            "sample_x": self.experiment_file_dict["motors"]["sample_x"][
                "scan_utils_mnemonic"
            ],
            "sample_rx": self.experiment_file_dict["motors"]["sample_rx"][
                "scan_utils_mnemonic"
            ],
            "sample_y": self.experiment_file_dict["motors"]["sample_y"][
                "scan_utils_mnemonic"
            ],
            "sample_ry": self.experiment_file_dict["motors"]["sample_ry"][
                "scan_utils_mnemonic"
            ],
            "sample_x_s1": self.experiment_file_dict["motors"]["sample_x_s1"][
                "scan_utils_mnemonic"
            ],
            "sample_y_s1": self.experiment_file_dict["motors"]["sample_y_s1"][
                "scan_utils_mnemonic"
            ],
            "diffractomer_ux": self.experiment_file_dict["motors"]["diffractomer_ux"][
                "scan_utils_mnemonic"
            ],
            "diffractomer_uy": self.experiment_file_dict["motors"]["diffractomer_uy"][
                "scan_utils_mnemonic"
            ],
            "diffractomer_rx": self.experiment_file_dict["motors"]["diffractomer_rx"][
                "scan_utils_mnemonic"
            ],
            "theta_analyzer_crystal": self.experiment_file_dict["motors"][
                "theta_analyzer_crystal"
            ]["scan_utils_mnemonic"],
            "2theta_analyzer_crystal": self.experiment_file_dict["motors"][
                "2theta_analyzer_crystal"
            ]["scan_utils_mnemonic"],
        }

        return data

    @staticmethod
    def get_inputed_motor_order(sysargv: sys.argv, motor_map: dict) -> list:
        """Method to retrieve the right order that the user input arguments through shell"""
        all_possibilities = [
            "-m",
            "-e",
            "-c",
            "-p",
            "-n",
            "-d",
            "-sz",
            "-sx",
            "-srx",
            "-sy",
            "-sry",
            "-sx1",
            "-sy1",
            "-diffux",
            "-diffuy",
            "-diffrx",
            "-thca",
            "-tthca",
            "--mu",
            "--eta",
            "--chi",
            "--phi",
            "--nu",
            "--del",
            "--sample_z",
            "--sample_x",
            "--sample_rx",
            "--sample_y",
            "--sample_ry",
            "--sample_x_s1",
            "--sample_y_s1",
            "--diffractomer_ux",
            "--diffractomer_uy",
            "--diffractomer_rx",
            "--theta_analyzer_crystal",
            "--2theta_analyzer_crystal",
        ]

        simp_to_comp = {
            "m": "mu",
            "e": "eta",
            "c": "chi",
            "p": "phi",
            "n": "nu",
            "d": "del",
            "sz": "sample_z",
            "sx": "sample_x",
            "srx": "sample_rx",
            "sy": "sample_y",
            "sry": "sample_ry",
            "sx1": "sample_x_s1",
            "sy1": "sample_y_s1",
            "diffux": "diffractomer_ux",
            "diffuy": "diffractomer_uy",
            "diffrx": "diffractomer_rx",
            "thca": "theta_analyzer_crystal",
            "tthca": "2theta_analyzer_crystal",
            "mu": "mu",
            "eta": "eta",
            "chi": "chi",
            "phi": "phi",
            "nu": "nu",
            "del": "del",
            "sample_z": "sample_z",
            "sample_x": "sample_x",
            "sample_rx": "sample_rx",
            "sample_y": "sample_y",
            "sample_ry": "sample_ry",
            "sample_x_s1": "sample_x_s1",
            "sample_y_s1": "sample_y_s1",
            "diffractomer_ux": "diffractomer_ux",
            "diffractomer_uy": "diffractomer_uy",
            "diffractomer_rx": "diffractomer_rx",
            "theta_analyzer_crystal": "theta_analyzer_crystal",
            "2theta_analyzer_crystal": "2theta_analyzer_crystal",
        }

        motor_order = [
            motor_map[simp_to_comp[i.split("-")[-1]]]
            for i in sysargv
            if i in all_possibilities
        ]

        return motor_order

    def get_current_motor_pos(self) -> dict:
        """Get the current motor pos and return a dict"""
        mu_now = self.experiment_file_dict["motors"]["mu"]["value"]
        eta_now = self.experiment_file_dict["motors"]["eta"]["value"]
        chi_now = self.experiment_file_dict["motors"]["chi"]["value"]
        phi_now = self.experiment_file_dict["motors"]["phi"]["value"]
        nu_now = self.experiment_file_dict["motors"]["nu"]["value"]
        del_now = self.experiment_file_dict["motors"]["del"]["value"]
        sz_now = self.experiment_file_dict["motors"]["sample_z"]["value"]
        sx_now = self.experiment_file_dict["motors"]["sample_x"]["value"]
        srx_now = self.experiment_file_dict["motors"]["sample_rx"]["value"]
        sy_now = self.experiment_file_dict["motors"]["sample_y"]["value"]
        sry_now = self.experiment_file_dict["motors"]["sample_ry"]["value"]
        sx1_now = self.experiment_file_dict["motors"]["sample_x_s1"]["value"]
        sy1_now = self.experiment_file_dict["motors"]["sample_y_s1"]["value"]
        diffux_now = self.experiment_file_dict["motors"]["diffractomer_ux"]["value"]
        diffuy_now = self.experiment_file_dict["motors"]["diffractomer_uy"]["value"]
        diffrx_now = self.experiment_file_dict["motors"]["diffractomer_rx"]["value"]
        thca_now = self.experiment_file_dict["motors"]["theta_analyzer_crystal"][
            "value"
        ]
        tthca_now = self.experiment_file_dict["motors"]["2theta_analyzer_crystal"][
            "value"
        ]
        current_motor_pos = {
            "mu": mu_now,
            "eta": eta_now,
            "chi": chi_now,
            "phi": phi_now,
            "nu": nu_now,
            "del": del_now,
            "sample_z": sz_now,
            "sample_x": sx_now,
            "sample_rx": srx_now,
            "sample_y": sy_now,
            "sample_ry": sry_now,
            "sample_x_s1": sx1_now,
            "sample_y_s1": sy1_now,
            "diffractomer_ux": diffux_now,
            "diffractomer_uy": diffuy_now,
            "diffractomer_rx": diffrx_now,
            "theta_analyzer_crystal": thca_now,
            "2theta_analyzer_crystal": tthca_now,
        }
        return current_motor_pos

    def generate_data_for_scan(
        self,
        arguments: dict,
        number_of_motors: int,
        motor_map: dict,
        current_motor_pos: dict,
        scan_type: str,
    ) -> tuple:
        """Generate the scan path for scans"""
        number_of_iters = 0
        motors = []
        data_for_scan = {}
        for key, val in arguments.items():
            if isinstance(val, list):
                motor = key
                motors.append(motor_map[motor])
                if scan_type == "absolute" or scan_type == "abs":
                    points = np.linspace(val[0], val[1], arguments["step"] + 1)
                elif scan_type == "relative" or scan_type == "rel":
                    points = np.linspace(
                        current_motor_pos[motor] + val[0],
                        current_motor_pos[motor] + val[1],
                        arguments["step"] + 1,
                    )
                points = [float(i) for i in points]
                data_for_scan[motor_map[motor]] = points
                number_of_iters += 1
            if number_of_iters == number_of_motors:
                break
        ordered_motors = self.get_inputed_motor_order(sys.argv, motor_map)
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
        with open(".points.yaml", "w") as stream:
            yaml.dump(data_for_scan, stream, allow_unicode=False)

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
            "reset": arguments["reset_motors"],
            "step_mode": False,
            "points_mode": False,
            "start": None,
            "end": None,
            "step_or_points": None,
            "time": [[arguments["time"]]],
            "filename": ".points.yaml",
        }

        return scan_args

    def configure_scan(self) -> dict:
        """Basically, a wrapper for configure_scan_inputs. It may differ from scan to scan"""
        data_for_scan, ordered_motors = self.generate_data_for_scan(
            self.parsed_args_dict,
            self.number_of_motors,
            self.motor_map,
            self.get_current_motor_pos(),
            self.scan_type,
        )
        if self.parsed_args_dict["xlabel"] == None:
            xlabel = ordered_motors[0]
        else:
            xlabel = motor_map[self.parsed_args_dict["xlabel"].lower()]
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

    def run_scan(self) -> None:
        """Perform the scan"""
        scan = sd.DAFScan(self.scan_args)
        scan.run()
