import os
import sys
from abc import abstractmethod

import daf.utils.dafutilities as du
from daf.command_line.cli_base_utils import CLIBase
import daf.command_line.scan.scan_daf as sd
from daf.command_line.scan.scan_daf import DAFScanInputs
from daf.utils.daf_paths import DAFPaths as dp


class ScanBase(CLIBase):
    def __init__(
        self, *args, number_of_motors: int = None, scan_type: str = None, **kwargs
    ):
        self.io = du.DAFIO(read=False)
        self.experiment_file_dict = self.io.only_read()
        self.number_of_motors = number_of_motors
        self.scan_type = scan_type
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.inputed_motors = self.get_inputed_motor_order(sys.argv)

    def parse_command_line(self):
        """The majority of the scans use this, but some not and have to overwrite this method"""
        super().parse_command_line()
        for motor in self.experiment_file_dict["motors"].keys():
            self.parser.add_argument(
                "-" + self.experiment_file_dict["motors"][motor]["cli_abbrev"],
                "--" + motor,
                metavar=("start", "end"),
                type=float,
                nargs=2,
                help="Start and end for {}".format(motor),
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
            "-o",
            "--output",
            help="output data to file output-prefix/<fileprefix>_nnnn",
            default=os.getcwd() + "/scan_daf.nxs",
        )

    def get_inputed_motor_order(self, sysargv: sys.argv) -> list:
        """Method to retrieve the right order that the user input arguments through shell"""
        full_name = ["--" + i for i in self.experiment_file_dict["motors"].keys()]
        abbrev = [
            "-" + self.experiment_file_dict["motors"][i]["cli_abbrev"]
            for i in self.experiment_file_dict["motors"].keys()
        ]
        all_possibilities = full_name + abbrev

        abbrev_map = {
            self.experiment_file_dict["motors"][i]["cli_abbrev"]: i
            for i in self.experiment_file_dict["motors"].keys()
        }
        full_name_map = {i: i for i in self.experiment_file_dict["motors"].keys()}
        abbrev_map.update(full_name_map)
        full_map = abbrev_map
        motor_order = [
            full_map[i.split("-")[-1]] for i in sysargv if i in all_possibilities
        ]
        return motor_order

    def get_counters(self):
        path_to_config = dp.SCAN_CONFIGS
        path_to_file = os.path.join(
            path_to_config, self.experiment_file_dict["default_counters"]
        )
        counter_names = du.read_yml(path_to_file)
        counter_data = {
            counter: self.experiment_file_dict["counters"][counter]
            for counter in counter_names
        }
        return counter_data

    def configure_scan_input(self):
        scan_data = {
            motor: self.parsed_args_dict[motor] for motor in self.inputed_motors
        }
        scan_inputs = {
            "scan_data": scan_data,
            "inputed_motors": self.inputed_motors,
            "motors_data_dict": self.experiment_file_dict["motors"],
            "counters": self.get_counters(),
            "main_counter": self.experiment_file_dict["main_scan_counter"],
            "scan_type": self.scan_type,
            "steps": self.parsed_args_dict["step"]
            + 1,  # Number of interval instead of number of points
            "acquisition_time": self.parsed_args_dict["time"],
            "output": self.parsed_args_dict["output"],
            "kafka_topic": self.experiment_file_dict["kafka_topic"],
            "scan_db": self.experiment_file_dict["scan_db"],
        }

        return scan_inputs

    def run_scan(self) -> None:
        """Perform the scan"""
        scan_inputs = self.configure_scan_input()
        scan_inputs_obj = DAFScanInputs(**scan_inputs)
        scan = sd.DAFScan(scan_inputs_obj)
        scan.run()
