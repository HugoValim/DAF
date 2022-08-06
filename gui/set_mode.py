from os import path
import subprocess

from pydm import Display
from qtpy.QtWidgets import QApplication
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

import daf.utils.dafutilities as du

DEFAULT = ".Experiment"


class MyDisplay(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.app = QApplication.instance()
        self.build_icons()
        self.set_icons()
        self.make_connections()
        # self.init_labels()
        self.highlight_table()
        self.default_labels()
        self.center()

    #
    def ui_filename(self):
        return "ui/set_mode.ui"

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
        self.mode_input_button.setIcon(QIcon(self.check_icon))

    def make_connections(self):
        """Make the needed connections"""
        self.ui.mode_input.textChanged.connect(self.highlight_table)
        self.ui.mode_input.textChanged.connect(self.get_cons)
        self.ui.mode_input.textChanged.connect(self.update_labels)
        self.ui.mode_input_button.clicked.connect(self.set_mode)
        self.ui.lineEdit_set_cons1.textChanged.connect(self.get_cons)
        self.ui.lineEdit_set_cons2.textChanged.connect(self.get_cons)
        self.ui.lineEdit_set_cons3.textChanged.connect(self.get_cons)

    def init_labels(self):
        """Initialize labels disabled"""
        self.ui.label_set_cons1.setEnabled(False)
        self.ui.label_set_cons2.setEnabled(False)
        self.ui.label_set_cons3.setEnabled(False)

    def setup_dicts(self):
        """Make cons and set_cons dict"""
        cons_dict = {
            "1": self.ui.label_set_cons1,
            "2": self.ui.label_set_cons2,
            "3": self.ui.label_set_cons3,
        }
        set_cons_dict = {
            "1": self.ui.lineEdit_set_cons1,
            "2": self.ui.lineEdit_set_cons2,
            "3": self.ui.lineEdit_set_cons3,
        }
        return cons_dict, set_cons_dict

    def default_labels(self):
        """Handle labels"""
        cons_dict, set_cons_dict = self.setup_dicts()
        for key in cons_dict.keys():
            if cons_dict[key].text() not in self.mode_list:
                cons_dict[key].setText("Constraint")
                set_cons_dict[key].setText("N/A")
                set_cons_dict[key].setEnabled(False)
                cons_dict[key].setEnabled(False)

    def update_labels(self):
        """Update constraint label names"""
        cons_dict, set_cons_dict = self.setup_dicts()
        # Update constraint fields with the angles written in .Experement file
        dict_args = du.read()
        dict_cons_angles = {
            "chi": "cons_Chi",
            "delta": "cons_Del",
            "eta": "cons_Eta",
            "mu": "cons_Mu",
            "nu": "cons_Nu",
            "phi": "cons_Phi",
            "alpha": "cons_alpha",
            "beta": "cons_beta",
            "naz": "cons_naz",
            "omega": "cons_omega",
            "psi": "cons_psi",
            "qaz": "cons_qaz",
        }

        for key in cons_dict.keys():
            # print(cons_dict[key].text().lower().split(' ')[0])
            if (
                "=" not in cons_dict[key].text()
                and "Constraint" not in cons_dict[key].text()
            ):
                angle_now = cons_dict[key].text().lower().split(" ")[0]
                if angle_now in dict_cons_angles.keys():
                    set_cons_dict[key].setText(
                        str(dict_args[dict_cons_angles[angle_now]])
                    )

    def highlight_table(self):
        """Logic to highlight the table"""
        table_dict = {
            "00": self.ui.label_mode00,
            "10": self.ui.label_mode10,
            "20": self.ui.label_mode20,
            "30": self.ui.label_mode30,
            "40": self.ui.label_mode40,
            "50": self.ui.label_mode50,
            "60": self.ui.label_mode60,
            "01": self.ui.label_mode01,
            "11": self.ui.label_mode11,
            "21": self.ui.label_mode21,
            "31": self.ui.label_mode31,
            "41": self.ui.label_mode41,
            "51": self.ui.label_mode51,
            "61": self.ui.label_mode61,
            "02": self.ui.label_mode02,
            "12": self.ui.label_mode12,
            "22": self.ui.label_mode22,
            "32": self.ui.label_mode32,
            "42": self.ui.label_mode42,
            "52": self.ui.label_mode52,
            "62": self.ui.label_mode62,
            "03": self.ui.label_mode03,
            "13": self.ui.label_mode13,
            "23": self.ui.label_mode23,
            "33": self.ui.label_mode33,
            "43": self.ui.label_mode43,
            "53": self.ui.label_mode53,
            "63": self.ui.label_mode63,
            "04": self.ui.label_mode04,
            "14": self.ui.label_mode14,
            "24": self.ui.label_mode24,
            "34": self.ui.label_mode34,
            "44": self.ui.label_mode44,
            "54": self.ui.label_mode54,
            "64": self.ui.label_mode64,
        }

        column = 0
        self.mode_list = []  # list to store the current mode
        for key in table_dict.keys():
            table_dict[key].setStyleSheet(
                """   
                                                qproperty-alignment: AlignCenter;
                                                border: 1px solid rgb(0, 0, 0);
                                                padding: 5px 0px;
                                                color: rgb(0, 0, 0);
                                                max-height: 16px;
                                                font-size: 14px;
                                            """
            )
            if len(str(self.ui.mode_input.text())) >= column + 1:
                if key == str(self.ui.mode_input.text())[column] + str(column):
                    table_dict[key].setStyleSheet(
                        """
                                                        
                                                        qproperty-alignment: AlignCenter;
                                                        border: 1px solid rgb(0, 0, 0);
                                                        padding: 5px 0px;
                                                        color: rgb(0, 0, 0);
                                                        max-height: 16px;
                                                        font-size: 14px;
                                                        background-color: green;

                                                """
                    )
                    column += 1
                    self.mode_list.append(table_dict[key].text())

            if column > 4:
                break

    def get_cons(self):
        """Get the current constraints and update this section on the fly"""
        cons_dict, set_cons_dict = self.setup_dicts()
        mode_cont = 1
        self.cons_table = []  # table to store the constraints to be passed to daf.cons
        for i in self.mode_list:
            if i != "." and i != "X":
                if mode_cont <= 3:
                    cons_dict[str(mode_cont)].setText(i)
                    self.cons_table.append((i, set_cons_dict[str(mode_cont)].text()))
                    if "=" in i:
                        set_cons_dict[str(mode_cont)].setText("N/A")
                        set_cons_dict[str(mode_cont)].setEnabled(False)
                        cons_dict[str(mode_cont)].setEnabled(False)
                    else:
                        cons_dict[str(mode_cont)].setEnabled(True)
                        set_cons_dict[str(mode_cont)].setEnabled(True)
                    mode_cont += 1
        self.default_labels()

    def set_mode(self):
        """Set the mode and the constraints"""
        daf_cons_args = ""
        for i in self.cons_table:
            if not "=" in i[0]:
                ang = (
                    i[0].split(" ")[0].lower()
                )  # get only the angle name in lower case
                fix_in = i[1]
                if ang in ["mu", "eta", "chi", "phi", "nu", "del"]:
                    ang = ang.capitalize()
                arg = "--cons_" + str(ang) + " " + str(fix_in) + " "
                daf_cons_args += arg
        p = subprocess.Popen(
            "daf.mode {} ".format(str(self.ui.mode_input.text())), shell=True
        )
        p.wait()  # Wait for the first command, otherwise it'll not execute the second one
        subprocess.Popen("daf.cons {} ".format(daf_cons_args), shell=True)
