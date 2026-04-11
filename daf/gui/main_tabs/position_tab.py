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

    def _configure_motor_channel(self, motor: str, pv: str) -> None:
        """Configure all PyDM widget channels for a single motor."""
        translate = QCoreApplication.translate
        channel = f"ca://{pv}"
        suffix_to_postfix = {
            "desc": ".DESC",
            "val": ".VAL",
            "rbv": ".RBV",
        }
        for suffix, postfix in suffix_to_postfix.items():
            widget = getattr(self, f"PyDMLabel_{motor}_{suffix}")
            widget.setProperty("channel", translate("Form", channel + postfix))
        getattr(self, f"PyDMByteIndicator_{motor}").setProperty(
            "channel", translate("Form", channel + ".MOVN")
        )
        getattr(self, f"PyDMPushButton_{motor}").setProperty(
            "channel", translate("Form", channel + ".STOP")
        )

    def refresh_pydm_motors(self, data: dict) -> None:
        """Refresh PyDM motor channels for all six motors."""
        motors = ("del", "eta", "chi", "phi", "nu", "mu")
        for motor in motors:
            pv = data["motors"][motor]["pv"]
            self._configure_motor_channel(motor, pv)

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
