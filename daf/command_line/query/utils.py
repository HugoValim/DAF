from abc import abstractmethod
import numpy as np

from daf.core.main import DAF
import daf.utils.dafutilities as du


class QueryBase:
    def __init__(self):
        self.experiment_file_dict = du.read()

    def build_exp(self):
        """Instantiate an instance of DAF main class setting all necessary parameters"""
        mode = [int(i) for i in self.experiment_file_dict["Mode"]]
        U = np.array(self.experiment_file_dict["U_mat"])
        idir = self.experiment_file_dict["IDir_print"]
        ndir = self.experiment_file_dict["NDir_print"]
        rdir = self.experiment_file_dict["RDir"]
        Mu_bound = self.experiment_file_dict["bound_Mu"]
        Eta_bound = self.experiment_file_dict["bound_Eta"]
        Chi_bound = self.experiment_file_dict["bound_Chi"]
        Phi_bound = self.experiment_file_dict["bound_Phi"]
        Nu_bound = self.experiment_file_dict["bound_Nu"]
        Del_bound = self.experiment_file_dict["bound_Del"]

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
            en=self.experiment_file_dict["PV_energy"]
            - self.experiment_file_dict["energy_offset"],
            sampleor=self.experiment_file_dict["Sampleor"],
        )
        exp.set_circle_constrain(
            Mu=Mu_bound,
            Eta=Eta_bound,
            Chi=Chi_bound,
            Phi=Phi_bound,
            Nu=Nu_bound,
            Del=Del_bound,
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

        return exp

    @abstractmethod
    def run_cmd(self, arguments):
        pass
