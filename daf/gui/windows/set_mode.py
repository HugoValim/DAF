from os import path
import subprocess

from pydm import Display
from qtpy.QtWidgets import QApplication, QWidget
from PyQt5 import QtGui, uic
from PyQt5.QtGui import QIcon

from daf.utils.dafutilities import DAFIO
from daf.gui.utils import format_5_dec, Icons, center_screen


class MyDisplay(QWidget):

    _MODE_TABLE_KEYS = [f"{col}{row}" for col in range(5) for row in range(7)]
    _CONS_NUMBERS = ("1", "2", "3")
    _CONS_LABELS = ("label_set_cons1", "label_set_cons2", "label_set_cons3")
    _SET_CONS_EDIT = ("lineEdit_set_cons1", "lineEdit_set_cons2", "lineEdit_set_cons3")
    _CONSTRAINT_ANGLES = {
        "chi": "cons_chi",
        "delta": "cons_del",
        "eta": "cons_eta",
        "mu": "cons_mu",
        "nu": "cons_nu",
        "phi": "cons_phi",
        "alpha": "cons_alpha",
        "beta": "cons_beta",
        "naz": "cons_naz",
        "omega": "cons_omega",
        "psi": "cons_psi",
        "qaz": "cons_qaz",
    }
    _STYLESHEET_DEFAULT = """
                                                qproperty-alignment: AlignCenter;
                                                border: 1px solid rgb(0, 0, 0);
                                                padding: 5px 0px;
                                                color: rgb(0, 0, 0);
                                                max-height: 16px;
                                                font-size: 14px;
                                            """
    _STYLESHEET_HIGHLIGHT = """

                                                        qproperty-alignment: AlignCenter;
                                                        border: 1px solid rgb(0, 0, 0);
                                                        padding: 5px 0px;
                                                        color: rgb(0, 0, 0);
                                                        max-height: 16px;
                                                        font-size: 14px;
                                                        background-color: green;

                                                """

    def __init__(self, update_dict: dict):
        super().__init__()
        self.app = QApplication.instance()
        uic.loadUi(self.ui_filepath(), self)
        self.set_icons()
        self.make_connections()
        # self.init_labels()
        self.highlight_table()
        self.default_labels()
        center_screen(self)
        self.update_dict = update_dict

    def ui_filename(self):
        return "set_mode.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def set_icons(self):
        """Set used icons"""
        self.mode_input_button.setIcon(QIcon(Icons.check))

    def make_connections(self):
        """Make the needed connections"""
        self.mode_input.textChanged.connect(self.highlight_table)
        self.mode_input.textChanged.connect(self.get_cons)
        self.mode_input.textChanged.connect(self.update_labels)
        self.mode_input_button.clicked.connect(self.set_mode)
        for edit in self._SET_CONS_EDIT:
            getattr(self, edit).textChanged.connect(self.get_cons)

    def init_labels(self):
        """Initialize labels disabled"""
        for label in self._CONS_LABELS:
            getattr(self, label).setEnabled(False)

    def _build_table_dict(self):
        """Build the table label dictionary."""
        return {key: getattr(self, f"label_mode{key}") for key in self._MODE_TABLE_KEYS}

    def _setup_dicts(self):
        """Make cons and set_cons dict"""
        cons_dict = {num: getattr(self, label) for num, label in zip(self._CONS_NUMBERS, self._CONS_LABELS)}
        set_cons_dict = {num: getattr(self, edit) for num, edit in zip(self._CONS_NUMBERS, self._SET_CONS_EDIT)}
        return cons_dict, set_cons_dict

    def default_labels(self):
        """Handle labels"""
        cons_dict, set_cons_dict = self._setup_dicts()
        for key in self._CONS_NUMBERS:
            if cons_dict[key].text() not in self.mode_list:
                cons_dict[key].setText("Constraint")
                set_cons_dict[key].setText("N/A")
                set_cons_dict[key].setEnabled(False)
                cons_dict[key].setEnabled(False)

    def update_labels(self):
        """Update constraint label names"""
        cons_dict, set_cons_dict = self._setup_dicts()
        dict_args = self.update_dict["default"]

        for key in self._CONS_NUMBERS:
            if (
                "=" not in cons_dict[key].text()
                and "Constraint" not in cons_dict[key].text()
            ):
                angle_now = cons_dict[key].text().lower().split(" ")[0]
                if angle_now in self._CONSTRAINT_ANGLES:
                    set_cons_dict[key].setText(
                        str(dict_args[self._CONSTRAINT_ANGLES[angle_now]])
                    )

    def highlight_table(self):
        """Logic to highlight the table"""
        table_dict = self._build_table_dict()

        column = 0
        self.mode_list = []
        for key in self._MODE_TABLE_KEYS:
            table_dict[key].setStyleSheet(self._STYLESHEET_DEFAULT)
            if len(str(self.mode_input.text())) >= column + 1:
                if key == str(self.mode_input.text())[column] + str(column):
                    table_dict[key].setStyleSheet(self._STYLESHEET_HIGHLIGHT)
                    column += 1
                    self.mode_list.append(table_dict[key].text())

            if column > 4:
                break

    def get_cons(self):
        """Get the current constraints and update this section on the fly"""
        cons_dict, set_cons_dict = self._setup_dicts()
        mode_cont = 1
        self.cons_table = []
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
        daf_cons_args = []
        for i in self.cons_table:
            if not "=" in i[0]:
                ang = (
                    i[0].split(" ")[0].lower()
                )  # get only the angle name in lower case
                fix_in = i[1]
                daf_cons_args.extend(["--cons_" + str(ang), str(fix_in)])
        p = subprocess.Popen(
            ["daf.mode", str(self.mode_input.text())], shell=False
        )
        p.wait()  # Wait for the first command, otherwise it'll not execute the second one
        if daf_cons_args:
            subprocess.Popen(["daf.cons"] + daf_cons_args, shell=False)
