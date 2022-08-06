from os import path
import subprocess

from pydm import Display
from qtpy.QtWidgets import QApplication
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon


class MyDisplay(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.app = QApplication.instance()
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
        self.ui.calc_HKL.setIcon(QIcon(self.check_icon))

    def set_tab_order(self):
        self.setTabOrder(self.ui.H_set, self.ui.K_set)
        self.setTabOrder(self.ui.K_set, self.ui.L_set)
        self.setTabOrder(self.ui.L_set, self.ui.calc_HKL)
        self.setTabOrder(self.ui.calc_HKL, self.ui.H_set)

    def move_in_hkl(self):

        H = self.ui.H_set.text()
        K = self.ui.K_set.text()
        L = self.ui.L_set.text()

        # os.system("daf.mv {} {} {} -q".format(H, K, L))
        subprocess.Popen("daf.mv {} {} {}".format(H, K, L), shell=True)

        self.H_set.setText("")
        self.K_set.setText("")
        self.L_set.setText("")
