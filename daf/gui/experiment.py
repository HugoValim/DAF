from os import path
import subprocess

import xrayutilities as xu
from pydm import Display
from qtpy.QtWidgets import QApplication
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

import daf.utils.dafutilities as du


class MyDisplay(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.app = QApplication.instance()
        self.set_labels()
        self.set_tab_order()
        self.build_icons()
        self.set_icons()
        self.center()
        self.make_connections()

    def ui_filename(self):
        return "ui/experiment.ui"

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def center(self):
        """Center the launched GUI in the midle of the current screen"""
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(
            QtGui.QApplication.desktop().cursor().pos()
        )
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def build_icons(self):
        """Build used icons"""
        pixmap_path = path.join(path.dirname(path.realpath(__file__)), "ui/icons")
        self.check_icon = path.join(pixmap_path, "check.svg")

    def set_icons(self):
        """Set used icons"""
        self.pushButton_energy.setIcon(QIcon(self.check_icon))
        self.pushButton_idir.setIcon(QIcon(self.check_icon))
        self.pushButton_ndir.setIcon(QIcon(self.check_icon))
        self.pushButton_rdir.setIcon(QIcon(self.check_icon))

    def set_tab_order(self):
        """Set the corret other when clicking tab"""
        self.setTabOrder(self.ui.lineEdit_e_wl, self.ui.comboBox_e_wl)
        self.setTabOrder(self.ui.comboBox_e_wl, self.ui.pushButton_energy)
        self.setTabOrder(self.ui.pushButton_energy, self.ui.lineEdit_i_1)
        self.setTabOrder(self.ui.lineEdit_i_1, self.ui.lineEdit_i_2)
        self.setTabOrder(self.ui.lineEdit_i_2, self.ui.lineEdit_i_3)
        self.setTabOrder(self.ui.lineEdit_i_2, self.ui.lineEdit_i_3)
        self.setTabOrder(self.ui.lineEdit_i_3, self.ui.pushButton_idir)
        self.setTabOrder(self.ui.pushButton_idir, self.ui.lineEdit_n_1)
        self.setTabOrder(self.ui.lineEdit_n_1, self.ui.lineEdit_n_2)
        self.setTabOrder(self.ui.lineEdit_n_2, self.ui.lineEdit_n_3)
        self.setTabOrder(self.ui.lineEdit_n_3, self.ui.pushButton_ndir)
        self.setTabOrder(self.ui.pushButton_ndir, self.ui.lineEdit_r_1)
        self.setTabOrder(self.ui.lineEdit_r_1, self.ui.lineEdit_r_2)
        self.setTabOrder(self.ui.lineEdit_r_2, self.ui.lineEdit_r_3)
        self.setTabOrder(self.ui.lineEdit_r_3, self.ui.pushButton_rdir)
        self.setTabOrder(self.ui.pushButton_rdir, self.ui.lineEdit_e_wl)

    def make_connections(self):
        """Make the needed connections"""
        self.ui.comboBox_e_wl.currentTextChanged.connect(self.on_combobox_en_changed)
        self.pushButton_energy.clicked.connect(self.set_energy)
        self.pushButton_idir.clicked.connect(self.set_idir)
        self.pushButton_ndir.clicked.connect(self.set_ndir)
        self.pushButton_rdir.clicked.connect(self.set_rdir)

    def get_experiment_file(self):
        """Get the data in DAF's .Exeriment file"""
        dict_args = du.read()
        return dict_args

    def on_combobox_en_changed(self):
        """Switch the energy lineEdit between energy and Wave length based in the QComboBox"""
        lb = lambda x: "{:.5f}".format(float(x))  # format float with 5 decimals
        dict_args = self.get_experiment_file()
        if str(self.ui.comboBox_e_wl.currentText()).lower() == "energy":
            self.ui.lineEdit_e_wl.setText(
                str(lb(dict_args["PV_energy"] - dict_args["energy_offset"]))
            )
        elif str(self.ui.comboBox_e_wl.currentText()).lower() == "wl":
            # lb = lambda x: "{:.5f}".format(float(x))
            wl = xu.en2lam(dict_args["PV_energy"] - dict_args["energy_offset"])
            self.ui.lineEdit_e_wl.setText(str(lb(wl)))

    def set_labels(self):
        """Set default labels"""
        lb = lambda x: "{:.5f}".format(float(x))
        dict_args = self.get_experiment_file()
        if str(self.ui.comboBox_e_wl.currentText()).lower() == "energy":
            self.ui.lineEdit_e_wl.setText(
                str(lb(dict_args["PV_energy"] - dict_args["energy_offset"]))
            )
        elif str(self.ui.comboBox_e_wl.currentText()).lower() == "wave length":
            wl = xu.en2lam(dict_args["PV_energy"] - dict_args["energy_offset"])
            self.ui.lineEdit_e_wl.setText(str(lb(wl)))

        idir = dict_args["IDir"]
        self.ui.lineEdit_i_1.setText(str(idir[0]))
        self.ui.lineEdit_i_2.setText(str(idir[1]))
        self.ui.lineEdit_i_3.setText(str(idir[2]))

        ndir = dict_args["NDir"]
        self.ui.lineEdit_n_1.setText(str(ndir[0]))
        self.ui.lineEdit_n_2.setText(str(ndir[1]))
        self.ui.lineEdit_n_3.setText(str(ndir[2]))

        rdir = dict_args["RDir"]
        self.ui.lineEdit_r_1.setText(str(rdir[0]))
        self.ui.lineEdit_r_2.setText(str(rdir[1]))
        self.ui.lineEdit_r_3.setText(str(rdir[2]))

    def set_energy(self):
        """Sets experiment energy/wl"""
        if str(self.ui.comboBox_e_wl.currentText()).lower() == "energy":
            energy = self.ui.lineEdit_e_wl.text()
        elif str(self.ui.comboBox_e_wl.currentText()).lower() == "wl":
            energy = xu.lam2en(float(self.ui.lineEdit_e_wl.text()))
        subprocess.Popen("daf.expt -e {}".format(energy), shell=True)

    def set_idir(self):
        """Sets experiment idir vector"""
        idir = (
            self.ui.lineEdit_i_1.text()
            + " "
            + self.ui.lineEdit_i_2.text()
            + " "
            + self.ui.lineEdit_i_3.text()
        )
        subprocess.Popen("daf.expt -i {}".format(idir), shell=True)

    def set_ndir(self):
        """Sets experiment ndir vector"""
        ndir = (
            self.ui.lineEdit_n_1.text()
            + " "
            + self.ui.lineEdit_n_2.text()
            + " "
            + self.ui.lineEdit_n_3.text()
        )
        subprocess.Popen("daf.expt -n {}".format(ndir), shell=True)

    def set_rdir(self):
        """Sets experiment rdir vector"""
        rdir = (
            self.ui.lineEdit_r_1.text()
            + " "
            + self.ui.lineEdit_r_2.text()
            + " "
            + self.ui.lineEdit_r_3.text()
        )
        subprocess.Popen("daf.expt -r {}".format(rdir), shell=True)
