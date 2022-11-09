#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.command_line.experiment.experiment_utils import ExperimentBase
from daf.utils import dafutilities as du


class ExperimentConfiguration(ExperimentBase):
    DESC = """Sets several experiment configuration conditions"""

    EPI = """
    Eg:
        daf.expt --Material Si --energy 8000
        daf.expt -m Si -e 8000
        daf.expt -s x+
        daf.expt -i 1 0 0 -n 0 1 0
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-s",
            "--sample",
            metavar="sample",
            type=str,
            help="sets the material that is going to be used in the experiment",
        )
        self.parser.add_argument(
            "-p",
            "--lattice_parameters",
            metavar=("a", "b", "c", "alpha", "beta", "gamma "),
            type=float,
            nargs=6,
            help="sets lattice parameters, must be passed if defining a new material",
        )
        self.parser.add_argument(
            "-i",
            "--idir_print",
            metavar=("x", "y", "z"),
            type=float,
            nargs=3,
            help="sets the reflection paralel to the incident beam",
        )
        self.parser.add_argument(
            "-n",
            "--ndir_print",
            metavar=("x", "y", "z"),
            type=float,
            nargs=3,
            help="sets the reflection perpendicular to the incident beam",
        )
        self.parser.add_argument(
            "-r",
            "--rdir",
            metavar=("x", "y", "z"),
            type=float,
            nargs=3,
            help="sets the reference vector",
        )
        self.parser.add_argument(
            "-so",
            "--sample_orientation",
            metavar="or",
            type=str,
            help="sets the sample orientation at Phi axis",
        )
        self.parser.add_argument(
            "-e",
            "--energy",
            metavar="en",
            type=float,
            help="sets the energy of the experiment (eV), wavelength can also be given (angstrom)",
        )
        self.parser.add_argument(
            "-sim",
            "--simulated",
            action="store_true",
            help="use simulated somotors",
        )
        self.parser.add_argument(
            "-rl",
            "--real",
            action="store_true",
            help="use real motors in scans, movimentations",
        )

        args = self.parser.parse_args()
        return args

    def set_lattice_parameters(self, lattice_parameters: list) -> None:
        """Sets the inputed lattice parameters to the .Experiment file"""
        self.experiment_file_dict["lparam_a"] = lattice_parameters[0]
        self.experiment_file_dict["lparam_b"] = lattice_parameters[1]
        self.experiment_file_dict["lparam_c"] = lattice_parameters[2]
        self.experiment_file_dict["lparam_alpha"] = lattice_parameters[3]
        self.experiment_file_dict["lparam_beta"] = lattice_parameters[4]
        self.experiment_file_dict["lparam_gama"] = lattice_parameters[5]

    def set_energy(self, energy_to_set: float) -> float:
        """Sets the energy to the .Experiment file"""
        offset = (
            self.experiment_file_dict["beamline_pvs"]["energy"]["value"] - energy_to_set
        )
        self.experiment_file_dict["energy_offset"] = offset
        return offset

    def set_u_and_ub_based_in_idir_ndir(self, idir: list, ndir: list) -> tuple:
        """
        Calculate U and UB from idir and ndirm using a standard diffractometer angles.
        This will be used as the main "idir" and "ndir" but works better setting the
        U and UB matrix from that then using the raw idir, ndir.
        """
        exp = self.build_exp()
        hkl1 = idir
        angs1 = [0, 5, 0, -90, 0, 10]
        hkl2 = ndir
        angs2 = [0, 5, 90, 0, 0, 10]
        U, UB = exp.calc_U_2HKL(hkl1, angs1, hkl2, angs2)

        self.experiment_file_dict["IDir_print"] = idir
        self.experiment_file_dict["NDir_print"] = ndir
        self.experiment_file_dict["U_mat"] = U.tolist()
        self.experiment_file_dict["UB_mat"] = UB.tolist()
        return U, UB

    def set_material(self, sample: str) -> None:
        """Sets a new material from a predefined xrayutilities sample or a new sample from lattice parameters"""
        self.experiment_file_dict["Material"] = sample
        exp = self.build_exp()
        predef = exp.predefined_samples
        if (
            sample not in predef
            and sample not in self.experiment_file_dict["user_samples"].keys()
        ):
            nsamp_dict = self.experiment_file_dict["user_samples"]
            nsamp_dict[sample] = [
                self.experiment_file_dict["lparam_a"],
                self.experiment_file_dict["lparam_b"],
                self.experiment_file_dict["lparam_c"],
                self.experiment_file_dict["lparam_alpha"],
                self.experiment_file_dict["lparam_beta"],
                self.experiment_file_dict["lparam_gama"],
            ]
            self.experiment_file_dict["user_samples"] = nsamp_dict
        if (
            self.experiment_file_dict["Material"]
            in self.experiment_file_dict["user_samples"].keys()
        ):
            exp.set_material(
                self.experiment_file_dict["Material"],
                *self.experiment_file_dict["user_samples"][
                    self.experiment_file_dict["Material"]
                ]
            )
        else:
            exp.set_material(
                self.experiment_file_dict["Material"],
                self.experiment_file_dict["lparam_a"],
                self.experiment_file_dict["lparam_b"],
                self.experiment_file_dict["lparam_c"],
                self.experiment_file_dict["lparam_alpha"],
                self.experiment_file_dict["lparam_beta"],
                self.experiment_file_dict["lparam_gama"],
            )
        UB = exp.calcUB()
        # yaml doesn't handle numpy arrays well, so using python's list is a better choice
        self.experiment_file_dict["UB_mat"] = UB.tolist()

    def set_rdir(self, rdir: np.array):
        """Sets RDir"""
        self.experiment_file_dict["RDir"] = rdir

    def set_sample_or(self, sample_or: str) -> None:
        """Sets sample orientation"""
        self.experiment_file_dict["Sampleor"] = sample_or

    def set_simulated_motors(self):
        """Use simulated motors for all DAF functions"""
        self.experiment_file_dict["simulated"] = True

    def set_real_motors(self):
        """Use real motors for all DAF functions"""
        self.experiment_file_dict["simulated"] = False

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        if self.parsed_args_dict["lattice_parameters"]:
            self.set_lattice_parameters(self.parsed_args_dict["lattice_parameters"])
        if self.parsed_args_dict["energy"]:
            self.set_energy(self.parsed_args_dict["energy"])
        if self.parsed_args_dict["rdir"]:
            self.set_rdir(self.parsed_args_dict["rdir"])
        if (
            self.parsed_args_dict["idir_print"] is not None
            and self.parsed_args_dict["ndir_print"] is not None
        ):
            self.set_u_and_ub_based_in_idir_ndir(
                self.parsed_args_dict["idir_print"], self.parsed_args_dict["ndir_print"]
            )
        if self.parsed_args_dict["sample"]:
            self.set_material(self.parsed_args_dict["sample"])
        if self.parsed_args_dict["sample_orientation"]:
            self.set_sample_or(self.parsed_args_dict["sample_orientation"])
        if self.parsed_args_dict["simulated"]:
            self.set_simulated_motors()
        if self.parsed_args_dict["real"]:
            self.set_real_motors()
        self.write_to_experiment_file(self.experiment_file_dict)


@daf_log
def main() -> None:
    obj = ExperimentConfiguration()
    obj.run_cmd()


if __name__ == "__main__":
    main()
