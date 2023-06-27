from os import path

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QWidget
from PyQt5.QtCore import QThread, QCoreApplication, Qt

# import daf.gui.windows.goto_hkl as goto_hkl
import daf.gui.windows.bounds as bounds

# import daf.gui.windows.bounds as bounds
from daf.gui.utils import format_5_dec, Icons, Counter


class PositionTab(QWidget, Counter):
    def __init__(self, dafio):
        super().__init__()
        uic.loadUi(self.ui_filepath(), self)
        # self.set_icons()
        self.make_connections()
        self.update_dict = None
        self.iter_counter = 0
        self.io = dafio

    def ui_filename(self):
        return "position_tab.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def set_icons(self):
        """Set used icons"""
        # self.move_hkl_launcher.setIcon(QIcon(Icons.pen))
        pass

    def make_connections(self):
        self.bounds_launcher.clicked.connect(self.open_bounds_window)
        self.stop_all.clicked.connect(self.stop_all_motors)

    def update(self, update_dict: dict = None) -> None:
        self.update_dict = update_dict
        if self.execute_after_n_iter(10):
            self.refresh_pydm_motors(self.update_dict["default"])
        self.update_hkl()
        self.update_cons()

    def open_bounds_window(self):
        self.mode_window = bounds.MyDisplay()
        self.mode_window.show()

    def stop_all_motors(self):
        """Stop all DAF motors"""
        self.io.stop()

    def refresh_pydm_motors(self, data: dict) -> None:
        translate = QCoreApplication.translate

        # set del motor labels
        del_channel = "ca://" + data["motors"]["del"]["pv"]
        self.PyDMLabel_del_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.PyDMLabel_del_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.PyDMLabel_del_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.PyDMByteIndicator_del.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.PyDMPushButton_del.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set eta motor labels

        del_channel = "ca://" + data["motors"]["eta"]["pv"]
        self.PyDMLabel_eta_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.PyDMLabel_eta_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.PyDMLabel_eta_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.PyDMByteIndicator_eta.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.PyDMPushButton_eta.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set chi motor labels

        del_channel = "ca://" + data["motors"]["chi"]["pv"]
        self.PyDMLabel_chi_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.PyDMLabel_chi_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.PyDMLabel_chi_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.PyDMByteIndicator_chi.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.PyDMPushButton_chi.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set phi motor labels

        del_channel = "ca://" + data["motors"]["phi"]["pv"]
        self.PyDMLabel_phi_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.PyDMLabel_phi_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.PyDMLabel_phi_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.PyDMByteIndicator_phi.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.PyDMPushButton_phi.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set nu motor labels

        del_channel = "ca://" + data["motors"]["nu"]["pv"]
        self.PyDMLabel_nu_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.PyDMLabel_nu_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.PyDMLabel_nu_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.PyDMByteIndicator_nu.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.PyDMPushButton_nu.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set mu motor labels

        del_channel = "ca://" + data["motors"]["mu"]["pv"]
        self.PyDMLabel_mu_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.PyDMLabel_mu_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.PyDMLabel_mu_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.PyDMByteIndicator_mu.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.PyDMPushButton_mu.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

    def update_hkl(self):
        """Update HKL pos labels"""
        self.H_val.setText(str(format_5_dec(self.update_dict["hkl"][0])))
        self.K_val.setText(str(format_5_dec(self.update_dict["hkl"][1])))
        self.L_val.setText(str(format_5_dec(self.update_dict["hkl"][2])))

    def update_cons(self):
        """Update pseudo-angle pos labels"""
        self.label_alpha.setText(
            str(format_5_dec(self.update_dict["pseudo_dict"]["alpha"]))
        )
        self.label_beta.setText(
            str(format_5_dec(self.update_dict["pseudo_dict"]["beta"]))
        )
        self.label_psi.setText(
            str(format_5_dec(self.update_dict["pseudo_dict"]["psi"]))
        )
        self.label_tau.setText(
            str(format_5_dec(self.update_dict["pseudo_dict"]["tau"]))
        )
        self.label_qaz.setText(
            str(format_5_dec(self.update_dict["pseudo_dict"]["qaz"]))
        )
        self.label_naz.setText(
            str(format_5_dec(self.update_dict["pseudo_dict"]["naz"]))
        )
        self.label_omega.setText(
            str(format_5_dec(self.update_dict["pseudo_dict"]["omega"]))
        )
