from os import path
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtGui import QIcon

import pandas as pd

from daf.gui.utils import center_screen, Icons


class MyWindow(QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()
        self.make_connections()

    def initUI(self):
        self.setWindowTitle("HKL Scan")
        self.build_layout()
        center_screen(self)

    def _add_separator(self, layout):
        """Add a horizontal separator line to a layout."""
        line = QtWidgets.QFrame(self.frame)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

    def _add_spacer(self, layout):
        """Add an expanding spacer to a layout."""
        layout.addItem(
            QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

    def _add_hkl_field(self, grid, label_text, row_label, col):
        """Add a (bold label + lineEdit) pair to the grid at the given column."""
        font_bold = QtGui.QFont()
        font_bold.setBold(True)
        font_bold.setWeight(75)
        lbl = QtWidgets.QLabel(self.frame)
        lbl.setText(label_text)
        lbl.setFont(font_bold)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(lbl, row_label, col, 1, 1)
        le = QtWidgets.QLineEdit(self.frame)
        grid.addWidget(le, row_label + 1, col, 1, 1)
        return le

    def build_layout(self):
        # Basic layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.frame = QtWidgets.QFrame(self)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)

        # Open file dialog
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.pushButton_open_file = QtWidgets.QPushButton(self.frame)
        self.pushButton_open_file.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_open_file.setIcon(QIcon(Icons.folder))
        self.horizontalLayout_4.addWidget(self.pushButton_open_file)
        self.lineEdit_file_name = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout_4.addWidget(self.lineEdit_file_name)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self._add_separator(self.verticalLayout_2)

        # HKL grid: start row 0 labels / row 1 inputs; end row 2 labels / row 3 inputs
        self.gridLayout = QtWidgets.QGridLayout()
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.lineEdit_hi = self._add_hkl_field(self.gridLayout, "H start", 0, 0)
        self.lineEdit_ki = self._add_hkl_field(self.gridLayout, "K start", 0, 1)
        self.lineEdit_li = self._add_hkl_field(self.gridLayout, "L start", 0, 2)
        self.lineEdit_hf = self._add_hkl_field(self.gridLayout, "H end", 2, 0)
        self.lineEdit_kf = self._add_hkl_field(self.gridLayout, "K end", 2, 1)
        self.lineEdit_lf = self._add_hkl_field(self.gridLayout, "L end", 2, 2)

        self._add_separator(self.verticalLayout_2)

        # Steps and Time
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setText("Steps: ")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_steps = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout.addWidget(self.lineEdit_steps)
        self._add_spacer(self.horizontalLayout)
        self.label_time = QtWidgets.QLabel(self.frame)
        self.label_time.setText("Time: ")
        self.label_time.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.label_time)
        self.lineEdit_time = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout.addWidget(self.lineEdit_time)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self._add_separator(self.verticalLayout_2)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.label_xlabel = QtWidgets.QLabel(self.frame)
        self.label_xlabel.setText("xlabel")
        self.label_xlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_2.addWidget(self.label_xlabel)
        self.comboBox_xlabel = QtWidgets.QComboBox(self.frame)
        self.comboBox_xlabel.addItems(
            ["Points", "Mu", "Eta", "Chi", "Phi", "Nu", "Del"]
        )
        self.horizontalLayout_2.addWidget(self.comboBox_xlabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self._add_separator(self.verticalLayout_2)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.label_csv = QtWidgets.QLabel(self.frame)
        self.label_csv.setText("csv filename")
        self.label_csv.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_3.addWidget(self.label_csv)
        self.lineEdit_csv = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout_3.addWidget(self.lineEdit_csv)
        self.checkBox_csv = QtWidgets.QCheckBox(self.frame)
        self.checkBox_csv.setText("Only calc")
        self.horizontalLayout_3.addWidget(self.checkBox_csv)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self._add_separator(self.verticalLayout_2)

        self.horizontalLayout_start = QtWidgets.QHBoxLayout()
        self._add_spacer(self.horizontalLayout_start)
        self.pushButton_start = QtWidgets.QPushButton(self.frame)
        self.pushButton_start.setText("Start")
        self.pushButton_start.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_start.setIcon(QIcon(Icons.check))
        self.horizontalLayout_start.addWidget(self.pushButton_start)
        self._add_spacer(self.horizontalLayout_start)
        self.verticalLayout_2.addLayout(self.horizontalLayout_start)

    def make_connections(self):
        self.pushButton_open_file.clicked.connect(self.load_csv)
        self.pushButton_start.clicked.connect(self.do_scan)

    def load_csv(self):
        """Open the file browser"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select one or more files",
            "",
            "csv files (*.csv);;All Files (*)",
            options=options,
        )
        self.show()

        if files:
            self.files_now = files
        else:
            self.files_now = None

        if self.files_now:
            self.lineEdit_file_name.setText(self.files_now[0])
            self.update_gui_from_csv()

    def update_gui_from_csv(self):
        data = pd.read_csv(self.lineEdit_file_name.text())
        data_size = len(data["L"]) - 1
        self.lineEdit_steps.setText(str(data_size))
        self.lineEdit_hi.setText(str(data["H"][0]))
        self.lineEdit_ki.setText(str(data["K"][0]))
        self.lineEdit_li.setText(str(data["L"][0]))
        self.lineEdit_hf.setText(str(data["H"][data_size]))
        self.lineEdit_kf.setText(str(data["K"][data_size]))
        self.lineEdit_lf.setText(str(data["L"][data_size]))

    def build_scan_cmd(self):
        if self.lineEdit_file_name.text():
            file = self.lineEdit_file_name.text()
            time = self.lineEdit_time.text()
            return ["daf.ffscan", file, time]
        cmd = [
            "daf.scan",
            self.lineEdit_hi.text(),
            self.lineEdit_ki.text(),
            self.lineEdit_li.text(),
            self.lineEdit_hf.text(),
            self.lineEdit_kf.text(),
            self.lineEdit_lf.text(),
            self.lineEdit_steps.text(),
            self.lineEdit_time.text(),
        ]
        if self.lineEdit_csv.text():
            cmd.extend(["-n", self.lineEdit_csv.text()])
        if self.checkBox_csv.isChecked():
            cmd.append("-c")
        return cmd

    def do_scan(self):
        scan_cmd = self.build_scan_cmd()
        subprocess.Popen(scan_cmd, shell=False)
