from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget

from .ui.main_window import UiMainWindow
from .main_tabs.status_tab import StatusTab
from .main_tabs.position_tab import PositionTab
from .main_tabs.rmap_tab import RMapTab
from .main_tabs.scan_tab import ScanTab

from daf.gui.windows.update_gui import Worker

from daf.utils.dafutilities import DAFIO


class MainWindow(UiMainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.run_long_task()
        self.io = DAFIO()
        self.io.sync_with_environment()
        self.instantiate_tabs()

    def instantiate_tabs(self):
        """Instantiate all main tabs and save them in a dict"""
        self.main_tabs = {}
        self.main_tabs["Status"] = StatusTab(self.io)
        self.main_tabs["Position"] = PositionTab(self.io)
        self.main_tabs["RMap"] = RMapTab(self.io)
        self.main_tabs["Scan"] = ScanTab(self.io)

    def setupUi(self, main_window):
        super().setupUi(main_window)
        for tab_name, tab in self.main_tabs.items():
            self.tab_widget.addTab(tab, tab_name)

    def run_long_task(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.worker.update_ready.connect(self.update)

    def update(self):
        for tab in self.main_tabs.values():
            try:
                tab.update(self.worker.data)
            except KeyError:
                # Sometimes the it cannot build the exp, leading to a key error
                pass
