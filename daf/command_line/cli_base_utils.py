from abc import abstractmethod
import argparse as ap
import numpy as np

from daf.core.main import DAF
import daf.utils.dafutilities as du
from daf.core.matrix_utils import (
    calculate_rotation_matrix_from_diffractometer_angles,
    calculate_pseudo_angle_from_motor_angles,
)


class CLIBase:
    def __init__(self):
        self.experiment_file_dict = self.read_experiment_file()

    @staticmethod
    def read_experiment_file():
        return du.read()

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
        mu_bound = self.experiment_file_dict["bound_Mu"]
        eta_bound = self.experiment_file_dict["bound_Eta"]
        chi_bound = self.experiment_file_dict["bound_Chi"]
        phi_bound = self.experiment_file_dict["bound_Phi"]
        nu_bound = self.experiment_file_dict["bound_Nu"]
        del_bound = self.experiment_file_dict["bound_Del"]
        self.en = (
            self.experiment_file_dict["PV_energy"]
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
            Mu=self.experiment_file_dict["cons_Mu"],
            Eta=self.experiment_file_dict["cons_Eta"],
            Chi=self.experiment_file_dict["cons_Chi"],
            Phi=self.experiment_file_dict["cons_Phi"],
            Nu=self.experiment_file_dict["cons_Nu"],
            Del=self.experiment_file_dict["cons_Del"],
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
            self.experiment_file_dict["Mu"],
            self.experiment_file_dict["Eta"],
            self.experiment_file_dict["Chi"],
            self.experiment_file_dict["Phi"],
            self.experiment_file_dict["Nu"],
            self.experiment_file_dict["Del"],
        )
        return hkl

    def get_pseudo_angles_from_motor_angles(self) -> dict:
        """Calculate pseudo-angles from diffractometer angles"""
        pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
            self.experiment_file_dict["Mu"],
            self.experiment_file_dict["Eta"],
            self.experiment_file_dict["Chi"],
            self.experiment_file_dict["Phi"],
            self.experiment_file_dict["Nu"],
            self.experiment_file_dict["Del"],
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
            self.experiment_file_dict["Mu"],
            self.experiment_file_dict["Eta"],
            self.experiment_file_dict["Chi"],
            self.experiment_file_dict["Phi"],
            self.experiment_file_dict["Nu"],
            self.experiment_file_dict["Del"],
        ]
        self.exp.set_hkl(hkl)
        self.exp(sv=startvalue)
        error = self.exp.qerror
        return error

    def get_angles_from_calculated_exp(self) -> dict:
        """Get all angles and pseudo-angles based on a previous calculation, return a dicts"""
        angs = self.exp.export_angles()
        exp_dict = {
            "Mu": angs[0],
            "Eta": angs[1],
            "Chi": angs[2],
            "Phi": angs[3],
            "Nu": angs[4],
            "Del": angs[5],
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

    def write_to_experiment_file(self, dict_to_write, is_str=False):
        """Write to the .Experiment file based on a inputted dict"""
        for j, k in dict_to_write.items():
            if j in self.experiment_file_dict and k is not None:
                if isinstance(k, np.ndarray):
                    self.experiment_file_dict[j] = k.tolist()
                elif isinstance(k, list):
                    self.experiment_file_dict[j] = k
                elif is_str:
                    self.experiment_file_dict[j] = str(k)
                else:
                    self.experiment_file_dict[j] = float(k)
        du.write(self.experiment_file_dict)

    @abstractmethod
    def run_cmd(self, arguments: dict):
        """
        Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface
        """
        pass
