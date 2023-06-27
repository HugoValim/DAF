#!/usr/bin/env python3

import signal

from daf.utils.decorators import cli_decorator
from daf.command_line.cli_base_utils import CLIBase
from daf.command_line.scan.daf_scan_utils import ScanBase


class TimeScan(ScanBase):

    DESC = """Perform an infinite time scan for the configured counters, i should be stopped with Ctrl+c"""
    EPI = """
    Eg:
        daf.tscan .1
        daf.tscan .1 -d 1

        """

    def __init__(self):
        super().__init__(scan_type="count")

    def parse_command_line(self):
        CLIBase.parse_command_line(self)
        self.parser.add_argument(
            "-d",
            "--delay",
            metavar="delay",
            type=float,
            help="Delay between each point in seconds",
            default=0,
        )
        super().common_cli_scan_arguments(step=False)

        args = self.parser.parse_args()
        return args

    def configure_scan_input(self):
        """Basically, a wrapper for configure_scan_inputs. It may differ from scan to scan"""
        return {
            "counters": self.get_counters(),
            "scan_type": self.scan_type,
            "acquisition_time": self.parsed_args_dict["time"],
            "delay_time": self.parsed_args_dict["delay"],
            "output": self.parsed_args_dict["output"],
            "kafka_topic": self.experiment_file_dict["kafka_topic"],
            "scan_db": self.experiment_file_dict["scan_db"],
        }

    def run_cmd(self) -> None:
        """
        Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface
        """
        self.run_scan()


@cli_decorator
def main() -> None:
    obj = TimeScan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
