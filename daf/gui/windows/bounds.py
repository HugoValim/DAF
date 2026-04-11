import os
from os import path

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from qtpy.QtWidgets import QApplication, QWidget

from daf.utils.dafutilities import DAFIO
from daf.gui.utils import format_5_dec, Icons, center_screen


class MyDisplay(QWidget):

    _MOTOR_NAMES = ("mu", "eta", "chi", "phi", "nu", "del")
    _MOTOR_PAIRS = (("mu", "eta"), ("eta", "chi"), ("chi", "phi"),
                    ("phi", "nu"), ("nu", "del"), ("del", "mu"))

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
        prev_widget = None
        for motor in self._MOTOR_NAMES:
            llm = getattr(self, f"PyDMLineEdit_{motor}_llm")
            hlm = getattr(self, f"PyDMLineEdit_{motor}_hlm")
            if prev_widget:
                self.setTabOrder(prev_widget, llm)
            self.setTabOrder(llm, hlm)
            prev_widget = hlm

    def _configure_motor_channel(self, motor: str, pv: str) -> None:
        """Configure all PyDMLineEdit channels for a single motor."""
        translate = QCoreApplication.translate
        channel = f"ca://{pv}"
        for suffix in ("desc", "llm", "hlm"):
            widget = getattr(self, f"PyDMLabel_{motor}_{suffix}")
            postfix = ".DESC" if suffix == "desc" else f".{suffix.upper()}"
            widget.setProperty("channel", translate("Form", channel + postfix))

    def set_channels(self):
        data = self.io.read()["motors"]
        for motor in self._MOTOR_NAMES:
            self._configure_motor_channel(motor, data[motor]["pv"])
