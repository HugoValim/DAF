#!/usr/bin/env python3

import signal

from daf.utils.log import daf_log
from daf.command_line.cli_base_utils import CLIBase
from daf.command_line.scan.daf_scan_utils import ScanBase
import daf.command_line.scan.time_scan_daf as td


class TimeScan(CLIBase):

    DESC = """Perform an infinite time scan for the configured counters, i should be stopped with Ctrl+c"""
    EPI = """
    Eg:
        daf.tscan .1
        daf.tscan .1 -d 1

        """

    def __init__(self):
        self.reset_motors_pos_on_scan_end = False
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        signal.signal(signal.SIGINT, self.sigint_handler_utilities)

    def sigint_handler_utilities(self, *args, **kwargs):
        """Wrap the signal handler, so all scans points to the same guy"""
        ScanBase.sigint_handler_utilities(self, args, kwargs)

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-d",
            "--delay",
            metavar="delay",
            type=float,
            help="Delay between each point in seconds",
            default=0,
        )
        ScanBase.common_cli_scan_arguments(self, step=False)
        args = self.parser.parse_args()
        return args

    def config_scan_inputs(self, arguments: dict):
        """
        Generate all needed params for the scan based on the user input.
        """
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
            "motor": None,
            "xlabel": "points",
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
            "filename": None,
        }

        return scan_args

    def run_scan(self):
        scan_args = self.config_scan_inputs(self.parsed_args_dict)
        scan = td.DAFTimeScan(scan_args, delay=self.parsed_args_dict["delay"])
        scan.run()

    def run_cmd(self):
        """
        Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface
        """
        self.run_scan()


@daf_log
def main() -> None:
    obj = TimeScan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
