from os import path
import subprocess

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QApplication, QWidget
from daf.gui.utils import Icons, center_screen, format_5_dec
import xrayutilities as xu


class MyDisplay(QWidget):
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
        self.pushButton_energy.setIcon(QIcon(Icons.check))
        self.pushButton_idir.setIcon(QIcon(Icons.check))
        self.pushButton_ndir.setIcon(QIcon(Icons.check))
        self.pushButton_rdir.setIcon(QIcon(Icons.check))

    def set_tab_order(self):
        """Set the corret other when clicking tab"""
        self.setTabOrder(self.lineEdit_e_wl, self.comboBox_e_wl)
        self.setTabOrder(self.comboBox_e_wl, self.pushButton_energy)
        self.setTabOrder(self.pushButton_energy, self.lineEdit_i_1)
        self.setTabOrder(self.lineEdit_i_1, self.lineEdit_i_2)
        self.setTabOrder(self.lineEdit_i_2, self.lineEdit_i_3)
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
        self.pushButton_idir.clicked.connect(self.set_idir)
        self.pushButton_ndir.clicked.connect(self.set_ndir)
        self.pushButton_rdir.clicked.connect(self.set_rdir)

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

        idir = dict_args["IDir"]
        self.lineEdit_i_1.setText(str(idir[0]))
        self.lineEdit_i_2.setText(str(idir[1]))
        self.lineEdit_i_3.setText(str(idir[2]))

        ndir = dict_args["NDir"]
        self.lineEdit_n_1.setText(str(ndir[0]))
        self.lineEdit_n_2.setText(str(ndir[1]))
        self.lineEdit_n_3.setText(str(ndir[2]))

        rdir = dict_args["RDir"]
        self.lineEdit_r_1.setText(str(rdir[0]))
        self.lineEdit_r_2.setText(str(rdir[1]))
        self.lineEdit_r_3.setText(str(rdir[2]))

    def set_energy(self):
        """Sets experiment energy/wl"""
        if str(self.comboBox_e_wl.currentText()).lower() == "energy":
            energy = self.lineEdit_e_wl.text()
        elif str(self.comboBox_e_wl.currentText()).lower() == "wl":
            energy = xu.lam2en(float(self.lineEdit_e_wl.text()))
        subprocess.Popen("daf.expt -e {}".format(energy), shell=True)

    def set_idir(self):
        """Sets experiment idir vector"""
        idir = (
            self.lineEdit_i_1.text()
            + " "
            + self.lineEdit_i_2.text()
            + " "
            + self.lineEdit_i_3.text()
        )
        subprocess.Popen("daf.expt -i {}".format(idir), shell=True)

    def set_ndir(self):
        """Sets experiment ndir vector"""
        ndir = (
            self.lineEdit_n_1.text()
            + " "
            + self.lineEdit_n_2.text()
            + " "
            + self.lineEdit_n_3.text()
        )
        subprocess.Popen("daf.expt -n {}".format(ndir), shell=True)

    def set_rdir(self):
        """Sets experiment rdir vector"""
        rdir = (
            self.lineEdit_r_1.text()
            + " "
            + self.lineEdit_r_2.text()
            + " "
            + self.lineEdit_r_3.text()
        )
        subprocess.Popen("daf.expt -r {}".format(rdir), shell=True)
