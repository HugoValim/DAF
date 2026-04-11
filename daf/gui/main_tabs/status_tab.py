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

    _LAUNCHER_BUTTONS = (
        ("set_mode_launcher", "open_mode_window"),
        ("experiment_launcher", "open_experiment_window"),
        ("sample_launcher", "open_sample_window"),
        ("ub_launcher", "open_ub_window"),
    )
    _MODE_LABELS = ("mode_1_label", "mode_2_label", "mode_3_label", "mode_4_label", "mode_5_label")
    _CONS_LABELS = ("cons_1_label", "cons_2_label", "cons_3_label", "cons_4_label", "cons_5_label")
    _EXP_LABELS = ("wl_label", "energy_label", "idir_label", "ndir_label", "rdir_label")
    _SAMPLE_LABELS = ("a_label", "b_label", "c_label", "alpha_label", "beta_label", "gamma_label")

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
        for btn_name, _ in self._LAUNCHER_BUTTONS:
            getattr(self, btn_name).setIcon(QIcon(Icons.pen))

    def make_connections(self):
        for btn_name, method_name in self._LAUNCHER_BUTTONS:
            getattr(self, btn_name).clicked.connect(getattr(self, method_name))

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
        mode_text = "MODE: " + "".join(str(m) for m in mode_num)
        self.mode_label.setText(mode_text)
        for label, val in zip(self._MODE_LABELS, mode):
            getattr(self, label).setText(val)
        for label, val in zip(self._CONS_LABELS, (c[1] for c in cons)):
            getattr(self, label).setText(str(val))

    def update_experiment(self, exp_list):
        """Update status experiment label"""
        for label, val in zip(self._EXP_LABELS, exp_list[1:]):
            getattr(self, label).setText(str(val))

    def update_sample(self, samp_info):
        """Update sample info label"""
        self.sample.setText(str(samp_info[0]))
        for label, val in zip(self._SAMPLE_LABELS, samp_info[1:]):
            getattr(self, label).setText(format_5_dec(str(val)))

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
