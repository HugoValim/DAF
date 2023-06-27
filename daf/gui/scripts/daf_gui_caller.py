"""
Entry script for the DAF GUI application.
"""
import logging
import os
import signal
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QCloseEvent, QIcon, QSurfaceFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from daf.gui.main_window import MainWindow
from daf.gui.utils import Icons, center_screen
from daf.utils.decorators import cli_decorator

signal.signal(signal.SIGINT, signal.SIG_DFL)

if getattr(sys, "frozen", False):
    # frozen
    root_dir = os.path.dirname(sys.executable)
else:
    root_dir = os.path.dirname(os.path.realpath(__file__))


X_LOC = "window_x_location"
Y_LOC = "window_y_location"
X_SIZE = "window_x_size"
Y_SIZE = "window_y_size"


class DAFMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._config = QtCore.QSettings("Sirius", "DAF-GUI")

    def show(self):
        first_run = not self._config.contains(X_SIZE)
        if first_run:
            self.showMaximized()
        else:
            self.resize(
                int(self._config.value(X_SIZE, 500)),
                int(self._config.value(Y_SIZE, 500)),
            )
            self.move(
                int(self._config.value(X_LOC, 0)), int(self._config.value(Y_LOC, 0))
            )
            center_screen(self)
            super().show()

    def closeEvent(self, event: QCloseEvent) -> None:
        # msg = QMessageBox.question(
        #     None,
        #     "Close application",
        #     "Are you sure you want to quit?",
        #     QMessageBox.Yes | QMessageBox.No,
        #     QMessageBox.Yes,
        # )
        # if msg == QMessageBox.Yes:
        #     window_size = self.size()
        #     self._config.setValue(X_SIZE, window_size.width())
        #     self._config.setValue(Y_SIZE, window_size.height())
        #     window_loc = self.pos()
        #     self._config.setValue(X_LOC, window_loc.x())
        #     self._config.setValue(Y_LOC, window_loc.y())
        #     event.accept()
        # else:
        #     event.ignore()
        window_size = self.size()
        self._config.setValue(X_SIZE, window_size.width())
        self._config.setValue(Y_SIZE, window_size.height())
        window_loc = self.pos()
        self._config.setValue(X_LOC, window_loc.x())
        self._config.setValue(Y_LOC, window_loc.y())
        event.accept()

@cli_decorator
def main() -> None:
    QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.c()))
    logging.basicConfig(level=logging.INFO)
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    surfaceFormat = QSurfaceFormat()
    surfaceFormat.setSwapInterval(1)
    surfaceFormat.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(surfaceFormat)
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon(os.path.join("ui", "icon.png")))
    window = DAFMainWindow()
    ui = MainWindow()
    ui.setupUi(window)
    window.show()
    app.exec()
    # sys.exit(app.exec())


if __name__ == "__main__":
    main()
