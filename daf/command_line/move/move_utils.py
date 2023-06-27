from abc import abstractmethod
import argparse as ap
import numpy as np

from daf.core.main import DAF
from daf.command_line.cli_base_utils import CLIBase
import daf.utils.dafutilities as du


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
