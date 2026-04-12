#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.print_utils import format_5_decimals
from daf.utils.decorators import cli_decorator
from daf.command_line.cli_base_utils import CLIBase
from daf.utils import dafutilities as du


class ExperimentConfiguration(CLIBase):
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

    # Standard angles for idir/ndir-based UB calculation
    _IDIR_ANGLES = (0, 5, 0, -90, 0, 10)
    _NDIR_ANGLES = (0, 5, 90, 0, 0, 10)

    def set_lattice_parameters(self, lattice_parameters: list) -> None:
        """Set lattice parameters from a 6-element list."""
        lp_keys = (
            "lparam_a",
            "lparam_b",
            "lparam_c",
            "lparam_alpha",
            "lparam_beta",
            "lparam_gama",
        )
        for key, val in zip(lp_keys, lattice_parameters):
            self.experiment_file_dict[key] = val

    def set_energy(self, energy_to_set: float) -> float:
        """Sets the energy to the .Experiment file"""
        offset = (
            self.experiment_file_dict["beamline_pvs"]["energy"]["value"] - energy_to_set
        )
        self.experiment_file_dict["energy_offset"] = offset
        return offset

    def set_u_and_ub_based_in_idir_ndir(self, idir: list, ndir: list) -> tuple:
        """Calculate U and UB from idir/ndir using standard diffractometer angles."""
        exp = self.build_exp()
        U, UB = exp.calc_U_2HKL(idir, self._IDIR_ANGLES, ndir, self._NDIR_ANGLES)

        self.experiment_file_dict["IDir_print"] = idir
        self.experiment_file_dict["NDir_print"] = ndir
        self.experiment_file_dict["U_mat"] = U.tolist()
        self.experiment_file_dict["UB_mat"] = UB.tolist()
        return U, UB

    def set_material(self, sample: str) -> None:
        """Set material from predefined xrayutilities sample or user-defined lattice params."""
        efd = self.experiment_file_dict
        efd["Material"] = sample
        exp = self.build_exp()
        predef = exp.predefined_samples

        lp = [
            efd["lparam_a"],
            efd["lparam_b"],
            efd["lparam_c"],
            efd["lparam_alpha"],
            efd["lparam_beta"],
            efd["lparam_gama"],
        ]

        if sample not in predef and sample not in efd["user_samples"]:
            efd["user_samples"][sample] = lp

        if sample in efd["user_samples"]:
            exp.set_material(sample, *efd["user_samples"][sample])
        else:
            exp.set_material(sample, *lp)

        efd["UB_mat"] = exp.calcUB().tolist()

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


@cli_decorator
def main() -> None:
    obj = ExperimentConfiguration()
    obj.run_cmd()


if __name__ == "__main__":
    main()
