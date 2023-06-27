from os import path

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QWidget

import daf.gui.windows.set_mode as set_mode
import daf.gui.windows.experiment as experiment
import daf.gui.windows.sample as sample
import daf.gui.windows.ub as ub


from daf.gui.utils import format_5_dec, Icons


class StatusTab(QWidget):
    def __init__(self, dafio):
        super().__init__()
        uic.loadUi(self.ui_filepath(), self)
        self.set_icons()
        self.make_connections()
        self.update_dict = None
        self.io = dafio

    def ui_filename(self):
        return "status_tab.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def set_icons(self):
        """Set used icons"""
        self.set_mode_launcher.setIcon(QIcon(Icons.pen))
        self.experiment_launcher.setIcon(QIcon(Icons.pen))
        self.sample_launcher.setIcon(QIcon(Icons.pen))
        self.ub_launcher.setIcon(QIcon(Icons.pen))

    def make_connections(self):
        self.set_mode_launcher.clicked.connect(self.open_mode_window)
        self.experiment_launcher.clicked.connect(self.open_experiment_window)
        self.sample_launcher.clicked.connect(self.open_sample_window)
        self.ub_launcher.clicked.connect(self.open_ub_window)

    def open_mode_window(self):
        self.mode_window = set_mode.MyDisplay(self.update_dict)
        self.mode_window.show()

    def open_experiment_window(self):
        self.experiment_window = experiment.MyDisplay(self.update_dict)
        self.experiment_window.show()

    def open_sample_window(self):
        self.sample_window = sample.MyDisplay(self.update_dict)
        self.sample_window.show()

    def open_ub_window(self):
        self.ub_window = ub.MyDisplay()
        self.ub_window.show()

    def update(self, update_dict: dict = None) -> None:
        self.update_dict = update_dict
        mode, mode_num, cons, exp_list, samp_info = update_dict["exp"].show(sh="gui")
        self.update_mode(mode_num, mode, cons)
        self.update_experiment(exp_list)
        self.update_sample(samp_info)
        self.update_u_and_ub(update_dict["default"])

    def update_mode(self, mode_num, mode, cons):
        """Update status mode label"""
        mode_text = (
            "MODE: "
            + str(mode_num[0])
            + str(mode_num[1])
            + str(mode_num[2])
            + str(mode_num[3])
            + str(mode_num[4])
        )
        self.mode_label.setText(mode_text)
        self.mode_1_label.setText(mode[0])
        self.mode_2_label.setText(mode[1])
        self.mode_3_label.setText(mode[2])
        self.mode_4_label.setText(mode[3])
        self.mode_5_label.setText(mode[4])

        # Update status constraints label
        self.cons_1_label.setText(str(cons[0][1]))
        self.cons_2_label.setText(str(cons[1][1]))
        self.cons_3_label.setText(str(cons[2][1]))
        self.cons_4_label.setText(str(cons[3][1]))
        self.cons_5_label.setText(str(cons[4][1]))

    def update_experiment(self, exp_list):
        """Update status experiment label"""
        self.wl_label.setText(str(exp_list[1]))
        self.energy_label.setText(str(exp_list[2]))
        self.idir_label.setText(str(exp_list[3]))
        self.ndir_label.setText(str(exp_list[4]))
        self.rdir_label.setText(str(exp_list[5]))
        # self..setText(str(exp_list[0]))

    def update_sample(self, samp_info):
        """Update sample info label"""
        self.sample.setText(str(samp_info[0]))
        self.a_label.setText(format_5_dec(str(samp_info[1])))
        self.b_label.setText(format_5_dec(str(samp_info[2])))
        self.c_label.setText(format_5_dec(str(samp_info[3])))
        self.alpha_label.setText(format_5_dec(str(samp_info[4])))
        self.beta_label.setText(format_5_dec(str(samp_info[5])))
        self.gamma_label.setText(format_5_dec(str(samp_info[6])))

    def set_label_text_from_eval(self, label: str, text: str) -> None:
        "Update the label text after evaluating a string"
        eval(label).setText(str(format_5_dec(text)))

    def update_u_and_ub(self, update_dict):
        """Update status Matrixes"""
        u_label_pref = "self.u_"
        u_label_suf = "_label"
        ub_label_pref = "self.ub_"
        ub_label_suf = "_label"

        for i in range(3):
            for j in range(3):
                u_label_now = u_label_pref + str(i) + str(j) + u_label_suf
                ub_label_now = ub_label_pref + str(i) + str(j) + ub_label_suf
                self.set_label_text_from_eval(u_label_now, update_dict["U_mat"][i][j])
                self.set_label_text_from_eval(ub_label_now, update_dict["UB_mat"][i][j])
