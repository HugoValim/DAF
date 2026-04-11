from os import path
import subprocess

import xrayutilities as xu
from PyQt5 import uic
from qtpy.QtWidgets import QApplication, QWidget
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from daf.utils.dafutilities import DAFIO
from daf.gui.utils import format_5_dec, Icons, center_screen
import daf.utils.experiment_configs as ec


class MyDisplay(QWidget):

    _TAB_ORDER_PAIRS = (
        ("lineEdit_samp_name", "lineEdit_a"),
        ("lineEdit_a", "lineEdit_b"),
        ("lineEdit_b", "lineEdit_c"),
        ("lineEdit_c", "lineEdit_alpha"),
        ("lineEdit_alpha", "lineEdit_beta"),
        ("lineEdit_beta", "lineEdit_gamma"),
        ("lineEdit_gamma", "pushButton_set"),
    )
    _LATTICE_PARAMS = ("a", "b", "c", "alpha", "beta", "gamma")

    def __init__(self, update_dict: dict):
        super().__init__()
        self.app = QApplication.instance()
        uic.loadUi(self.ui_filepath(), self)
        self.update_dict = update_dict
        self.io = DAFIO()
        self.set_combobox_options()
        self.set_comboBox_materials_default()
        self.set_icons()
        self.init_frame_new_samp()
        self.make_connections()
        self.set_tab_order()
        center_screen(self)

    def ui_filename(self):
        return "sample.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def set_icons(self):
        """Set used icons"""
        self.pushButton_set.setIcon(QIcon(Icons.check))

    def set_tab_order(self):
        for from_widget, to_widget in self._TAB_ORDER_PAIRS:
            self.setTabOrder(getattr(self, from_widget), getattr(self, to_widget))

    def init_frame_new_samp(self):
        """Hide the frame at UI start"""
        self.frame_new_samp.setEnabled(False)
        self.frame_new_samp.hide()
        self.resize(450, 125)

    def make_connections(self):
        """Make the needed connections"""
        self.checkBox_new_mat.stateChanged.connect(self.checkbox_state_changed)
        self.pushButton_set.clicked.connect(self.set_sample)
        self.pushButton_set.clicked.connect(self.set_combobox_options)
        # self.pushButton_set.clicked.connect(self.set_comboBox_materials_default)

    def get_experiment_file(self):
        """Get the data in the experiment file"""
        dict_args = self.update_dict["default"]
        return dict_args

    def materials(self):
        """List all predefined materials in xrayutilities"""
        return ec.samples

    def set_comboBox_materials_default(self):
        """Set comboBox to the current used sample"""
        AllItems = [
            self.comboBox_materials.itemText(i)
            for i in range(self.comboBox_materials.count())
        ]
        sample_now = self.get_experiment_file()["Material"]
        if sample_now in AllItems:
            self.comboBox_materials.setCurrentIndex(AllItems.index(sample_now))

    def set_combobox_options(self):
        """Add all possible options to the combobox"""
        user_samples = self.get_experiment_file()["user_samples"]
        items = self.materials()
        items = list(items.keys())
        for sample in user_samples.keys():
            items.append(sample)
        items.sort()
        self.comboBox_materials.addItems(items)
        self.comboBox_materials.setEditable(True)
        self.comboBox_materials.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

    def checkbox_state_changed(self):
        """Manage the new sample section"""
        if self.checkBox_new_mat.isChecked():
            self.frame_new_samp.setEnabled(True)
            self.frame_new_samp.show()
            self.comboBox_materials.setEnabled(False)
            self.center()
        else:
            self.frame_new_samp.setEnabled(False)
            self.frame_new_samp.hide()
            self.comboBox_materials.setEnabled(True)
            self.resize(450, 125)
            self.center()

    def set_sample(self):
        """Set the new sample"""
        if self.checkBox_new_mat.isChecked():
            samp = self.lineEdit_samp_name.text()
            params = [getattr(self, f"lineEdit_{p}").text() for p in self._LATTICE_PARAMS]
            subprocess.Popen(
                ["daf.expt", "-s", samp, "-p"] + params,
                shell=False,
            )
        else:
            samp = self.comboBox_materials.currentText()
            subprocess.Popen(["daf.expt", "-s", samp], shell=False)
