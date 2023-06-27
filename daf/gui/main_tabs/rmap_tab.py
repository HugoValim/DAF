from os import path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QWidget, QMenu, QAction, QInputDialog, QComboBox
from PyQt5.QtCore import Qt

from daf.gui.windows.rmap_widget import RMapWidget

# import daf.gui.windows.bounds as bounds
from daf.gui.utils import format_5_dec, Icons, Counter
import daf.utils.experiment_configs as ec


class RMapTab(QWidget):
    def __init__(self, dafio):
        super().__init__()
        uic.loadUi(self.ui_filepath(), self)
        self.set_icons()
        self.make_connections()
        self.update_dict = None
        self.iter_counter = 0
        self.io = dafio
        self.current_rmap_samples = []
        self.idir = [0, 1, 0]
        self.ndir = [0, 0, 1]
        self.build_rmap_widget()

    def ui_filename(self):
        return "rmap_tab.ui"

    def ui_filepath(self):
        full_path = path.join(path.dirname(path.realpath(__file__)), "../ui/")
        full_image_path = path.join(full_path, self.ui_filename())
        return full_image_path

    def set_icons(self):
        """Set used icons"""
        self.pushButton_refresh.setIcon(QIcon(Icons.refresh))

    def make_connections(self):
        # RMap tab connections
        self.checkBox_rmap.stateChanged.connect(self.build_rmap_widget)
        self.pushButton_refresh.clicked.connect(self.build_rmap_widget)

    def build_rmap_widget(self):
        """Create the needed variables and instantiate the rmap widget"""
        self.rmap_widget(
            self.io.only_read(),
            samples=self.current_rmap_samples,
            idir=self.idir,
            ndir=self.ndir,
        )

    def rmap_widget(self, data, samples, idir, ndir):
        """Build the RMap graph"""
        self.rmap_plot = RMapWidget(
            dict_args=data,
            move=self.checkBox_rmap.isChecked(),
            samples=samples,
            idirp=idir,
            ndirp=ndir,
        )
        plt.close(
            self.rmap_plot.ax.figure
        )  # Must have that, otherwise it will consume all the RAM opening figures
        for i in reversed(range(self.verticalLayout_rmap.count())):
            self.verticalLayout_rmap.itemAt(i).widget().setParent(None)
        toolbar = NavigationToolbar(self.rmap_plot, self)
        self.verticalLayout_rmap.addWidget(toolbar)
        self.verticalLayout_rmap.addWidget(self.rmap_plot)
        # self.rmap_menu()
        self.rmap_plot.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rmap_plot.customContextMenuRequested[QtCore.QPoint].connect(
            self.rmap_menu_builder
        )

    def rmap_menu_builder(self):
        """Build the menu that will pop when with right clicks in the graph"""
        self.rmap_menu = QMenu(self.rmap_plot)
        # Refresh plot
        refresh_plot = self.rmap_menu.addAction("Refresh")
        refresh_plot.triggered.connect(self.build_rmap_widget)
        # Clear other samples in graph
        idir = self.rmap_menu.addAction("IDir ({})".format(self.idir))
        idir.triggered.connect(self.idir_manager)
        # Clear other samples in graph
        ndir = self.rmap_menu.addAction("Ndir ({})".format(self.ndir))
        ndir.triggered.connect(self.ndir_manager)
        # Add more samples to the graph
        add_samples = self.rmap_menu.addAction("Add Samples")
        add_samples.triggered.connect(self.rmap_add_samples)
        # Clear other samples in graph
        clear_plot = self.rmap_menu.addAction("Clear")
        clear_plot.triggered.connect(self.clear_plot_samples)

        self.rmap_menu.exec_(QtGui.QCursor.pos())

    def idir_manager(self):
        text, result = QInputDialog.getText(
            self, "Set IDir", "Enter with the new IDir with the format a,b,c"
        )
        if result:
            self.idir = [float(i) for i in text.split(",")]
        self.build_rmap_widget()

    def ndir_manager(self):
        text, result = QInputDialog.getText(
            self, "Set NDir", "Enter with the new NDir with the format a,b,c"
        )
        if result:
            self.ndir = [float(i) for i in text.split(",")]
        self.build_rmap_widget()

    def rmap_add_samples(self):
        self.combo_box = QComboBox()
        predefined_samples = [i for i in ec.samples]
        user_samples = self.io.read()["user_samples"]
        for sample in user_samples.keys():
            predefined_samples.append(sample)
        predefined_samples.sort()
        # adding list of items to combo box
        self.combo_box.addItems(predefined_samples)
        self.combo_box.move(QtGui.QCursor.pos())
        self.combo_box.currentTextChanged.connect(self.current_rmap_samples_manager)
        self.combo_box.showPopup()

    def clear_plot_samples(self):
        self.current_rmap_samples = []
        self.build_rmap_widget()

    def current_rmap_samples_manager(self, choice):
        if choice in self.current_rmap_samples:
            self.current_rmap_samples.remove(choice)
        else:
            self.current_rmap_samples.append(choice)
        self.build_rmap_widget()

    def update(self, update_dict: dict = None) -> None:
        self.update_dict = update_dict
