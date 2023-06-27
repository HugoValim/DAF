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
        self.setTabOrder(self.lineEdit_samp_name, self.lineEdit_a)
        self.setTabOrder(self.lineEdit_a, self.lineEdit_b)
        self.setTabOrder(self.lineEdit_b, self.lineEdit_c)
        self.setTabOrder(self.lineEdit_c, self.lineEdit_alpha)
        self.setTabOrder(self.lineEdit_alpha, self.lineEdit_beta)
        self.setTabOrder(self.lineEdit_beta, self.lineEdit_gamma)
        self.setTabOrder(self.lineEdit_gamma, self.pushButton_set)

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
            a = self.lineEdit_a.text()
            b = self.lineEdit_b.text()
            c = self.lineEdit_c.text()
            alpha = self.lineEdit_alpha.text()
            beta = self.lineEdit_beta.text()
            gamma = self.lineEdit_gamma.text()

            subprocess.Popen(
                "daf.expt -s {} -p {} {} {} {} {} {}".format(
                    samp, a, b, c, alpha, beta, gamma
                ),
                shell=True,
            )
        else:
            samp = self.comboBox_materials.currentText()
            subprocess.Popen("daf.expt -s {}".format(samp), shell=True)
