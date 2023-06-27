import os
from os import path

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from qtpy.QtWidgets import QApplication, QWidget

from daf.utils.dafutilities import DAFIO
from daf.gui.utils import format_5_dec, Icons, center_screen


class MyDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        uic.loadUi(self.ui_filepath(), self)
        self.io = DAFIO()
        self.set_tab_order()
        self.set_channels()
        center_screen(self)

    def ui_filename(self):
        return "bounds.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

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
        self.setTabOrder(self.PyDMLineEdit_mu_llm, self.PyDMLineEdit_mu_hlm)
        self.setTabOrder(self.PyDMLineEdit_mu_hlm, self.PyDMLineEdit_eta_llm)
        self.setTabOrder(self.PyDMLineEdit_eta_llm, self.PyDMLineEdit_eta_hlm)
        self.setTabOrder(self.PyDMLineEdit_eta_hlm, self.PyDMLineEdit_chi_llm)
        self.setTabOrder(self.PyDMLineEdit_chi_llm, self.PyDMLineEdit_chi_hlm)
        self.setTabOrder(self.PyDMLineEdit_chi_hlm, self.PyDMLineEdit_phi_llm)
        self.setTabOrder(self.PyDMLineEdit_phi_llm, self.PyDMLineEdit_phi_hlm)
        self.setTabOrder(self.PyDMLineEdit_phi_hlm, self.PyDMLineEdit_nu_llm)
        self.setTabOrder(self.PyDMLineEdit_nu_llm, self.PyDMLineEdit_nu_hlm)
        self.setTabOrder(self.PyDMLineEdit_nu_hlm, self.PyDMLineEdit_del_llm)
        self.setTabOrder(self.PyDMLineEdit_del_llm, self.PyDMLineEdit_del_hlm)
        self.setTabOrder(self.PyDMLineEdit_del_hlm, self.PyDMLineEdit_mu_llm)

    def set_channels(self):

        data = self.io.read()["motors"]

        translate = QCoreApplication.translate

        # set mu motor labels

        mu_channel = "ca://" + data["mu"]["pv"]
        self.PyDMLabel_mu_desc.setProperty(
            "channel", translate("Form", mu_channel + ".DESC")
        )
        self.PyDMLineEdit_mu_llm.setProperty(
            "channel", translate("Form", mu_channel + ".LLM")
        )
        self.PyDMLineEdit_mu_hlm.setProperty(
            "channel", translate("Form", mu_channel + ".HLM")
        )

        # set eta motor labels

        eta_channel = "ca://" + data["eta"]["pv"]
        self.PyDMLabel_eta_desc.setProperty(
            "channel", translate("Form", eta_channel + ".DESC")
        )
        self.PyDMLineEdit_eta_llm.setProperty(
            "channel", translate("Form", eta_channel + ".LLM")
        )
        self.PyDMLineEdit_eta_hlm.setProperty(
            "channel", translate("Form", eta_channel + ".HLM")
        )

        # set chi motor labels

        chi_channel = "ca://" + data["chi"]["pv"]
        self.PyDMLabel_chi_desc.setProperty(
            "channel", translate("Form", chi_channel + ".DESC")
        )
        self.PyDMLineEdit_chi_llm.setProperty(
            "channel", translate("Form", chi_channel + ".LLM")
        )
        self.PyDMLineEdit_chi_hlm.setProperty(
            "channel", translate("Form", chi_channel + ".HLM")
        )

        # set phi motor labels

        phi_channel = "ca://" + data["phi"]["pv"]
        self.PyDMLabel_phi_desc.setProperty(
            "channel", translate("Form", phi_channel + ".DESC")
        )
        self.PyDMLineEdit_phi_llm.setProperty(
            "channel", translate("Form", phi_channel + ".LLM")
        )
        self.PyDMLineEdit_phi_hlm.setProperty(
            "channel", translate("Form", phi_channel + ".HLM")
        )

        # set nu motor labels

        nu_channel = "ca://" + data["nu"]["pv"]
        self.PyDMLabel_nu_desc.setProperty(
            "channel", translate("Form", nu_channel + ".DESC")
        )
        self.PyDMLineEdit_nu_llm.setProperty(
            "channel", translate("Form", nu_channel + ".LLM")
        )
        self.PyDMLineEdit_nu_hlm.setProperty(
            "channel", translate("Form", nu_channel + ".HLM")
        )

        # set del motor labels

        del_channel = "ca://" + data["del"]["pv"]
        self.PyDMLabel_del_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.PyDMLineEdit_del_llm.setProperty(
            "channel", translate("Form", del_channel + ".LLM")
        )
        self.PyDMLineEdit_del_hlm.setProperty(
            "channel", translate("Form", del_channel + ".HLM")
        )
