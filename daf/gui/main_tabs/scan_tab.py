from os import path
import os
import subprocess

import yaml

from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QWidget, QComboBox, QMenu


from daf.gui.utils import format_5_dec, Icons, Counter
from daf.utils.daf_paths import DAFPaths as dp
import daf.config.counters_config as cc
import daf.gui.windows.scan_gui_daf as scan_gui_daf
import daf.gui.windows.scan_hkl_daf as scan_hkl_daf


class ScanTab(QWidget):
    default_config_path = dp.SCAN_CONFIGS
    config_file_prefix = "config."
    config_file_sufix = ".yml"

    _ASCAN_BUTTONS = [(i, f"pushButton_a{i}scan") for i in range(1, 7)]
    _DSCAN_BUTTONS = [(i, f"pushButton_d{i}scan") for i in range(1, 7)]
    _MESH_BUTTONS = [(2, "pushButton_m2scan")]

    def __init__(self, dafio):
        super().__init__()
        uic.loadUi(self.ui_filepath(), self)
        self.make_connections()
        self.update_dict = None
        self.io = dafio
        self.set_scan_properties()
        self.scan_windows = {}

    def ui_filename(self):
        return "scan_tab.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def set_icons(self):
        """Set used icons"""
        self.pushButton_refresh.setIcon(QIcon(Icons.refresh))

    def make_connections(self):
        # Scan tab
        self.listWidget_files.itemSelectionChanged.connect(
            self.on_counters_list_widget_change
        )
        self.listWidget_files.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget_files.customContextMenuRequested[QtCore.QPoint].connect(
            self.files_menu_builder
        )
        self.listWidget_counters.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget_counters.customContextMenuRequested[QtCore.QPoint].connect(
            self.counters_menu_builder
        )

        # Scans - absolute
        for n, btn_name in self._ASCAN_BUTTONS:
            getattr(self, btn_name).clicked.connect(lambda _, n=n: self.open_scan_window(n, "abs"))

        # Scans - relative
        for n, btn_name in self._DSCAN_BUTTONS:
            getattr(self, btn_name).clicked.connect(lambda _, n=n: self.open_scan_window(n, "rel"))

        # Scans - mesh
        for n, btn_name in self._MESH_BUTTONS:
            getattr(self, btn_name).clicked.connect(lambda _, n=n: self.open_scan_window(n, "mesh"))

        self.pushButton_hklscan.clicked.connect(lambda: self.open_hkl_scan_window())

        self.live_view_launcher.clicked.connect(self.open_live_view)

    def update(self, update_dict: dict = None) -> None:
        self.update_dict = update_dict
        self.update_labels()

    def update_labels(self):
        """Update labels"""
        self.label_main_counter.setText(
            self.update_dict["default"]["main_scan_counter"]
        )
        self.label_current_config.setText(
            self.update_dict["default"]["default_counters"].split(".")[1]
        )

    def open_scan_window(self, n_motors, scan_type):
        self.scan_windows[scan_type + str(n_motors)] = scan_gui_daf.MyWindow(
            n_motors, scan_type
        )
        self.scan_windows[scan_type + str(n_motors)].show()

    def open_hkl_scan_window(self):
        self.scan_hkl_window = scan_hkl_daf.MyWindow()
        self.scan_hkl_window.show()

    def set_scan_properties(self):
        """Set properties showed in scan tab in daf.gui"""
        dict_ = self.io.read()
        self.main_counter = dict_["main_scan_counter"]
        self.label_current_config.setText(dict_["default_counters"].split(".")[1])
        self.label_main_counter.setText(dict_["main_scan_counter"])
        self.counters_scroll_area()

    def files_menu_builder(self):
        """Build the menu that will pop when with right clicks in the listWidget_files"""
        self.files_menu = QMenu(self.listWidget_files)
        # New File
        new_file = self.files_menu.addAction("New File")
        new_file.triggered.connect(self.new_counter_file)
        # Remove File
        remove_file = self.files_menu.addAction("Remove File")
        remove_file.triggered.connect(self.remove_counter_file)
        # Set Config File
        set_config = self.files_menu.addAction("Set Config")
        set_config.triggered.connect(self.set_counter)

        self.files_menu.popup(QtGui.QCursor.pos())

    def counters_menu_builder(self):
        """Build the menu that will pop when with right clicks in the listWidget_counters"""
        self.counters_menu = QMenu(self.listWidget_counters)
        # New File
        add_counter = self.counters_menu.addAction("Add Counter")
        add_counter.triggered.connect(self.add_counter_manager)
        # Remove File
        remove_counter = self.counters_menu.addAction("Remove Counter")
        remove_counter.triggered.connect(self.remove_counter)

        set_main_counter = self.counters_menu.addAction("Set As Main")
        set_main_counter.triggered.connect(self.set_main_counter)

        self.counters_menu.popup(QtGui.QCursor.pos())

    def add_prefix_and_suffix_to_config(self, file: str) -> str:
        full_file_name = self.config_file_prefix + file + self.config_file_sufix
        return full_file_name

    def list_config_files(self) -> list:
        """List all configuration files without prefix and suffix"""
        configs = os.listdir(self.default_config_path)
        configs = [
            i.split(".")[1]
            for i in configs
            if len(i.split(".")) == 3 and i.endswith(".yml")
        ]
        return configs

    @staticmethod
    def list_all_counters() -> list:
        """List all available counters for the current beamline"""
        return [i for i in cc.counters_config.keys()]

    def get_all_counters_in_selected_file(self) -> list:
        """Get counter in a file and return a list with them"""
        defaut_file = self.add_prefix_and_suffix_to_config(self.current_config_file)
        file_path = os.path.join(self.default_config_path, defaut_file)
        with open(file_path) as file:
            data = yaml.safe_load(file)
            return data

    def counters_scroll_area(self) -> None:
        """List all possible counter configs file"""
        configs = self.list_config_files()
        configs.sort()
        self.listWidget_files.clear()
        self.listWidget_files.addItems(configs)

    def fill_counter_list_widget(self, items: list) -> None:
        """Fill the listWidget_counters with the counters in the selected file"""
        self.listWidget_counters.clear()
        for item in items:
            self.listWidget_counters.addItem(item)

    def on_counters_list_widget_change(self):
        """Print the counters on a setup when selected"""
        configs = self.list_config_files()
        item = self.listWidget_files.currentItem()
        value = item.text()
        self.current_config_file = value
        if value in configs:
            items = self.get_all_counters_in_selected_file()
            self.fill_counter_list_widget(items)

    def set_counter(self):
        item = self.listWidget_files.currentItem()
        value = item.text()
        subprocess.Popen(["daf.mc", "-s", value], shell=False)
        self.label_current_config.setText(value)

    def set_main_counter(self):
        counter = self.listWidget_counters.currentItem().text()
        self.label_main_counter.setText(counter)
        subprocess.Popen(["daf.mc", "-m", counter], shell=False)

    def new_counter_file(self):
        configs = self.list_config_files()
        text, result = QtWidgets.QInputDialog.getText(
            self, "Input Dialog", "New config file name"
        )

        if result:
            if text in configs:
                msgbox = QtWidgets.QMessageBox()
                msgbox_text = "Config file {} already exists, \ndo you want to overwrite it?".format(
                    text
                )
                ret = msgbox.question(
                    self,
                    "Warning",
                    msgbox_text,
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                    QtWidgets.QMessageBox.Cancel,
                )

                if ret == QtWidgets.QMessageBox.Ok:
                    subprocess.Popen(["daf.mc", "-n", text], shell=False)

            else:
                subprocess.Popen(["daf.mc", "-n", text], shell=False)
        self.counters_scroll_area()

    def add_counter_manager(self):
        self.combo_box = QComboBox()
        counters = self.list_all_counters()
        self.combo_box.addItems(counters)
        self.combo_box.move(QtGui.QCursor.pos())
        self.combo_box.activated.connect(self.add_counter)
        self.combo_box.showPopup()

    def add_counter(self, choice):
        """Add a counter to a setup"""
        file = self.listWidget_files.currentItem().text()
        counter = self.combo_box.currentText()
        subprocess.Popen(["daf.mc", "-a", file, counter], shell=False)
        self.on_counters_list_widget_change()

    def remove_counter_file(self):
        item = self.listWidget_files.currentItem()
        value = item.text()
        subprocess.Popen(["daf.mc", "-r", value], shell=False)
        self.counters_scroll_area()

    def remove_counter(self):
        get_selected = self.listWidget_counters.currentItem()
        if get_selected is not None:
            item = self.listWidget_files.currentItem()
            value = item.text()
            counter = get_selected.text()
            subprocess.Popen(["daf.mc", "-rc", value, counter], shell=False)
            self.on_counters_list_widget_change()

    def open_live_view(self):
        subprocess.Popen(["daf.live"], shell=False)
