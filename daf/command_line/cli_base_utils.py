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

    def __init__(self):
        self.io = du.DAFIO()
        self.experiment_file_dict = self.read_experiment_file()
        # sys.stderr = DevNull()

    def read_experiment_file(self):
        return self.io.read()

    def parse_command_line(self):
        self.parser = ap.ArgumentParser(
            formatter_class=ap.RawDescriptionHelpFormatter,
            description=self.DESC,
            epilog=self.EPI,
        )

    def build_exp(self) -> DAF:
        """Instantiate an instance of DAF main class setting all necessary parameters"""
        mode = [int(i) for i in self.experiment_file_dict["Mode"]]
        U = np.array(self.experiment_file_dict["U_mat"])
        idir = self.experiment_file_dict["IDir_print"]
        ndir = self.experiment_file_dict["NDir_print"]
        rdir = self.experiment_file_dict["RDir"]
        mu_bound = self.experiment_file_dict["motors"]["mu"]["bounds"]
        eta_bound = self.experiment_file_dict["motors"]["eta"]["bounds"]
        chi_bound = self.experiment_file_dict["motors"]["chi"]["bounds"]
        phi_bound = self.experiment_file_dict["motors"]["phi"]["bounds"]
        nu_bound = self.experiment_file_dict["motors"]["nu"]["bounds"]
        del_bound = self.experiment_file_dict["motors"]["del"]["bounds"]
        self.en = (
            self.experiment_file_dict["beamline_pvs"]["energy"]["value"]
            - self.experiment_file_dict["energy_offset"]
        )

        exp = DAF(*mode)
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

        exp.set_exp_conditions(
            idir=idir,
            ndir=ndir,
            rdir=rdir,
            en=self.en,
            sampleor=self.experiment_file_dict["Sampleor"],
        )
        exp.set_circle_constrain(
            Mu=mu_bound,
            Eta=eta_bound,
            Chi=chi_bound,
            Phi=phi_bound,
            Nu=nu_bound,
            Del=del_bound,
        )

        exp.set_constraints(
            Mu=self.experiment_file_dict["cons_mu"],
            Eta=self.experiment_file_dict["cons_eta"],
            Chi=self.experiment_file_dict["cons_chi"],
            Phi=self.experiment_file_dict["cons_phi"],
            Nu=self.experiment_file_dict["cons_nu"],
            Del=self.experiment_file_dict["cons_del"],
            alpha=self.experiment_file_dict["cons_alpha"],
            beta=self.experiment_file_dict["cons_beta"],
            psi=self.experiment_file_dict["cons_psi"],
            omega=self.experiment_file_dict["cons_omega"],
            qaz=self.experiment_file_dict["cons_qaz"],
            naz=self.experiment_file_dict["cons_naz"],
        )

        exp.set_U(U)
        exp.build_xrd_experiment()
        exp.build_bounds()

        return exp

    def calculate_hkl_from_angles(self) -> np.array:
        """Calculate current HKL position from diffractometer angles"""
        hkl = self.exp.calc_from_angs(
            self.experiment_file_dict["motors"]["mu"]["value"],
            self.experiment_file_dict["motors"]["eta"]["value"],
            self.experiment_file_dict["motors"]["chi"]["value"],
            self.experiment_file_dict["motors"]["phi"]["value"],
            self.experiment_file_dict["motors"]["nu"]["value"],
            self.experiment_file_dict["motors"]["del"]["value"],
        )
        return hkl

    def get_pseudo_angles_from_motor_angles(self) -> dict:
        """Calculate pseudo-angles from diffractometer angles"""
        pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
            self.experiment_file_dict["motors"]["mu"]["value"],
            self.experiment_file_dict["motors"]["eta"]["value"],
            self.experiment_file_dict["motors"]["chi"]["value"],
            self.experiment_file_dict["motors"]["phi"]["value"],
            self.experiment_file_dict["motors"]["nu"]["value"],
            self.experiment_file_dict["motors"]["del"]["value"],
            self.exp.samp,
            self.calculate_hkl_from_angles(),
            self.exp.lam,
            self.exp.nref,
            self.exp.U,
        )

        return pseudo_angles_dict

    def calculate_hkl(self, hkl: list) -> float:
        """Calculate the angles to a given HKL"""
        startvalue = [
            self.experiment_file_dict["motors"]["mu"]["value"],
            self.experiment_file_dict["motors"]["eta"]["value"],
            self.experiment_file_dict["motors"]["chi"]["value"],
            self.experiment_file_dict["motors"]["phi"]["value"],
            self.experiment_file_dict["motors"]["nu"]["value"],
            self.experiment_file_dict["motors"]["del"]["value"],
        ]
        self.exp.set_hkl(hkl)
        self.exp(sv=startvalue)
        error = self.exp.qerror
        return error

    def get_angles_from_calculated_exp(self) -> dict:
        """Get all angles and pseudo-angles based on a previous calculation, return a dicts"""
        angs = self.exp.export_angles()
        exp_dict = {
            "mu": angs[0],
            "eta": angs[1],
            "chi": angs[2],
            "phi": angs[3],
            "nu": angs[4],
            "del": angs[5],
            "twotheta": angs[6],
            "theta": angs[7],
            "alpha": angs[8],
            "qaz": angs[9],
            "naz": angs[10],
            "tau": angs[11],
            "psi": angs[12],
            "beta": angs[13],
            "omega": angs[14],
            "hklnow": angs[15],
        }
        return exp_dict

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
    ):
        """Write to the .Experiment file based on a inputted dict"""
        if is_motor_set_point:
            self.write_motors_to_experiment_file(dict_to_write)
        if is_motor_bounds:
            self.write_motors_bounds_to_experiment_file(dict_to_write)
        self.io.write(self.experiment_file_dict)

    @abstractmethod
    def run_cmd(self):
        """
        Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface
        """
        pass
