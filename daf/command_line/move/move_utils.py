from abc import abstractmethod
import argparse as ap
import numpy as np

from daf.core.main import DAF
from daf.command_line.cli_base_utils import CLIBase
import daf.utils.dafutilities as du


class MoveBase(CLIBase):
    def motor_inputs(self):
        """Get all possible motor inputs"""
        self.parser.add_argument(
            "-m",
            "--mu",
            metavar="ang",
            type=str,
            help="sets Mu angle to a desired position",
        )
        self.parser.add_argument(
            "-e",
            "--eta",
            metavar="ang",
            type=str,
            help="sets Eta angle to a desired position",
        )
        self.parser.add_argument(
            "-c",
            "--chi",
            metavar="ang",
            type=str,
            help="sets Chi angle to a desired position",
        )
        self.parser.add_argument(
            "-p",
            "--phi",
            metavar="ang",
            type=str,
            help="sets Phi angle to a desired position",
        )
        self.parser.add_argument(
            "-n",
            "--nu",
            metavar="ang",
            type=str,
            help="sets Nu angle to a desired position",
        )
        self.parser.add_argument(
            "-d",
            "--del",
            metavar="ang",
            type=str,
            help="sets Del angle to a desired position",
        )
        self.parser.add_argument(
            "-sz",
            "--sample_z",
            metavar="ang",
            type=str,
            help="sets sample z (stage 1 and 2) to a desired position",
        )
        self.parser.add_argument(
            "-sx",
            "--sample_x",
            metavar="ang",
            type=str,
            help="sets sample x (stage 2) to a desired position",
        )
        self.parser.add_argument(
            "-srx",
            "--sample_rx",
            metavar="ang",
            type=str,
            help="sets sample Rx (stage 2) to a desired position",
        )
        self.parser.add_argument(
            "-sy",
            "--sample_y",
            metavar="ang",
            type=str,
            help="sets sample y (stage 2) to a desired position",
        )
        self.parser.add_argument(
            "-sry",
            "--sample_ry",
            metavar="ang",
            type=str,
            help="sets sample Ry (stage 2) to a desired position",
        )
        self.parser.add_argument(
            "-sx1",
            "--sample_x_s1",
            metavar="ang",
            type=str,
            help="sets sample x (stage 1) to a desired position",
        )
        self.parser.add_argument(
            "-sy1",
            "--sample_y_s1",
            metavar="ang",
            type=str,
            help="sets sample y (stage 1) to a desired position",
        )
        self.parser.add_argument(
            "-diffux",
            "--diffractomer_ux",
            metavar="ang",
            type=str,
            help="sets diffractometer Ux to a desired position",
        )
        self.parser.add_argument(
            "-diffuy",
            "--diffractomer_uy",
            metavar="ang",
            type=str,
            help="sets diffractometer Uy to a desired position",
        )
        self.parser.add_argument(
            "-diffrx",
            "--diffractomer_rx",
            metavar="ang",
            type=str,
            help="sets diffractometer Rx to a desired position",
        )
        self.parser.add_argument(
            "-thca",
            "--theta_analyzer_crystal",
            metavar="ang",
            type=str,
            help="sets theta crystal an. to a desired position",
        )
        self.parser.add_argument(
            "-tthca",
            "--2theta_analyzer_crystal",
            metavar="ang",
            type=str,
            help="sets 2theta crystal an. to a desired position",
        )
