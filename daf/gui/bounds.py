import os
from os import path
from pydm import Display

from PyQt5 import QtGui
from PyQt5.QtCore import QCoreApplication
from qtpy.QtWidgets import QApplication

import daf.utils.dafutilities as du


class MyDisplay(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.app = QApplication.instance()
        self.set_tab_order()
        self.set_channels()
        self.center()

    def ui_filename(self):
        return "ui/bounds.ui"

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(
            QtGui.QApplication.desktop().cursor().pos()
        )
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def load_data(self):
        # Extract the directory of this file...
        base_dir = os.path.dirname(os.path.realpath(__file__))
        # Concatenate the directory with the file name...
        data_file = os.path.join(base_dir, "motor_fields_default.yml")
        # Open the file so we can read the data...
        with open(data_file, "r") as file:
            data = yaml.safe_load(file)
            return data

    def set_tab_order(self):
        self.setTabOrder(self.ui.PyDMLineEdit_mu_llm, self.ui.PyDMLineEdit_mu_hlm)
        self.setTabOrder(self.ui.PyDMLineEdit_mu_hlm, self.ui.PyDMLineEdit_eta_llm)
        self.setTabOrder(self.ui.PyDMLineEdit_eta_llm, self.ui.PyDMLineEdit_eta_hlm)
        self.setTabOrder(self.ui.PyDMLineEdit_eta_hlm, self.ui.PyDMLineEdit_chi_llm)
        self.setTabOrder(self.ui.PyDMLineEdit_chi_llm, self.ui.PyDMLineEdit_chi_hlm)
        self.setTabOrder(self.ui.PyDMLineEdit_chi_hlm, self.ui.PyDMLineEdit_phi_llm)
        self.setTabOrder(self.ui.PyDMLineEdit_phi_llm, self.ui.PyDMLineEdit_phi_hlm)
        self.setTabOrder(self.ui.PyDMLineEdit_phi_hlm, self.ui.PyDMLineEdit_nu_llm)
        self.setTabOrder(self.ui.PyDMLineEdit_nu_llm, self.ui.PyDMLineEdit_nu_hlm)
        self.setTabOrder(self.ui.PyDMLineEdit_nu_hlm, self.ui.PyDMLineEdit_del_llm)
        self.setTabOrder(self.ui.PyDMLineEdit_del_llm, self.ui.PyDMLineEdit_del_hlm)
        self.setTabOrder(self.ui.PyDMLineEdit_del_hlm, self.ui.PyDMLineEdit_mu_llm)

    def set_channels(self):

        data = du.PVS

        translate = QCoreApplication.translate

        # set mu motor labels

        mu_channel = "ca://" + data["Mu"]
        self.ui.PyDMLabel_mu_desc.setProperty(
            "channel", translate("Form", mu_channel + ".DESC")
        )
        self.ui.PyDMLineEdit_mu_llm.setProperty(
            "channel", translate("Form", mu_channel + ".LLM")
        )
        self.ui.PyDMLineEdit_mu_hlm.setProperty(
            "channel", translate("Form", mu_channel + ".HLM")
        )

        # set eta motor labels

        eta_channel = "ca://" + data["Eta"]
        self.ui.PyDMLabel_eta_desc.setProperty(
            "channel", translate("Form", eta_channel + ".DESC")
        )
        self.ui.PyDMLineEdit_eta_llm.setProperty(
            "channel", translate("Form", eta_channel + ".LLM")
        )
        self.ui.PyDMLineEdit_eta_hlm.setProperty(
            "channel", translate("Form", eta_channel + ".HLM")
        )

        # set chi motor labels

        chi_channel = "ca://" + data["Chi"]
        self.ui.PyDMLabel_chi_desc.setProperty(
            "channel", translate("Form", chi_channel + ".DESC")
        )
        self.ui.PyDMLineEdit_chi_llm.setProperty(
            "channel", translate("Form", chi_channel + ".LLM")
        )
        self.ui.PyDMLineEdit_chi_hlm.setProperty(
            "channel", translate("Form", chi_channel + ".HLM")
        )

        # set phi motor labels

        phi_channel = "ca://" + data["Phi"]
        self.ui.PyDMLabel_phi_desc.setProperty(
            "channel", translate("Form", phi_channel + ".DESC")
        )
        self.ui.PyDMLineEdit_phi_llm.setProperty(
            "channel", translate("Form", phi_channel + ".LLM")
        )
        self.ui.PyDMLineEdit_phi_hlm.setProperty(
            "channel", translate("Form", phi_channel + ".HLM")
        )

        # set nu motor labels

        nu_channel = "ca://" + data["Nu"]
        self.ui.PyDMLabel_nu_desc.setProperty(
            "channel", translate("Form", nu_channel + ".DESC")
        )
        self.ui.PyDMLineEdit_nu_llm.setProperty(
            "channel", translate("Form", nu_channel + ".LLM")
        )
        self.ui.PyDMLineEdit_nu_hlm.setProperty(
            "channel", translate("Form", nu_channel + ".HLM")
        )

        # set del motor labels

        del_channel = "ca://" + data["Del"]
        self.ui.PyDMLabel_del_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.ui.PyDMLineEdit_del_llm.setProperty(
            "channel", translate("Form", del_channel + ".LLM")
        )
        self.ui.PyDMLineEdit_del_hlm.setProperty(
            "channel", translate("Form", del_channel + ".HLM")
        )
