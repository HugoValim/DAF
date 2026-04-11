from os import path
import subprocess

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QApplication, QWidget
from daf.gui.utils import Icons, center_screen, format_5_dec
import xrayutilities as xu


class MyDisplay(QWidget):

    _VECTOR_PREFIXES = ("i", "n", "r")
    _VECTOR_NAMES = {"i": "idir", "n": "ndir", "r": "rdir"}

    def __init__(self, update_dict: dict):
        super().__init__()
        self.app = QApplication.instance()
        uic.loadUi(self.ui_filepath(), self)
        center_screen(self)
        self.update_dict = update_dict
        self.set_labels()
        self.set_tab_order()
        self.set_icons()
        self.make_connections()

    def ui_filename(self):
        return "experiment.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def set_icons(self):
        """Set used icons"""
        for prefix in self._VECTOR_PREFIXES:
            btn = getattr(self, f"pushButton_{prefix}dir")
            btn.setIcon(QIcon(Icons.check))

    def set_tab_order(self):
        """Set the correct order when clicking tab"""
        self.setTabOrder(self.lineEdit_e_wl, self.comboBox_e_wl)
        self.setTabOrder(self.comboBox_e_wl, self.pushButton_energy)
        self.setTabOrder(self.pushButton_energy, self.lineEdit_i_1)
        self.setTabOrder(self.lineEdit_i_1, self.lineEdit_i_2)
        self.setTabOrder(self.lineEdit_i_2, self.lineEdit_i_3)
        self.setTabOrder(self.lineEdit_i_3, self.pushButton_idir)
        self.setTabOrder(self.pushButton_idir, self.lineEdit_n_1)
        self.setTabOrder(self.lineEdit_n_1, self.lineEdit_n_2)
        self.setTabOrder(self.lineEdit_n_2, self.lineEdit_n_3)
        self.setTabOrder(self.lineEdit_n_3, self.pushButton_ndir)
        self.setTabOrder(self.pushButton_ndir, self.lineEdit_r_1)
        self.setTabOrder(self.lineEdit_r_1, self.lineEdit_r_2)
        self.setTabOrder(self.lineEdit_r_2, self.lineEdit_r_3)
        self.setTabOrder(self.lineEdit_r_3, self.pushButton_rdir)
        self.setTabOrder(self.pushButton_rdir, self.lineEdit_e_wl)

    def make_connections(self):
        """Make the needed connections"""
        self.comboBox_e_wl.currentTextChanged.connect(self.on_combobox_en_changed)
        self.pushButton_energy.clicked.connect(self.set_energy)
        for prefix in self._VECTOR_PREFIXES:
            btn = getattr(self, f"pushButton_{prefix}dir")
            btn.clicked.connect(getattr(self, f"set_{prefix}dir"))

    def on_combobox_en_changed(self):
        """Switch the energy lineEdit between energy and wave length based in the QComboBox"""
        dict_args = self.update_dict["default"]
        en = dict_args["beamline_pvs"]["energy"]["value"] - dict_args["energy_offset"]
        if str(self.comboBox_e_wl.currentText()).lower() == "energy":
            self.lineEdit_e_wl.setText(str(en))
        elif str(self.comboBox_e_wl.currentText()).lower() == "wl":
            wl = xu.en2lam(en)
            self.lineEdit_e_wl.setText(str(format_5_dec(wl)))

    def set_labels(self):
        """Set default labels"""
        dict_args = self.update_dict["default"]
        en = dict_args["beamline_pvs"]["energy"]["value"] - dict_args["energy_offset"]
        if str(self.comboBox_e_wl.currentText()).lower() == "energy":
            self.lineEdit_e_wl.setText(str(format_5_dec(en)))
        elif str(self.comboBox_e_wl.currentText()).lower() == "wave length":
            wl = xu.en2lam(en)
            self.lineEdit_e_wl.setText(str(format_5_dec(wl)))

        for prefix, name in self._VECTOR_NAMES.items():
            vector = dict_args[name]
            for i, val in enumerate(vector, 1):
                le = getattr(self, f"lineEdit_{prefix}_{i}")
                le.setText(str(val))

    def _build_vector_arg(self, prefix: str) -> str:
        """Build a vector argument string from line edits."""
        return " ".join(
            getattr(self, f"lineEdit_{prefix}_{i}").text()
            for i in range(1, 4)
        )

    def set_energy(self):
        """Sets experiment energy/wl"""
        if str(self.comboBox_e_wl.currentText()).lower() == "energy":
            energy = self.lineEdit_e_wl.text()
        elif str(self.comboBox_e_wl.currentText()).lower() == "wl":
            energy = xu.lam2en(float(self.lineEdit_e_wl.text()))
        subprocess.Popen(["daf.expt", "-e", str(energy)], shell=False)

    def set_idir(self):
        """Sets experiment idir vector"""
        vector_args = self._build_vector_arg("i").split()
        subprocess.Popen(["daf.expt", "-i"] + vector_args, shell=False)

    def set_ndir(self):
        """Sets experiment ndir vector"""
        vector_args = self._build_vector_arg("n").split()
        subprocess.Popen(["daf.expt", "-n"] + vector_args, shell=False)

    def set_rdir(self):
        """Sets experiment rdir vector"""
        vector_args = self._build_vector_arg("r").split()
        subprocess.Popen(["daf.expt", "-r"] + vector_args, shell=False)
