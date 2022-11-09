from os import path
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon


class MyWindow(QWidget):
    def __init__(self, n_motors, scan_type):
        super(MyWindow, self).__init__()
        self.n_motors = n_motors
        self.scan_type = scan_type
        self.build_icons()
        self.initUI()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(
            QtGui.QApplication.desktop().cursor().pos()
        )
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def build_icons(self):
        pixmap_path = path.join(path.dirname(path.realpath(__file__)), "ui/icons")
        self.check_icon = path.join(pixmap_path, "check.svg")

    def initUI(self):
        # self.setGeometry(200, 200, 300, 300)
        if self.scan_type == "abs":
            self.title = "a"
        elif self.scan_type == "rel":
            self.title = "d"
        elif self.scan_type == "mesh":
            self.title = "m"

        if self.n_motors > 1:
            self.title += str(self.n_motors) + "scan"
        else:
            self.title += "scan"

        self.setWindowTitle(self.title)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalLayout.addWidget(self.frame)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.build_motor_layout()
        self.build_time_step()
        self.build_scan_button()
        self.center()

    def build_motor_layout(self):
        self.motor_layout = []
        for i in range(self.n_motors):
            self.motor_layout.append(self.scan_field(i))
            for name, checkbox in self.motor_layout[i]["checkboxes"].items():
                checkbox.clicked.connect(
                    lambda state, x=name: self.only_one_checkbox(state, x)
                )

    def only_one_checkbox(self, state, name):
        idx = int(name.split("_")[-1])
        for checkbox in self.motor_layout[idx]["checkboxes"].values():
            if checkbox.isChecked():
                checkbox.setChecked(False)
        if state:
            self.motor_layout[idx]["checkboxes"][name].setChecked(True)

    def scan_field(self, idx):
        checkbox_dict = {}
        line_edit_dict = {}
        final_dict = {}
        label_motor = QtWidgets.QLabel(self.frame)
        label_motor.setText("Motor " + str(idx + 1))
        label_motor.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        label_motor.setFont(QtGui.QFont("Sans Serif", weight=QtGui.QFont.Bold))
        self.verticalLayout_2.addWidget(label_motor)
        horizontalLayout = QtWidgets.QHBoxLayout()
        checkbox_dict["mu_" + str(idx)] = QtWidgets.QCheckBox(self.frame)
        checkbox_dict["mu_" + str(idx)].setText("Mu")
        horizontalLayout.addWidget(checkbox_dict["mu_" + str(idx)])
        checkbox_dict["eta_" + str(idx)] = QtWidgets.QCheckBox(self.frame)
        checkbox_dict["eta_" + str(idx)].setText("Eta")
        horizontalLayout.addWidget(checkbox_dict["eta_" + str(idx)])
        checkbox_dict["chi_" + str(idx)] = QtWidgets.QCheckBox(self.frame)
        checkbox_dict["chi_" + str(idx)].setText("Chi")
        horizontalLayout.addWidget(checkbox_dict["chi_" + str(idx)])
        checkbox_dict["phi_" + str(idx)] = QtWidgets.QCheckBox(self.frame)
        checkbox_dict["phi_" + str(idx)].setText("Phi")
        horizontalLayout.addWidget(checkbox_dict["phi_" + str(idx)])
        checkbox_dict["nu_" + str(idx)] = QtWidgets.QCheckBox(self.frame)
        checkbox_dict["nu_" + str(idx)].setText("Nu")
        horizontalLayout.addWidget(checkbox_dict["nu_" + str(idx)])
        checkbox_dict["del_" + str(idx)] = QtWidgets.QCheckBox(self.frame)
        checkbox_dict["del_" + str(idx)].setText("Del")
        horizontalLayout.addWidget(checkbox_dict["del_" + str(idx)])
        self.verticalLayout_2.addLayout(horizontalLayout)
        horizontalLayout_2 = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        horizontalLayout_2.addItem(spacerItem)
        label = QtWidgets.QLabel(self.frame)
        label.setText("Start: ")
        horizontalLayout_2.addWidget(label)
        line_edit_dict["start"] = QtWidgets.QLineEdit(self.frame)
        horizontalLayout_2.addWidget(line_edit_dict["start"])
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        horizontalLayout_2.addItem(spacerItem1)
        label_2 = QtWidgets.QLabel(self.frame)
        label_2.setText("End: ")
        horizontalLayout_2.addWidget(label_2)
        line_edit_dict["end"] = QtWidgets.QLineEdit(self.frame)
        horizontalLayout_2.addWidget(line_edit_dict["end"])
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(horizontalLayout_2)
        line = QtWidgets.QFrame(self.frame)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout_2.addWidget(line)

        final_dict["checkboxes"] = checkbox_dict
        final_dict["line_edits"] = line_edit_dict
        return final_dict

    def build_time_step(self):
        label_stepntime = QtWidgets.QLabel(self.frame)
        label_stepntime.setText("Step and Time")
        label_stepntime.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        label_stepntime.setFont(QtGui.QFont("Sans Serif", weight=QtGui.QFont.Bold))
        self.verticalLayout_2.addWidget(label_stepntime)
        horizontalLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        horizontalLayout.addItem(spacerItem)
        label_step = QtWidgets.QLabel(self.frame)
        label_step.setText("Steps: ")
        horizontalLayout.addWidget(label_step)
        self.line_edit_step = QtWidgets.QLineEdit(self.frame)
        self.line_edit_step.setText("100")
        horizontalLayout.addWidget(self.line_edit_step)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        horizontalLayout.addItem(spacerItem1)
        label_time = QtWidgets.QLabel(self.frame)
        label_time.setText("Time: ")
        horizontalLayout.addWidget(label_time)
        self.line_edit_time = QtWidgets.QLineEdit(self.frame)
        self.line_edit_time.setText("0.1")
        horizontalLayout.addWidget(self.line_edit_time)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(horizontalLayout)
        line = QtWidgets.QFrame(self.frame)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout_2.addWidget(line)

    def build_scan_button(self):
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
        self.pushButton_start.clicked.connect(self.do_scan)

    def build_scan_cmd(self):
        cmd = "daf." + self.title + " "

        for line in self.motor_layout:
            for motor, checkbox in line["checkboxes"].items():
                if checkbox.isChecked():
                    cmd += "--" + motor.split("_")[0] + " "
            for key, line_edit in line["line_edits"].items():
                cmd += line_edit.text() + " "

        cmd += self.line_edit_step.text() + " "
        cmd += self.line_edit_time.text() + " "

        return cmd

    def do_scan(self):
        scan_cmd = self.build_scan_cmd()
        print(scan_cmd)
        subprocess.Popen(scan_cmd, shell=True)
        # os.system(scan_cmd)
