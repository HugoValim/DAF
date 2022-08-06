import subprocess
from os import path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtGui import QIcon

import pandas as pd


class MyWindow(QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()
        self.make_connections()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(
            QtGui.QApplication.desktop().cursor().pos()
        )
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def initUI(self):
        # self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("HKL Scan")
        self.build_icons()
        self.build_layout()
        self.center()

    def build_icons(self):
        pixmap_path = path.join(path.dirname(path.realpath(__file__)), "ui/icons")
        self.folder_icon = path.join(pixmap_path, "folder-open.svg")
        self.check_icon = path.join(pixmap_path, "check.svg")

    def build_layout(self):
        font_bold = QtGui.QFont()
        font_bold.setBold(True)
        font_bold.setWeight(75)

        # Basic Layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        # self.verticalLayout.addWidget(self.frame)

        # Open file dialog
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.pushButton_open_file = QtWidgets.QPushButton(self.frame)
        self.pushButton_open_file.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_open_file.setIcon(QIcon(self.folder_icon))
        self.horizontalLayout_4.addWidget(self.pushButton_open_file)
        self.lineEdit_file_name = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout_4.addWidget(self.lineEdit_file_name)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        line1 = QtWidgets.QFrame(self.frame)
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout_2.addWidget(line1)

        # Build the grid layout
        self.gridLayout = QtWidgets.QGridLayout()
        self.verticalLayout_2.addLayout(self.gridLayout)

        # Hi
        self.label_hi = QtWidgets.QLabel(self.frame)
        self.label_hi.setText("H start")
        self.label_hi.setFont(font_bold)
        self.label_hi.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_hi, 0, 0, 1, 1)
        self.lineEdit_hi = QtWidgets.QLineEdit(self.frame)
        self.gridLayout.addWidget(self.lineEdit_hi, 1, 0, 1, 1)

        # Ki
        self.label_ki = QtWidgets.QLabel(self.frame)
        self.label_ki.setText("K start")
        self.label_ki.setFont(font_bold)
        self.label_ki.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_ki, 0, 1, 1, 1)
        self.lineEdit_ki = QtWidgets.QLineEdit(self.frame)
        self.gridLayout.addWidget(self.lineEdit_ki, 1, 1, 1, 1)

        # Li
        self.label_li = QtWidgets.QLabel(self.frame)
        self.label_li.setText("L start")
        self.label_li.setFont(font_bold)
        self.label_li.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_li, 0, 2, 1, 1)
        self.lineEdit_li = QtWidgets.QLineEdit(self.frame)
        self.gridLayout.addWidget(self.lineEdit_li, 1, 2, 1, 1)

        # Hf
        self.label_hf = QtWidgets.QLabel(self.frame)
        self.label_hf.setText("H end")
        self.label_hf.setFont(font_bold)
        self.label_hf.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_hf, 2, 0, 1, 1)
        self.lineEdit_hf = QtWidgets.QLineEdit(self.frame)
        self.gridLayout.addWidget(self.lineEdit_hf, 3, 0, 1, 1)

        # Kf
        self.label_kf = QtWidgets.QLabel(self.frame)
        self.label_kf.setText("K end")
        self.label_kf.setFont(font_bold)
        self.label_kf.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_kf, 2, 1, 1, 1)
        self.lineEdit_kf = QtWidgets.QLineEdit(self.frame)
        self.gridLayout.addWidget(self.lineEdit_kf, 3, 1, 1, 1)

        # Lf
        self.label_lf = QtWidgets.QLabel(self.frame)
        self.label_lf.setText("L end")
        self.label_lf.setFont(font_bold)
        self.label_lf.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_lf, 2, 2, 1, 1)
        self.lineEdit_lf = QtWidgets.QLineEdit(self.frame)
        self.gridLayout.addWidget(self.lineEdit_lf, 3, 2, 1, 1)

        line2 = QtWidgets.QFrame(self.frame)
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout_2.addWidget(line2)

        # Steps and Time
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setText("Steps: ")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_steps = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout.addWidget(self.lineEdit_steps)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.label_time = QtWidgets.QLabel(self.frame)
        self.label_time.setText("Time: ")
        self.label_time.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.label_time)
        self.lineEdit_time = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout.addWidget(self.lineEdit_time)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        line3 = QtWidgets.QFrame(self.frame)
        line3.setFrameShape(QtWidgets.QFrame.HLine)
        line3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout_2.addWidget(line3)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.label_xlabel = QtWidgets.QLabel(self.frame)
        self.label_xlabel.setText("xlabel")
        self.label_xlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_2.addWidget(self.label_xlabel)
        self.comboBox_xlabel = QtWidgets.QComboBox(self.frame)
        self.comboBox_xlabel.addItem("Points")
        self.comboBox_xlabel.addItem("Mu")
        self.comboBox_xlabel.addItem("Eta")
        self.comboBox_xlabel.addItem("Chi")
        self.comboBox_xlabel.addItem("Phi")
        self.comboBox_xlabel.addItem("Nu")
        self.comboBox_xlabel.addItem("Del")
        self.horizontalLayout_2.addWidget(self.comboBox_xlabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        line4 = QtWidgets.QFrame(self.frame)
        line4.setFrameShape(QtWidgets.QFrame.HLine)
        line4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout_2.addWidget(line4)

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

        line5 = QtWidgets.QFrame(self.frame)
        line5.setFrameShape(QtWidgets.QFrame.HLine)
        line5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout_2.addWidget(line5)

        self.horizontalLayout_start = QtWidgets.QHBoxLayout()
        spacerItem_2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_start.addItem(spacerItem_2)
        self.pushButton_start = QtWidgets.QPushButton(self.frame)
        self.pushButton_start.setText("Start")
        self.pushButton_start.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_start.setIcon(QIcon(self.check_icon))
        self.horizontalLayout_start.addWidget(self.pushButton_start)
        spacerItem_3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_start.addItem(spacerItem_3)
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
            cmd = "daf.rfscan "
            file = self.lineEdit_file_name.text() + " "
            time = self.lineEdit_time.text() + " "
            xlabel = "-x " + self.comboBox_xlabel.currentText()
            cmd += file + time + xlabel
        else:
            cmd = "daf.scan "
            hi = self.lineEdit_hi.text() + " "
            ki = self.lineEdit_ki.text() + " "
            li = self.lineEdit_li.text() + " "
            hf = self.lineEdit_hf.text() + " "
            kf = self.lineEdit_kf.text() + " "
            lf = self.lineEdit_lf.text() + " "
            steps = self.lineEdit_steps.text() + " "
            time = self.lineEdit_time.text() + " "
            xlabel = "-x " + self.comboBox_xlabel.currentText() + " "
            cmd += hi + ki + li + hf + kf + lf + steps + time + xlabel
            if self.lineEdit_csv.text():
                cmd += "-n " + self.lineEdit_csv.text() + " "
            if self.checkBox_csv.isChecked():
                cmd += "-c"

        return cmd

    def do_scan(self):
        scan_cmd = self.build_scan_cmd()
        print(scan_cmd)
        subprocess.Popen(scan_cmd, shell=True)
        # os.system(scan_cmd)
