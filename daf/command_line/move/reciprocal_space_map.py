#!/usr/bin/env python3

from dataclasses import dataclass

import argparse as ap
import numpy as np
from matplotlib import pyplot as plt

from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.utils import dafutilities as du
from daf.command_line.move.move_utils import MoveBase

@dataclass
class GraphAttributes:
    ttmin: float
    ttmax: float
    idir: list
    ndir: list
    scale: float

class ReciprocalSpace(MoveBase):
    DESC = """Move in reciprocal space by choosing a HKL in a graphical resciprocal space map"""
    EPI = """
    Eg:
        daf.rmap
        daf.rmap -i 1 1 0 -n 0 0 1
        daf.rmap -m Cu Ge
        daf.rmap -i 1 1 0 -n 0 0 1 -m Ge
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()
        plt.show(block=True)

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-i",
            "--IDir",
            metavar=("x", "y", "z"),
            type=float,
            nargs=3,
            help="Sets the plane paralel to x axis",
            default=self.experiment_file_dict['IDir']
        )
        self.parser.add_argument(
            "-n",
            "--NDir",
            metavar=("x", "y", "z"),
            type=float,
            nargs=3,
            help="Sets the plane perpendicular to x axis",
            default=self.experiment_file_dict['NDir']
        )
        self.parser.add_argument(
            "-m",
            "--materials",
            metavar="sample",
            nargs="*",
            help="Add a predefined material to rmap visualization",
        )
        self.parser.add_argument(
            "-s",
            "--scale",
            metavar="",
            type=float,
            help="Scale reference for the points in the map, default is 100",
            default=100
        )

        args = self.parser.parse_args()
        return args

    def build_reciprocal_map(self, idir, ndir, scale):
        """Build the reciprocal space map based in the current conditions"""
        ttmax, ttmin = self.exp.two_theta_max()
        ax, h = self.exp.show_reciprocal_space_plane(
            ttmax=ttmax, ttmin=ttmin, idir=idir, ndir=ndir, scalef=scale
        )
        graph_att_obj = GraphAttributes(    
            ttmin,
            ttmax,
            idir,
            ndir,
            scale)
        return ax, graph_att_obj

    def append_to_reciprocal_map(self, sample: str, axis: "subplot_axis", graph_att: GraphAttributes):
        """
        For each sample passed by the user another instance of an experiment should 
        be created and appended to the existing graph figure.
        """
        exp = self.build_exp()
        exp.set_material(sample)
        ttmax, ttmin = exp.two_theta_max()
        ax, h2 = exp.show_reciprocal_space_plane(
            ttmax=graph_att.ttmax,
            ttmin=graph_att.ttmin,
            idir=graph_att.idir,
            ndir=graph_att.ndir,
            scalef=graph_att.scale,
            ax=axis,
        )

    def run_cmd(self, arguments) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        ax, graph_att_obj = self.build_reciprocal_map(arguments["IDir"], arguments["NDir"], arguments["scale"])
        if arguments["materials"]:
            for sample in arguments["materials"]:
                self.append_to_reciprocal_map(sample, ax, graph_att_obj)
                
        plt.show(block=True)
        ax.figure.show()

@daf_log
def main() -> None:
    obj = ReciprocalSpace()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
