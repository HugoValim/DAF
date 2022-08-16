import time

import numpy as np
import yaml
from PyQt5.QtCore import QObject, pyqtSignal

# DAF GUIs imports
import daf.utils.dafutilities as du
from daf.core.main import DAF
from daf.core.matrix_utils import calculate_pseudo_angle_from_motor_angles


DEFAULT = ".Experiment"


class Worker(QObject):
    finished = pyqtSignal()
    update_labels = pyqtSignal()
    io = du.DAFIO()

    def get_experiment_data(self, filepath=DEFAULT):
        with open(filepath) as file:
            data = yaml.safe_load(file)
        return data

    def format_decimals(self, x):
        if type(x) == float:
            return "{:.5f}".format(float(x))  # format float with 5 decimals
        else:
            result = []
            for i in x:
                result.append("{:.5f}".format(float(i)))
            return result

    def call_update(self):
        data = self.get_experiment_data()
        if data != self.data:
            self.update()
            self.data = data

    def update(self):
        dict_args = self.io.read()
        U = np.array(dict_args["U_mat"])
        U_print = np.array(
            [
                self.format_decimals(U[0]),
                self.format_decimals(U[1]),
                self.format_decimals(U[2]),
            ]
        )
        UB = np.array(dict_args["UB_mat"])
        UB_print = np.array(
            [
                self.format_decimals(UB[0]),
                self.format_decimals(UB[1]),
                self.format_decimals(UB[2]),
            ]
        )
        mode = [int(i) for i in dict_args["Mode"]]
        idir = dict_args["IDir_print"]
        ndir = dict_args["NDir_print"]
        rdir = dict_args["RDir"]
        exp = DAF(*mode)
        exp.set_exp_conditions(
            idir=idir,
            ndir=ndir,
            rdir=rdir,
            en=dict_args["beamline_pvs"]["energy"]["value"]
            - dict_args["energy_offset"],
            sampleor=dict_args["Sampleor"],
        )
        if dict_args["Material"] in dict_args["user_samples"].keys():
            exp.set_material(
                dict_args["Material"], *dict_args["user_samples"][dict_args["Material"]]
            )

        else:
            exp.set_material(
                dict_args["Material"],
                dict_args["lparam_a"],
                dict_args["lparam_b"],
                dict_args["lparam_c"],
                dict_args["lparam_alpha"],
                dict_args["lparam_beta"],
                dict_args["lparam_gama"],
            )

        # exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
        exp.set_U(U)
        exp.set_constraints(
            Mu=dict_args["cons_mu"],
            Eta=dict_args["cons_eta"],
            Chi=dict_args["cons_chi"],
            Phi=dict_args["cons_phi"],
            Nu=dict_args["cons_nu"],
            Del=dict_args["cons_del"],
            alpha=dict_args["cons_alpha"],
            beta=dict_args["cons_beta"],
            psi=dict_args["cons_psi"],
            omega=dict_args["cons_omega"],
            qaz=dict_args["cons_qaz"],
            naz=dict_args["cons_naz"],
        )
        exp.build_xrd_experiment()
        exp.build_bounds()

        hklnow = exp.calc_from_angs(
            dict_args["motors"]["mu"]["value"],
            dict_args["motors"]["eta"]["value"],
            dict_args["motors"]["chi"]["value"],
            dict_args["motors"]["phi"]["value"],
            dict_args["motors"]["nu"]["value"],
            dict_args["motors"]["del"]["value"],
        )

        pseudo_dict = calculate_pseudo_angle_from_motor_angles(
            dict_args["motors"]["mu"]["value"],
            dict_args["motors"]["eta"]["value"],
            dict_args["motors"]["chi"]["value"],
            dict_args["motors"]["phi"]["value"],
            dict_args["motors"]["nu"]["value"],
            dict_args["motors"]["del"]["value"],
            exp.samp,
            hklnow,
            exp.lam,
            exp.nref,
            exp.U,
        )

        hklnow = list(hklnow)

        mode, mode_num, cons, exp_list, samp_info = exp.show(sh="gui")

        bounds = {
            "mu": dict_args["motors"]["mu"]["bounds"],
            "eta": dict_args["motors"]["eta"]["bounds"],
            "chi": dict_args["motors"]["chi"]["bounds"],
            "phi": dict_args["motors"]["phi"]["bounds"],
            "nu": dict_args["motors"]["nu"]["bounds"],
            "del": dict_args["motors"]["del"]["bounds"],
        }

        self.data_to_update = {
            "hklnow": hklnow,
            "mode": mode,
            "mode_num": mode_num,
            "cons": cons,
            "exp_list": exp_list,
            "samp_info": samp_info,
            "U": U_print,
            "UB": UB_print,
            "bounds": bounds,
            "pseudo_dict": pseudo_dict,
            "dargs": dict_args,
        }

    def run(self):
        """Long-running task."""
        while True:
            self.update()
            self.update_labels.emit()
            time.sleep(1)
