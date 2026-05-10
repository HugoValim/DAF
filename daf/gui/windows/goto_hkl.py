from os import path

from pydm import Display
from qtpy.QtWidgets import QApplication
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

from daf.core.hkl_move import HKLMove
from daf.utils.dafutilities import DAFIO


class MyDisplay(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.app = QApplication.instance()
        self.hkl_move = HKLMove(file_store=DAFIO())
        self.ui.calc_HKL.clicked.connect(self.move_in_hkl)
        self.build_icons()
        self.set_icons()
        self.set_tab_order()
        self.center()

    #
    def ui_filename(self):
        return "ui/goto_hkl.ui"

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos()
        )
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def build_icons(self):
        """Build used icons"""
        pixmap_path = path.join(path.dirname(path.realpath(__file__)), "ui/icons")
        self.check_icon = path.join(pixmap_path, "check.svg")

    def set_icons(self):
        """Set used icons"""
        self.ui.calc_HKL.setIcon(QIcon(self.check_icon))

    def set_tab_order(self):
        self.setTabOrder(self.ui.H_set, self.ui.K_set)
        self.setTabOrder(self.ui.K_set, self.ui.L_set)
        self.setTabOrder(self.ui.L_set, self.ui.calc_HKL)
        self.setTabOrder(self.ui.calc_HKL, self.ui.H_set)

    def move_in_hkl(self):

        H = float(self.ui.H_set.text())
        K = float(self.ui.K_set.text())
        L = float(self.ui.L_set.text())

        self.hkl_move.move([H, K, L])

        self.ui.H_set.setText("")
        self.ui.K_set.setText("")
        self.ui.L_set.setText("")
