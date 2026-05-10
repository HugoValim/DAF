from abc import abstractmethod
import argparse as ap
import numpy as np

from daf.core.main import DAF
from daf.command_line.cli_base_utils import CLIBase
import daf.utils.dafutilities as du


def _add_hkl_display_args(parser: ap.ArgumentParser) -> None:
    """Add the shared quiet/marker/column-marker/size display args to parser."""
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="do not show the full output"
    )
    parser.add_argument(
        "-m",
        "--marker",
        type=str,
        help="marker to be used in the print",
        default="",
    )
    parser.add_argument(
        "-cm",
        "--column-marker",
        type=str,
        help="column marker to be used in the print",
        default="",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        help="size of the print, default is 14",
        default=14,
    )


class MoveBase(CLIBase):
    def motor_inputs(self):
        """create all possible motor inputs parser"""
        for motor in self.experiment_file_dict["motors"].keys():
            self.parser.add_argument(
                "-" + self.experiment_file_dict["motors"][motor]["cli_abbrev"],
                "--" + motor,
                metavar="ang",
                type=str,
                help="sets {} angle to a desired position".format(motor),
            )
