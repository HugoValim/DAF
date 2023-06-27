import time

from PyQt5.QtCore import QObject, pyqtSignal

# DAF GUIs imports
from daf.utils.daf_paths import DAFPaths as dp
from daf.command_line.cli_base_utils import CLIBase


DEFAULT = dp.check_for_local_config()
FREQUENCY = 0.5  # 0.5s update rate


class Worker(QObject, CLIBase):
    finished = pyqtSignal()
    update_ready = pyqtSignal()

    def update(self):
        self.data = {}
        try:
            data = self.read_experiment_file()
        except TypeError:
            return
        self.exp = self.build_exp()
        pseudo_dict = self.get_pseudo_angles_from_motor_angles()
        hkl = self.calculate_hkl_from_angles()
        self.data["default"] = data
        self.data["exp"] = self.exp
        self.data["pseudo_dict"] = pseudo_dict
        self.data["hkl"] = hkl

    def run(self):
        """Long-running task."""
        while True:
            self.update()
            self.update_ready.emit()
            time.sleep(FREQUENCY)
