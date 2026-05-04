from abc import abstractmethod
import argparse as ap
import sys

import numpy as np

from daf.core.main import DAF
import daf.utils.dafutilities as du
from daf.core.matrix_utils import (
    calculate_pseudo_angle_from_motor_angles,
)


class DevNull:
    """Supress errors for the user"""

    def write(self, msg):
        pass


class CLIBase:
    """Base class to be inherited by all command line classes"""

    # Motor names in canonical order
    _MOTOR_NAMES = ("mu", "eta", "chi", "phi", "nu", "del")

    # Mapping of export_angles() index to name
    _ANGLE_EXPORT_NAMES = (
        "mu",
        "eta",
        "chi",
        "phi",
        "nu",
        "del",
        "twotheta",
        "theta",
        "alpha",
        "qaz",
        "naz",
        "tau",
        "psi",
        "beta",
        "omega",
        "hklnow",
    )

    def __init__(self, read: bool = True):
        self.io = du.DAFIO(read=read)
        if read:
            self.read_experiment_file()
        # sys.stderr = DevNull()

    def read_experiment_file(self):
        self.experiment_file_dict = self.io.read()
        return self.experiment_file_dict

    def parse_command_line(self):
        self.parser = ap.ArgumentParser(
            formatter_class=ap.RawDescriptionHelpFormatter,
            description=self.DESC,
            epilog=self.EPI,
        )

    def _get_motor_bounds(self) -> dict:
        """Extract motor bounds from experiment file as a dict."""
        return {
            m: self.experiment_file_dict["motors"][m]["bounds"]
            for m in self._MOTOR_NAMES
        }

    def _get_constraints_dict(self) -> dict:
        """Extract constraints from experiment file as a dict."""
        cons_keys = (
            "cons_mu",
            "cons_eta",
            "cons_chi",
            "cons_phi",
            "cons_nu",
            "cons_del",
            "cons_alpha",
            "cons_beta",
            "cons_psi",
            "cons_omega",
            "cons_qaz",
            "cons_naz",
        )
        return {k: self.experiment_file_dict[k] for k in cons_keys}

    def _get_motor_values(self) -> dict:
        """Extract current motor values from experiment file as a dict."""
        return {
            m: self.experiment_file_dict["motors"][m]["value"]
            for m in self._MOTOR_NAMES
        }

    def build_exp(self) -> DAF:
        """Instantiate an instance of DAF main class setting all necessary parameters"""
        mode = [int(i) for i in self.experiment_file_dict["Mode"]]
        U = np.array(self.experiment_file_dict["U_mat"])
        idir = self.experiment_file_dict["IDir_print"]
        ndir = self.experiment_file_dict["NDir_print"]
        rdir = self.experiment_file_dict["RDir"]
        bounds_dict = self._get_motor_bounds()
        self.en = (
            self.experiment_file_dict["beamline_pvs"]["energy"]["value"]
            - self.experiment_file_dict["energy_offset"]
        )

        exp = DAF(*mode)
        material = self.experiment_file_dict["Material"]
        if material in self.experiment_file_dict["user_samples"]:
            exp.set_material(
                material, *self.experiment_file_dict["user_samples"][material]
            )
        else:
            exp.set_material(
                material,
                self.experiment_file_dict["lparam_a"],
                self.experiment_file_dict["lparam_b"],
                self.experiment_file_dict["lparam_c"],
                self.experiment_file_dict["lparam_alpha"],
                self.experiment_file_dict["lparam_beta"],
                self.experiment_file_dict["lparam_gama"],
            )

        exp.set_exp_conditions(
            idir=idir,
            ndir=ndir,
            rdir=rdir,
            en=self.en,
            sampleor=self.experiment_file_dict["Sampleor"],
        )
        exp.set_circle_constrain(**bounds_dict)
        exp.set_constraints(**self._get_constraints_dict())

        exp.set_U(U)
        exp.build_xrd_experiment()
        exp.build_bounds()

        return exp

    def calculate_hkl_from_angles(self) -> np.array:
        """Calculate current HKL position from diffractometer angles"""
        motor_vals = self._get_motor_values()
        hkl = self.exp.calc_from_angs(
            motor_vals["mu"],
            motor_vals["eta"],
            motor_vals["chi"],
            motor_vals["phi"],
            motor_vals["nu"],
            motor_vals["del"],
        )
        return hkl

    def get_pseudo_angles_from_motor_angles(self) -> dict:
        """Calculate pseudo-angles from diffractometer angles"""
        motor_vals = self._get_motor_values()
        pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
            motor_vals["mu"],
            motor_vals["eta"],
            motor_vals["chi"],
            motor_vals["phi"],
            motor_vals["nu"],
            motor_vals["del"],
            self.exp.samp,
            self.calculate_hkl_from_angles(),
            self.exp.lam,
            self.exp.nref,
            self.exp.U,
        )

        return pseudo_angles_dict

    def calculate_hkl(self, hkl: list) -> float:
        """Calculate the angles to a given HKL"""
        motor_vals = self._get_motor_values()
        startvalue = [motor_vals[m] for m in self._MOTOR_NAMES]
        self.exp.set_hkl(hkl)
        self.exp(start_values=startvalue)
        error = self.exp.qerror
        return error

    def get_angles_from_calculated_exp(self) -> dict:
        """Get all angles and pseudo-angles based on a previous calculation, return a dicts"""
        angs = self.exp.export_angles()
        return {name: angs[i] for i, name in enumerate(self._ANGLE_EXPORT_NAMES)}

    def write_motors_bounds_to_experiment_file(self, dict_to_write: dict) -> None:
        """Write motor bounds to the experiment file"""
        for key in self.experiment_file_dict["motors"].keys():
            if key in dict_to_write.keys() and dict_to_write[key] is not None:
                self.experiment_file_dict["motors"][key]["bounds"] = dict_to_write[key]

    def write_motors_to_experiment_file(self, dict_to_write: dict) -> None:
        """Write motor set point to the experiment file"""
        for key in self.experiment_file_dict["motors"].keys():
            if key in dict_to_write.keys() and dict_to_write[key] is not None:
                self.experiment_file_dict["motors"][key]["value"] = float(
                    dict_to_write[key]
                )

    def update_experiment_file(self, dict_to_write: dict, is_str: bool = False) -> None:
        """Update self.experiment_file_dict based on user inputs"""
        for j, k in dict_to_write.items():
            if j in self.experiment_file_dict and k is not None:
                if isinstance(k, np.ndarray):
                    self.experiment_file_dict[j] = k.tolist()
                elif isinstance(k, list):
                    self.experiment_file_dict[j] = k
                elif is_str:
                    self.experiment_file_dict[j] = str(k)
                elif isinstance(k, str) and not k.isnumeric():
                    self.experiment_file_dict[j] = str(k)
                else:
                    self.experiment_file_dict[j] = float(k)

    def write_to_experiment_file(
        self,
        dict_to_write: dict,
        is_motor_set_point: bool = False,
        is_motor_bounds: bool = False,
        write=True,
    ):
        """Write to the .Experiment file based on a inputted dict"""
        if is_motor_set_point:
            self.write_motors_to_experiment_file(dict_to_write)
        if is_motor_bounds:
            self.write_motors_bounds_to_experiment_file(dict_to_write)
        if write:
            self.io.write(self.experiment_file_dict)

    @abstractmethod
    def run_cmd(self):
        """
        Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface
        """
        pass
