from os import path
import subprocess

from PyQt5 import uic
from qtpy.QtWidgets import QApplication
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QWidget,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QMenu,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
import numpy as np

from daf.utils.dafutilities import DAFIO
from daf.gui.utils import format_5_dec, Icons, center_screen


class MyDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        uic.loadUi(self.ui_filepath(), self)
        self.io = DAFIO()
        self.loop()
        self.update_reflections()
        self.link_table_2_menu()
        self.make_connections()
        self.set_tab_order()
        self.set_icons()
        center_screen(self)

    def ui_filename(self):
        return "ub.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def loop(self):
        """Loop to check if a curve is selected or not"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(2000)  # trigger every 2 seconds.

    def set_icons(self):
        """Set used icons"""
        self.pushButton_set_u.setIcon(QIcon(Icons.check))
        self.pushButton_set_i.setIcon(QIcon(Icons.pen))
        self.pushButton_set_ub.setIcon(QIcon(Icons.check))

    def make_connections(self):
        """Make the needed connections"""

        # Umat
        self.update_u_labels()
        self.pushButton_set_u.clicked.connect(self.set_u_matrix)
        self.pushButton_set_i.clicked.connect(self.set_u_to_i)

        # UBmat
        self.update_ub_labels()
        self.pushButton_set_ub.clicked.connect(self.update_ub_labels)

    def set_tab_order(self):

        # Set U and UB
        self.setTabOrder(self.tab_UB, self.lineEdit_u_00)
        self.setTabOrder(self.lineEdit_u_00, self.lineEdit_u_01)
        self.setTabOrder(self.lineEdit_u_01, self.lineEdit_u_02)
        self.setTabOrder(self.lineEdit_u_02, self.lineEdit_u_10)
        self.setTabOrder(self.lineEdit_u_10, self.lineEdit_u_11)
        self.setTabOrder(self.lineEdit_u_11, self.lineEdit_u_12)
        self.setTabOrder(self.lineEdit_u_12, self.lineEdit_u_20)
        self.setTabOrder(self.lineEdit_u_20, self.lineEdit_u_21)
        self.setTabOrder(self.lineEdit_u_21, self.lineEdit_u_22)
        self.setTabOrder(self.lineEdit_u_22, self.pushButton_set_u)
        self.setTabOrder(self.pushButton_set_u, self.pushButton_set_i)
        self.setTabOrder(self.pushButton_set_i, self.lineEdit_ub_00)
        self.setTabOrder(self.lineEdit_ub_00, self.lineEdit_ub_01)
        self.setTabOrder(self.lineEdit_ub_01, self.lineEdit_ub_02)
        self.setTabOrder(self.lineEdit_ub_02, self.lineEdit_ub_10)
        self.setTabOrder(self.lineEdit_ub_10, self.lineEdit_ub_11)
        self.setTabOrder(self.lineEdit_ub_11, self.lineEdit_ub_12)
        self.setTabOrder(self.lineEdit_ub_12, self.lineEdit_ub_20)
        self.setTabOrder(self.lineEdit_ub_20, self.lineEdit_ub_21)
        self.setTabOrder(self.lineEdit_ub_21, self.lineEdit_ub_22)
        self.setTabOrder(self.lineEdit_ub_22, self.pushButton_set_ub)
        self.setTabOrder(self.pushButton_set_ub, self.tab_UB)

    def get_experiment_file(self):
        """Get data from the .Experiment file"""
        dict_args = self.io.read()
        return dict_args

    def format_decimals(self, x):
        return "{:.5f}".format(float(x))  # format float with 5 decimals

    def update(self):
        """Get data to update, if things change update"""
        data = self.get_experiment_file()
        refs = data["reflections"]
        if self.refs != refs:
            self.update_reflections()

    def _build_reflection_row(self, row_idx: int, ref: list) -> QCheckBox:
        """Insert a single reflection row into the table. Returns the checkbox."""
        centered = Qt.AlignHCenter | Qt.AlignVCenter
        values = [str(row_idx)] + [str(ref[i]) for i in range(10)]
        values[-1] = format_5_dec(ref[9])
        for col, val in enumerate(values):
            item = QTableWidgetItem(val)
            item.setTextAlignment(centered)
            self.tableWidget.setItem(row_idx, col, item)
        cb = QCheckBox()
        cb.setCheckState(QtCore.Qt.Unchecked)
        widget = QWidget()
        layoutH = QHBoxLayout(widget)
        layoutH.addWidget(cb)
        layoutH.setAlignment(QtCore.Qt.AlignCenter)
        layoutH.setContentsMargins(10, 0, 0, 0)
        self.tableWidget.setCellWidget(row_idx, 11, cb)
        return cb

    def update_reflections(self):
        """Update reflections table from experiment file."""
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        data = self.get_experiment_file()
        refs = data["reflections"]
        self.refs = refs
        self.table_checkboxes = {}
        for row in range(len(refs)):
            self.tableWidget.insertRow(row)
            idx = str(row + 1)
            cb = self._build_reflection_row(row, refs[row])
            self.table_checkboxes[idx] = cb
        for col in range(self.tableWidget.columnCount()):
            header = self.tableWidget.horizontalHeader()
            header.setResizeMode(col, QHeaderView.Stretch)

    def link_table_2_menu(self):
        """Link the table widget to the menu options"""
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested[QtCore.QPoint].connect(
            self.table_menu_builder
        )

    def table_menu_builder(self):
        """Build the menu that will pop when with right clicks in the table"""
        self.table_menu = QMenu(self.tableWidget)
        # Refresh plot

        get_reflection = self.table_menu.addAction("Get Current Pos")
        get_reflection.triggered.connect(self.get_reflection)
        calc_from_2 = self.table_menu.addAction("Calc From 2 Refs")
        calc_from_2.triggered.connect(self.calc_from_2_ref)
        calc_from_3 = self.table_menu.addAction("Calc From 3 Refs")
        calc_from_3.triggered.connect(self.calc_from_3_ref)

        self.table_menu.exec_(QtGui.QCursor.pos())

    def get_reflection(self):
        """Get the reflection now, user must pass the HKL position"""
        text, result = QtWidgets.QInputDialog.getText(
            self,
            "Input Dialog",
            "What is the current HKL position? (use the format H,K,L)",
        )
        if result:
            hkl_now = text.split(",")
            # print("daf.ub -rn {} {} {}".format(hkl_now[0], hkl_now[1], hkl_now[2]))
            p = subprocess.Popen(
                "daf.ub -rn {} {} {}".format(hkl_now[0], hkl_now[1], hkl_now[2]),
                shell=True,
            )
            p.wait()
            self.update_reflections()

    def calc_from_2_ref(self):
        """Do the calculation with 2 selected reflections"""
        inp = []
        for key, value in self.table_checkboxes.items():
            if value.isChecked():
                inp.append(key)

        if len(inp) != 2:
            msgbox = QtWidgets.QMessageBox()
            msgbox_text = "The number of checked items \nmust be 2 for this calculation"
            ret = msgbox.question(
                self,
                "Warning",
                msgbox_text,
                QtWidgets.QMessageBox.Ok,
                QtWidgets.QMessageBox.Ok,
            )
        else:
            # os.system("daf.ub -c2 {} {}".format(inp[0], inp[1]))
            subprocess.Popen("daf.ub -c2 {} {}".format(inp[0], inp[1]), shell=True)

    def calc_from_3_ref(self):
        """Do the calculation with 3 selected reflections"""
        inp = []
        for key, value in self.table_checkboxes.items():
            if value.isChecked():
                inp.append(key)

        if len(inp) != 3:
            msgbox = QtWidgets.QMessageBox()
            msgbox_text = "The number of checked items \nmust be 2 for this calculation"
            ret = msgbox.question(
                self,
                "Warning",
                msgbox_text,
                QtWidgets.QMessageBox.Ok,
                QtWidgets.QMessageBox.Ok,
            )
        else:
            # os.system("daf.ub -c3 {} {} {}".format(inp[0], inp[1], inp[2]))
            subprocess.Popen(
                "daf.ub -c3 {} {} {}".format(inp[0], inp[1], inp[2]), shell=True
            )

    def set_u_to_i(self):
        """Set the U lineEdits values to the 3x3 identity matrix."""
        identity = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        for r, row in enumerate(identity):
            for c, val in enumerate(row):
                getattr(self, f"lineEdit_u_{r}{c}").setText(self.format_decimals(val))

    def update_u_labels(self):
        """Set the U lineEdits values from the experiment file."""
        U = np.array(self.get_experiment_file()["U_mat"])
        for r in range(3):
            for c in range(3):
                getattr(self, f"lineEdit_u_{r}{c}").setText(
                    self.format_decimals(str(U[r][c]))
                )

    def set_u_matrix(self):
        """Set the U matrix from lineEdit values."""
        values = [
            getattr(self, f"lineEdit_u_{r}{c}").text()
            for r in range(3) for c in range(3)
        ]
        subprocess.Popen(
            "daf.ub -u " + " ".join(values),
            shell=True,
        )
        self.update_ub_labels()  # U changes → UB changes too

    def update_ub_labels(self):
        """Set the UB lineEdits values from the experiment file."""
        UB = np.array(self.get_experiment_file()["UB_mat"])
        for r in range(3):
            for c in range(3):
                getattr(self, f"lineEdit_ub_{r}{c}").setText(
                    self.format_decimals(str(UB[r][c]))
                )

    def set_ub_matrix(self):
        """Set the UB matrix from lineEdit values."""
        values = [
            getattr(self, f"lineEdit_ub_{r}{c}").text()
            for r in range(3) for c in range(3)
        ]
        subprocess.Popen(
            "daf.ub -ub " + " ".join(values),
            shell=True,
        )
