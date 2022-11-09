import os
from os import path

import yaml
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import (
    QApplication,
    QTreeWidgetItem,
    QMenu,
    QAction,
    QHeaderView,
    QTableWidgetItem,
    QComboBox,
)
from pydm import Display
import qdarkstyle
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt

# DAF GUIs imports
import scan_gui_daf
import scan_hkl_daf
import set_mode
import experiment
import sample
import ub
import bounds
import goto_hkl
import daf.utils.dafutilities as du
import daf.utils.daf_paths as dp
from update_gui import Worker
from rmap_widget import RMapWidget

DEFAULT = ".Experiment"


class MyDisplay(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.io = du.DAFIO()
        self.app = QApplication.instance()
        self.set_main_screen_title()
        self.current_theme = None
        self._createMenuBar()
        self.default_theme()
        self.set_scan_prop()
        self.setup_scroll_area()
        self.scan = False
        self.make_connections()
        self.build_icons()
        self.set_icons()
        self.set_tab_order()
        self.runLongTask()
        self.current_rmap_samples = []
        self.idir = [0, 1, 0]
        self.ndir = [0, 0, 1]
        self.rmap_widget(
            self.io.read(),
            samples=self.current_rmap_samples,
            idir=self.idir,
            ndir=self.ndir,
        )
        self.delay = 5  # Some thing in GUI dont need to be updated every update call
        self.delay_counter = (
            self.delay
        )  # Cooldown to delay, it start with the same value so it runs in the first loop
        self.scan_windows = {}

    def ui_filename(self):
        return "ui/main.ui"

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def build_icons(self):
        pixmap_path = path.join(path.dirname(path.realpath(__file__)), "ui/icons")
        self.settings_icon = path.join(pixmap_path, "settings.svg")
        self.cached_icon = path.join(pixmap_path, "cached1.svg")

    def set_icons(self):
        self.b_icon_size_h = 20
        self.b_icon_size_v = 20

        self.pushButton_mode.setIconSize(
            QtCore.QSize(self.b_icon_size_h, self.b_icon_size_v)
        )
        self.pushButton_mode.setIcon(QIcon(self.settings_icon))
        self.pushButton_expt.setIconSize(
            QtCore.QSize(self.b_icon_size_h, self.b_icon_size_v)
        )
        self.pushButton_expt.setIcon(QIcon(self.settings_icon))
        self.pushButton_sample.setIconSize(
            QtCore.QSize(self.b_icon_size_h, self.b_icon_size_v)
        )
        self.pushButton_sample.setIcon(QIcon(self.settings_icon))
        self.pushButton_ub.setIconSize(
            QtCore.QSize(self.b_icon_size_h, self.b_icon_size_v)
        )
        self.pushButton_ub.setIcon(QIcon(self.settings_icon))
        self.pushButton_bounds.setIconSize(
            QtCore.QSize(self.b_icon_size_h, self.b_icon_size_v)
        )
        self.pushButton_bounds.setIcon(QIcon(self.settings_icon))
        self.pushButton_move.setIconSize(
            QtCore.QSize(self.b_icon_size_h, self.b_icon_size_v)
        )
        self.pushButton_move.setIcon(QIcon(self.settings_icon))
        self.pushButton_refresh.setIconSize(
            QtCore.QSize(self.b_icon_size_h, self.b_icon_size_v)
        )
        self.pushButton_refresh.setIcon(QIcon(self.cached_icon))

    def set_tab_order(self):

        # Scan
        self.setTabOrder(self.ui.tab_scan, self.lineEdit_scan_path)
        self.setTabOrder(self.lineEdit_scan_path, self.lineEdit_scan_file)
        self.setTabOrder(self.lineEdit_scan_file, self.ui.listWidget_counters)
        self.setTabOrder(self.ui.listWidget_counters, self.ui.treeWidget_counters)
        self.setTabOrder(
            self.ui.treeWidget_counters, self.ui.pushButton_new_counter_file
        )
        self.setTabOrder(
            self.ui.pushButton_new_counter_file, self.ui.pushButton_remove_counter_file
        )
        self.setTabOrder(
            self.ui.pushButton_remove_counter_file,
            self.ui.pushButton_set_config_counter,
        )
        self.setTabOrder(
            self.ui.pushButton_set_config_counter, self.ui.comboBox_counters
        )
        self.setTabOrder(self.ui.comboBox_counters, self.ui.pushButton_add_counter)
        self.setTabOrder(
            self.ui.pushButton_add_counter, self.ui.pushButton_remove_counter
        )
        self.setTabOrder(self.ui.pushButton_remove_counter, self.ui.tab_scan)

        # Setup
        self.setTabOrder(self.ui.tab_setup, self.ui.listWidget_setup)
        self.setTabOrder(self.ui.listWidget_setup, self.ui.pushButton_new_setup)
        self.setTabOrder(self.ui.pushButton_new_setup, self.ui.pushButton_save_setup)
        self.setTabOrder(self.ui.pushButton_save_setup, self.ui.pushButton_copy_setup)
        self.setTabOrder(self.ui.pushButton_copy_setup, self.ui.pushButton_remove_setup)
        self.setTabOrder(
            self.ui.pushButton_remove_setup, self.ui.pushButton_change_setup
        )
        self.setTabOrder(
            self.ui.pushButton_change_setup, self.ui.pushButton_update_desc
        )
        self.setTabOrder(self.ui.pushButton_update_desc, self.ui.tab_setup)

    def make_connections(self):

        # Secundary GUIs
        self.pushButton_mode.clicked.connect(lambda: self.open_mode_window())
        self.pushButton_expt.clicked.connect(lambda: self.open_experiment_window())
        self.pushButton_sample.clicked.connect(lambda: self.open_sample_window())
        self.pushButton_ub.clicked.connect(lambda: self.open_ub_window())
        self.pushButton_bounds.clicked.connect(lambda: self.open_bounds_window())
        self.pushButton_move.clicked.connect(lambda: self.open_goto_hkl_window())

        self.ui.listWidget_setup.itemSelectionChanged.connect(
            self.on_list_widget_change
        )
        self.ui.listWidget_counters.itemSelectionChanged.connect(
            self.on_counters_list_widget_change
        )

        # Scan tab
        self.ui.pushButton_set_config_counter.clicked.connect(self.set_counter)
        self.ui.pushButton_new_counter_file.clicked.connect(self.new_counter_file)
        self.ui.pushButton_remove_counter_file.clicked.connect(self.remove_counter_file)
        self.ui.pushButton_add_counter.clicked.connect(self.add_counter)
        self.ui.pushButton_remove_counter.clicked.connect(self.remove_counter)
        self.comboBox_main_counter.currentTextChanged.connect(self.change_main_counter)

        # Scans
        self.pushButton_ascan.clicked.connect(lambda: self.open_scan_window(1, "abs"))
        self.pushButton_a2scan.clicked.connect(lambda: self.open_scan_window(2, "abs"))
        self.pushButton_a3scan.clicked.connect(lambda: self.open_scan_window(3, "abs"))
        self.pushButton_a4scan.clicked.connect(lambda: self.open_scan_window(4, "abs"))
        self.pushButton_a5scan.clicked.connect(lambda: self.open_scan_window(5, "abs"))
        self.pushButton_a6scan.clicked.connect(lambda: self.open_scan_window(6, "abs"))

        self.pushButton_dscan.clicked.connect(lambda: self.open_scan_window(1, "rel"))
        self.pushButton_d2scan.clicked.connect(lambda: self.open_scan_window(2, "rel"))
        self.pushButton_d3scan.clicked.connect(lambda: self.open_scan_window(3, "rel"))
        self.pushButton_d4scan.clicked.connect(lambda: self.open_scan_window(4, "rel"))
        self.pushButton_d5scan.clicked.connect(lambda: self.open_scan_window(5, "rel"))
        self.pushButton_d6scan.clicked.connect(lambda: self.open_scan_window(6, "rel"))

        self.pushButton_m2scan.clicked.connect(lambda: self.open_scan_window(2, "mesh"))

        self.pushButton_hklscan.clicked.connect(lambda: self.open_hkl_scan_window())

        # Setup buttons
        self.ui.pushButton_new_setup.clicked.connect(self.new_setup_dialog)
        self.ui.pushButton_save_setup.clicked.connect(self.save_setup)
        self.ui.pushButton_copy_setup.clicked.connect(self.copy_setup)
        self.ui.pushButton_change_setup.clicked.connect(self.change_setup)
        self.ui.pushButton_update_desc.clicked.connect(self.update_setup_description)
        self.ui.pushButton_remove_setup.clicked.connect(self.remove_setup)

        # Menu connections
        self.menu_bar.triggered.connect(self.style_sheet_handler)

        # RMap tab connections
        self.checkBox_rmap.stateChanged.connect(
            lambda: self.rmap_widget(
                self.worker.data_to_update["dargs"],
                samples=self.current_rmap_samples,
                idir=self.idir,
                ndir=self.ndir,
            )
        )
        self.pushButton_refresh.clicked.connect(
            lambda: self.rmap_widget(
                self.worker.data_to_update["dargs"],
                samples=self.current_rmap_samples,
                idir=self.idir,
                ndir=self.ndir,
            )
        )

    def _createMenuBar(self):
        """Create the menu bar and shortcuts"""
        self.menu_bar = self.app.main_window.menuBar()
        self.menu_bar.clear()
        # Creating menus using a QMenu object
        self.file_menu = QMenu("&File", self)
        self.option_menu = QMenu("&Options", self)

        self.menu_bar.addMenu(self.file_menu)
        open_action = self.file_menu.addAction("&Open File")
        open_action.setShortcut("Ctrl+o")

        self.menu_bar.addMenu(self.option_menu)
        style_action = self.option_menu.addAction(
            QAction("Dark Theme", self.menu_bar, checkable=True)
        )

    def default_theme(self):
        dict_args = self.io.read()
        if dict_args["dark_mode"]:
            self.current_theme = "dark"
            style = qdarkstyle.load_stylesheet_pyqt5()
            self.tableWidget_U.setMaximumHeight(97)
            self.tableWidget_UB.setMaximumHeight(97)
            self.app.setStyleSheet(style)
            for action in self.option_menu.actions():
                if action.text() == "Dark Theme":
                    action.setChecked(True)
        else:
            self.current_theme = "light"
            self.tableWidget_U.setMaximumHeight(92)
            self.tableWidget_UB.setMaximumHeight(92)
            self.app.setStyleSheet("")
            for action in self.option_menu.actions():
                if action.text() == "Dark Theme":
                    action.setChecked(False)

    def style_sheet_handler(self):
        dict_args = self.io.read()
        for action in self.option_menu.actions():
            if action.text() == "Dark Theme":
                if action.isChecked():
                    self.current_theme = "dark"
                    style = qdarkstyle.load_stylesheet_pyqt5()
                    self.tableWidget_U.setMaximumHeight(97)
                    self.tableWidget_UB.setMaximumHeight(97)
                    self.app.setStyleSheet(style)
                    dict_args["dark_mode"] = 1
                    du.write(dict_args)
                else:
                    self.current_theme = "light"
                    self.tableWidget_U.setMaximumHeight(92)
                    self.tableWidget_UB.setMaximumHeight(92)
                    self.app.setStyleSheet("")
                    dict_args["dark_mode"] = 0
                    du.write(dict_args)

    def load_data(self):
        # Extract the directory of this file...
        base_dir = os.path.dirname(os.path.realpath(__file__))
        # Concatenate the directory with the file name...
        data_file = os.path.join(base_dir, "motor_fields_default.yml")
        # Open the file so we can read the data...
        with open(data_file, "r") as file:
            data = yaml.safe_load(file)
            return data

    def set_main_screen_title(self):
        dict_ = self.io.read()
        # self.app.main_window.setWindowTitle('teste')
        self.ui.setWindowTitle("DAF GUI ({})".format(dict_["setup"]))

    def update_main_screen_title(self):
        dict_ = self.io.read()
        self.app.main_window.setWindowTitle(
            "DAF GUI ({}) - PyDM".format(dict_["setup"])
        )

    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.worker.update_labels.connect(self.update)

    def open_scan_window(self, n_motors, scan_type):
        self.scan_windows[scan_type + str(n_motors)] = scan_gui_daf.MyWindow(
            n_motors, scan_type
        )
        self.scan_windows[scan_type + str(n_motors)].show()

    def open_hkl_scan_window(self):
        self.scan_hkl_window = scan_hkl_daf.MyWindow()
        self.scan_hkl_window.show()

    def open_mode_window(self):
        self.mode_window = set_mode.MyDisplay()
        self.mode_window.show()

    def open_experiment_window(self):
        self.experiment_window = experiment.MyDisplay()
        self.experiment_window.show()

    def open_sample_window(self):
        self.sample_window = sample.MyDisplay()
        self.sample_window.show()

    def open_ub_window(self):
        self.ub_window = ub.MyDisplay()
        self.ub_window.show()

    def open_bounds_window(self):
        self.bounds_window = bounds.MyDisplay()
        self.bounds_window.show()

    def open_goto_hkl_window(self):
        self.goto_hkl_window = goto_hkl.MyDisplay()
        self.goto_hkl_window.show()

    def refresh_pydm_motors(self):
        translate = QCoreApplication.translate

        # set del motor labels
        data = self.io.read()
        del_channel = "ca://" + data["motors"]["del"]["pv"]
        self.ui.PyDMLabel_del_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.ui.PyDMLabel_del_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.ui.PyDMLabel_del_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.ui.PyDMByteIndicator_del.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.ui.PyDMPushButton_del.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set eta motor labels

        del_channel = "ca://" + data["motors"]["eta"]["pv"]
        self.ui.PyDMLabel_eta_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.ui.PyDMLabel_eta_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.ui.PyDMLabel_eta_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.ui.PyDMByteIndicator_eta.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.ui.PyDMPushButton_eta.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set chi motor labels

        del_channel = "ca://" + data["motors"]["chi"]["pv"]
        self.ui.PyDMLabel_chi_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.ui.PyDMLabel_chi_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.ui.PyDMLabel_chi_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.ui.PyDMByteIndicator_chi.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.ui.PyDMPushButton_chi.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set phi motor labels

        del_channel = "ca://" + data["motors"]["phi"]["pv"]
        self.ui.PyDMLabel_phi_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.ui.PyDMLabel_phi_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.ui.PyDMLabel_phi_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.ui.PyDMByteIndicator_phi.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.ui.PyDMPushButton_phi.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set nu motor labels

        del_channel = "ca://" + data["motors"]["nu"]["pv"]
        self.ui.PyDMLabel_nu_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.ui.PyDMLabel_nu_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.ui.PyDMLabel_nu_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.ui.PyDMByteIndicator_nu.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.ui.PyDMPushButton_nu.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

        # set mu motor labels

        del_channel = "ca://" + data["motors"]["mu"]["pv"]
        self.ui.PyDMLabel_mu_desc.setProperty(
            "channel", translate("Form", del_channel + ".DESC")
        )
        self.ui.PyDMLabel_mu_val.setProperty(
            "channel", translate("Form", del_channel + ".VAL")
        )
        self.ui.PyDMLabel_mu_rbv.setProperty(
            "channel", translate("Form", del_channel + ".RBV")
        )
        self.ui.PyDMByteIndicator_mu.setProperty(
            "channel", translate("Form", del_channel + ".MOVN")
        )
        self.ui.PyDMPushButton_mu.setProperty(
            "channel", translate("Form", del_channel + ".STOP")
        )

    def rmap_widget(self, data, samples, idir, ndir):
        # Build the RMap graph
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
        refresh_plot.triggered.connect(
            lambda: self.rmap_widget(
                self.worker.data_to_update["dargs"],
                samples=self.current_rmap_samples,
                idir=self.idir,
                ndir=self.ndir,
            )
        )
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
        text, result = QtWidgets.QInputDialog.getText(
            self, "Set IDir", "Enter with the new IDir with the format a,b,c"
        )
        if result:
            self.idir = [float(i) for i in text.split(",")]
        self.rmap_widget(
            self.worker.data_to_update["dargs"],
            samples=self.current_rmap_samples,
            idir=self.idir,
            ndir=self.ndir,
        )

    def ndir_manager(self):
        text, result = QtWidgets.QInputDialog.getText(
            self, "Set NDir", "Enter with the new NDir with the format a,b,c"
        )
        if result:
            self.ndir = [float(i) for i in text.split(",")]
        self.rmap_widget(
            self.worker.data_to_update["dargs"],
            samples=self.current_rmap_samples,
            idir=self.idir,
            ndir=self.ndir,
        )

    def rmap_add_samples(self):
        self.combo_box = QComboBox()
        items = [
            "Si",
            "Al",
            "Co",
            "Cu",
            "Cr",
            "Fe",
            "Ge",
            "Sn",
            "LaB6",
            "Al2O3",
            "C",
            "C_HOPG",
            "InAs",
            "InP",
            "InSb",
            "GaP",
            "GaAs",
            "AlAs",
            "GaSb",
            "GaAsWZ",
            "GaAs4H",
            "GaPWZ",
            "InPWZ",
            "InAs4H",
            "InSbWZ",
            "InSb4H",
            "PbTe",
            "PbSe",
            "CdTe",
            "CdSe",
            "CdSe_ZB",
            "HgSe",
            "NaCl",
            "MgO",
            "GaN",
            "BaF2",
            "SrF2",
            "CaF2",
            "MnO",
            "MnTe",
            "GeTe",
            "SnTe",
            "Au",
            "Ti",
            "Mo",
            "Ru",
            "Rh",
            "V",
            "Ta",
            "Nb",
            "Pt",
            "Ag2Se",
            "TiO2",
            "MnO2",
            "VO2_Rutile",
            "VO2_Baddeleyite",
            "SiO2",
            "In",
            "Sb",
            "Ag",
            "SnAlpha",
            "CaTiO3",
            "SrTiO3",
            "BaTiO3",
            "FeO",
            "CoO",
            "Fe3O4",
            "Co3O4",
            "FeRh",
            "Ir20Mn80",
            "CoFe",
            "CoGa",
            "CuMnAs",
            "Mn3Ge_cub",
            "Mn3Ge",
            "Pt3Cr",
            "TiN",
        ]

        user_samples = self.io.read()["user_samples"]
        for sample in user_samples.keys():
            items.append(sample)
        items.sort()
        # adding list of items to combo box
        self.combo_box.addItems(items)
        self.combo_box.move(QtGui.QCursor.pos())
        self.combo_box.currentTextChanged.connect(self.current_rmap_samples_manager)
        self.combo_box.showPopup()

    def clear_plot_samples(self):
        self.current_rmap_samples = []
        self.rmap_widget(
            self.worker.data_to_update["dargs"],
            samples=self.current_rmap_samples,
            idir=self.idir,
            ndir=self.ndir,
        )

    def current_rmap_samples_manager(self, choice):
        if choice in self.current_rmap_samples:
            self.current_rmap_samples.remove(choice)
        else:
            self.current_rmap_samples.append(choice)
        self.rmap_widget(
            self.worker.data_to_update["dargs"],
            samples=self.current_rmap_samples,
            idir=self.idir,
            ndir=self.ndir,
        )

    def extract(self, q_list_widget):
        lst = q_list_widget
        items = []
        for x in range(lst.count()):
            items.append(lst.item(x).text())
        return items

    def setup_scroll_area(self):

        setups = os.listdir(dp.HOME + "/.daf")
        setups = [i for i in setups if not i.endswith(".py")]
        setups.sort()

        # itemsTextList =  [str(self.ui.listWidget_setup.item(i).text()) for i in range(self.ui.listWidget_setup.count())]

        self.ui.listWidget_setup.clear()

        self.ui.listWidget_setup.addItems(setups)

    def on_list_widget_change(self):

        setups = os.listdir(dp.HOME + "/.daf")
        setups = [i for i in setups if not i.endswith(".py")]

        item = self.ui.listWidget_setup.currentItem()
        value = item.text()

        if value in setups:
            dict_ = self.io.read(dp.HOME + "/.daf/" + value)
            # self.ui.textEdit_setup.setText(bytes(dict_['setup_desc'], "uft-8").decode("unicode_escape"))
            self.ui.textEdit_setup.setText(dict_["setup_desc"])

    def change_setup(self):

        item = self.ui.listWidget_setup.currentItem()
        value = item.text()

        os.system("daf.setup -c {}".format(value))
        self.update_main_screen_title()

    def update_setup_description(self):

        item = self.ui.listWidget_setup.currentItem()
        value = item.text()
        mytext = self.textEdit_setup.toPlainText()
        # raw_s = repr(mytext)

        os.system('daf.setup -d {} "{}"'.format(value, mytext))

    def new_setup_dialog(self):
        setups = os.listdir(dp.HOME + "/.daf")
        setups = [i for i in setups if not i.endswith(".py")]

        text, result = QtWidgets.QInputDialog.getText(
            self, "Input Dialog", "New setup name"
        )

        if result:
            if text in setups:
                msgbox = QtWidgets.QMessageBox()
                msgbox_text = (
                    "Setup {} already exists, \ndo you want to overwrite it?".format(
                        text
                    )
                )
                ret = msgbox.question(
                    self,
                    "Warning",
                    msgbox_text,
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                    QtWidgets.QMessageBox.Cancel,
                )

                if ret == QtWidgets.QMessageBox.Ok:
                    os.system("daf.setup -n {}".format(text))

            else:
                os.system("daf.setup -n {}".format(text))

        self.setup_scroll_area()

    def save_setup(self):

        os.system("daf.setup -s")

    def copy_setup(self):

        setups = os.listdir(dp.HOME + "/.daf")
        setups = [i for i in setups if not i.endswith(".py")]

        text, result = QtWidgets.QInputDialog.getText(
            self, "Input Dialog", "Copy setup name"
        )

        if result:
            if text in setups:
                msgbox = QtWidgets.QMessageBox()
                msgbox_text = (
                    "Setup {} already exists, \ndo you want to overwrite it?".format(
                        text
                    )
                )
                ret = msgbox.question(
                    self,
                    "Warning",
                    msgbox_text,
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                    QtWidgets.QMessageBox.Cancel,
                )

                if ret == QtWidgets.QMessageBox.Ok:
                    os.system("daf.setup -s {}".format(text))

            else:
                os.system("daf.setup -s {}".format(text))

        self.setup_scroll_area()

    def remove_setup(self):
        item = self.ui.listWidget_setup.currentItem()
        value = item.text()
        os.system("daf.setup -r {}".format(value))
        self.setup_scroll_area()

    def set_scan_prop(self):
        """Set properties showed in scan tab in daf.gui"""
        dict_ = self.io.read()
        self.main_counter = dict_["main_scan_counter"]
        self.ui.label_current_config.setText(dict_["default_counters"].split(".")[1])
        self.set_scan_path()
        self.counters_scroll_area()
        self.main_counter_cbox(dict_["default_counters"], dict_["main_scan_counter"])
        self.set_counter_combobox_options()

    def set_scan_path(self):
        self.lineEdit_scan_path.setText(os.getcwd())
        self.lineEdit_scan_file.setText("scan_daf")

    def main_counter_cbox(self, defaut_file, main_counter):
        self.comboBox_main_counter.clear()
        user_configs = os.listdir(dp.HOME + "/.config/scan-utils")
        sys_configs = os.listdir("/etc/xdg/scan-utils")
        if defaut_file in user_configs:
            path_to_use = dp.HOME + "/.config/scan-utils/"
        elif defaut_file in sys_configs:
            path_to_use = "/etc/xdg/scan-utils/"
        with open(path_to_use + defaut_file) as file:
            data = yaml.safe_load(file)
            #         if isinstance(counter, dict):
            # counter = list(counter.keys())[0]
        data = [list(i.keys())[0] if type(i) == dict else i for i in data]
        if main_counter in data:
            data.remove(main_counter)
        if main_counter not in data and main_counter != None:
            data.insert(0, main_counter)
        elif main_counter == None:
            data.insert(0, "None")
        self.comboBox_main_counter.addItems(data)
        self.main_counter_cbox_default(main_counter)

    def main_counter_cbox_default(self, main_counter):
        AllItems = [
            self.comboBox_main_counter.itemText(i)
            for i in range(self.comboBox_main_counter.count())
        ]
        if main_counter in AllItems:
            self.comboBox_main_counter.setCurrentIndex(AllItems.index(main_counter))
        elif main_counter == None:
            self.comboBox_main_counter.setCurrentIndex(AllItems.index("None"))

    def change_main_counter(self):
        dict_ = self.io.read()
        AllItems = [
            self.comboBox_main_counter.itemText(i)
            for i in range(self.comboBox_main_counter.count())
        ]
        counter = self.comboBox_main_counter.currentText()
        if counter != "" and counter != "None":
            if counter != self.main_counter:
                self.main_counter = counter
                os.system("daf.mc -m {}".format(counter))
                if "None" in AllItems and dict_["main_scan_counter"] != None:
                    AllItems.remove("None")
                    self.comboBox_main_counter.clear()
                    self.comboBox_main_counter.addItems(AllItems)

    def fill_item(self, item, value):
        item.setExpanded(False)
        if type(value) is dict:
            for key, val in sorted(value.items()):
                child = QTreeWidgetItem()
                child.setText(0, str(key))
                item.addChild(child)
                self.fill_item(child, val)
        elif type(value) is list:
            for val in value:
                child = QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:
                    child.setText(0, "[dict]")
                    self.fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, "[list]")
                    self.fill_item(child, val)
                else:
                    child.setText(0, str(val))
                    child.setExpanded(True)
        else:
            child = QTreeWidgetItem()
            child.setText(0, str(value))
            item.addChild(child)

    def fill_widget(self, widget, value):
        widget.clear()
        self.fill_item(widget.invisibleRootItem(), value)

    def print_tree(self, file):
        """Print counters of a setup as a tree"""
        with open("/etc/xdg/scan-utils/config.yml") as conf:
            config_data = yaml.safe_load(conf)
        with open(file) as file:
            data = yaml.safe_load(file)
        if data != None:
            full_output = {}
            for counter in data:
                if isinstance(counter, dict):
                    counter = list(counter.keys())[0]
                full_output[counter] = config_data["counters"][counter]
        else:
            full_output = "Add counters to this file"
        self.fill_widget(self.ui.treeWidget_counters, full_output)

    def counters_scroll_area(self):
        dict_ = self.io.read()
        """List all possible counter configs"""
        user_configs = os.listdir(dp.HOME + "/.config/scan-utils")
        sys_configs = os.listdir("/etc/xdg/scan-utils")
        all_configs = user_configs + sys_configs
        configs = [
            i.split(".")[1]
            for i in all_configs
            if len(i.split(".")) == 3 and i.endswith(".yml")
        ]
        configs.sort()
        self.ui.listWidget_counters.clear()
        self.ui.listWidget_counters.addItems(configs)
        # simp_counter_file = dict_['default_counters'].split('.')[1]
        # for i in range (self.ui.listWidget_counters.count()):
        #     item = self.ui.listWidget_counters.item(i)
        #     text = item.text()
        #     if simp_counter_file == text:
        #         self.ui.listWidget_counters.setCurrentItem(item)

    def on_counters_list_widget_change(self):
        """Print the counters on a setup when selected"""
        prefix = "config."
        sufix = ".yml"
        user_configs = os.listdir(dp.HOME + "/.config/scan-utils")
        sys_configs = os.listdir("/etc/xdg/scan-utils")
        all_configs = user_configs + sys_configs
        configs = [
            i.split(".")[1]
            for i in all_configs
            if len(i.split(".")) == 3 and i.endswith(".yml")
        ]
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        if value in configs:
            try:
                self.print_tree("/etc/xdg/scan-utils/" + prefix + value + sufix)
            except:
                self.print_tree(
                    dp.HOME + "/.config/scan-utils/" + prefix + value + sufix
                )

    def set_counter(self):
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        os.system("daf.mc -s {}".format(value))
        dict_ = self.io.read()
        self.ui.label_current_config.setText(dict_["default_counters"].split(".")[1])
        self.main_counter_cbox(dict_["default_counters"], dict_["main_scan_counter"])
        self.main_counter_cbox_default(dict_["main_scan_counter"])

    def new_counter_file(self):
        configs = os.listdir(dp.HOME + "/.config/scan-utils")
        configs = [
            i.split(".")[1]
            for i in configs
            if len(i.split(".")) == 3 and i.endswith(".yml")
        ]
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
                    os.system("daf.mc -n {}".format(text))

            else:
                os.system("daf.mc -n {}".format(text))
        self.counters_scroll_area()

    def add_counter(self):
        """Add a counter to a setup"""
        dict_ = self.io.read()
        counter = self.ui.comboBox_counters.currentText()
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        os.system("daf.mc -a {} {}".format(value, counter))
        list_ = self.extract(self.ui.listWidget_counters)
        if list_.index(value) == 0 and len(list_) > 1:
            self.ui.listWidget_counters.setCurrentRow(1)
        else:
            self.ui.listWidget_counters.setCurrentRow(0)
        self.ui.listWidget_counters.setCurrentRow(list_.index(value))
        self.main_counter_cbox(dict_["default_counters"], dict_["main_scan_counter"])

    def remove_counter_file(self):
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        os.system("daf.mc -r {}".format(value))
        self.counters_scroll_area()

    def set_counter_combobox_options(self):
        with open("/etc/xdg/scan-utils/config.yml") as conf:
            config_data = yaml.safe_load(conf)
        counters = config_data["counters"].keys()
        self.ui.comboBox_counters.addItems(counters)
        self.ui.comboBox_counters.setEditable(True)
        self.ui.comboBox_counters.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

    def remove_counter(self):
        dict_ = self.io.read()
        getSelected = self.ui.treeWidget_counters.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            counter = baseNode.text(0)
            item = self.ui.listWidget_counters.currentItem()
            value = item.text()
            os.system("daf.mc -rc {} {}".format(value, counter))
            list_ = self.extract(self.ui.listWidget_counters)
            if list_.index(value) == 0 and len(list_) > 1:
                self.ui.listWidget_counters.setCurrentRow(1)
            else:
                self.ui.listWidget_counters.setCurrentRow(0)
            self.ui.listWidget_counters.setCurrentRow(list_.index(value))
        self.main_counter_cbox(dict_["default_counters"], dict_["main_scan_counter"])

    def update(self):
        self.refresh_pydm_motors()

        lb = lambda x: "{:.5f}".format(float(x))  # format float with 5 decimals

        # Update HKL pos labels
        self.ui.H_val.setText(str(lb(self.worker.data_to_update["hklnow"][0])))
        self.ui.K_val.setText(str(lb(self.worker.data_to_update["hklnow"][1])))
        self.ui.L_val.setText(str(lb(self.worker.data_to_update["hklnow"][2])))

        # Update pseudo-angle pos labels
        self.ui.label_alpha.setText(
            str(lb(self.worker.data_to_update["pseudo_dict"]["alpha"]))
        )
        self.ui.label_beta.setText(
            str(lb(self.worker.data_to_update["pseudo_dict"]["beta"]))
        )
        self.ui.label_psi.setText(
            str(lb(self.worker.data_to_update["pseudo_dict"]["psi"]))
        )
        self.ui.label_tau.setText(
            str(lb(self.worker.data_to_update["pseudo_dict"]["tau"]))
        )
        self.ui.label_qaz.setText(
            str(lb(self.worker.data_to_update["pseudo_dict"]["qaz"]))
        )
        self.ui.label_naz.setText(
            str(lb(self.worker.data_to_update["pseudo_dict"]["naz"]))
        )
        self.ui.label_omega.setText(
            str(lb(self.worker.data_to_update["pseudo_dict"]["omega"]))
        )

        # Update status mode label
        mode_text = (
            "MODE: "
            + str(self.worker.data_to_update["mode_num"][0])
            + str(self.worker.data_to_update["mode_num"][1])
            + str(self.worker.data_to_update["mode_num"][2])
            + str(self.worker.data_to_update["mode_num"][3])
            + str(self.worker.data_to_update["mode_num"][4])
        )
        self.ui.label_mode.setText(mode_text)
        self.ui.label_mode1.setText(self.worker.data_to_update["mode"][0])
        self.ui.label_mode2.setText(self.worker.data_to_update["mode"][1])
        self.ui.label_mode3.setText(self.worker.data_to_update["mode"][2])
        self.ui.label_mode4.setText(self.worker.data_to_update["mode"][3])
        self.ui.label_mode5.setText(self.worker.data_to_update["mode"][4])

        # Update status constraints label
        self.ui.label_cons1.setText(str(self.worker.data_to_update["cons"][0][1]))
        self.ui.label_cons2.setText(str(self.worker.data_to_update["cons"][1][1]))
        self.ui.label_cons3.setText(str(self.worker.data_to_update["cons"][2][1]))
        self.ui.label_cons4.setText(str(self.worker.data_to_update["cons"][3][1]))
        self.ui.label_cons5.setText(str(self.worker.data_to_update["cons"][4][1]))

        # Update status experiment label
        # self.ui.label_exp1.setText(str(self.worker.data_to_update['exp_list'][0]))
        self.ui.label_exp2.setText(str(self.worker.data_to_update["exp_list"][1]))
        self.ui.label_exp3.setText(str(self.worker.data_to_update["exp_list"][2]))
        self.ui.label_exp4.setText(str(self.worker.data_to_update["exp_list"][3]))
        self.ui.label_exp5.setText(str(self.worker.data_to_update["exp_list"][4]))
        self.ui.label_exp6.setText(str(self.worker.data_to_update["exp_list"][5]))

        # Update sample info label
        self.ui.label_samp_name.setText(str(self.worker.data_to_update["samp_info"][0]))
        self.ui.label_samp_a.setText(
            lb(str(self.worker.data_to_update["samp_info"][1]))
        )
        self.ui.label_samp_b.setText(
            lb(str(self.worker.data_to_update["samp_info"][2]))
        )
        self.ui.label_samp_c.setText(
            lb(str(self.worker.data_to_update["samp_info"][3]))
        )
        self.ui.label_samp_alpha.setText(
            lb(str(self.worker.data_to_update["samp_info"][4]))
        )
        self.ui.label_samp_beta.setText(
            lb(str(self.worker.data_to_update["samp_info"][5]))
        )
        self.ui.label_samp_gamma.setText(
            lb(str(self.worker.data_to_update["samp_info"][6]))
        )

        # Update status Matrixes
        # U
        header_U = self.tableWidget_U.horizontalHeader()
        for row in range(self.tableWidget_U.rowCount()):
            for column in range(self.tableWidget_U.columnCount()):
                item = QTableWidgetItem(
                    str(self.worker.data_to_update["U"][row][column])
                )
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget_U.setItem(row, column, item)
            header_U.setResizeMode(row, QHeaderView.Stretch)

        # UB
        header_UB = self.tableWidget_UB.horizontalHeader()
        for row in range(self.tableWidget_UB.rowCount()):
            for column in range(self.tableWidget_UB.columnCount()):
                item = QTableWidgetItem(
                    str(self.worker.data_to_update["UB"][row][column])
                )
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget_UB.setItem(row, column, item)
            header_UB.setResizeMode(row, QHeaderView.Stretch)

        # Update motor bounds
        self.ui.label_mu_bounds_ll.setText(
            str(self.worker.data_to_update["bounds"]["mu"][0])
        )
        self.ui.label_mu_bounds_hl.setText(
            str(self.worker.data_to_update["bounds"]["mu"][1])
        )

        self.ui.label_eta_bounds_ll.setText(
            str(self.worker.data_to_update["bounds"]["eta"][0])
        )
        self.ui.label_eta_bounds_hl.setText(
            str(self.worker.data_to_update["bounds"]["eta"][1])
        )

        self.ui.label_chi_bounds_ll.setText(
            str(self.worker.data_to_update["bounds"]["chi"][0])
        )
        self.ui.label_chi_bounds_hl.setText(
            str(self.worker.data_to_update["bounds"]["chi"][1])
        )

        self.ui.label_phi_bounds_ll.setText(
            str(self.worker.data_to_update["bounds"]["phi"][0])
        )
        self.ui.label_phi_bounds_hl.setText(
            str(self.worker.data_to_update["bounds"]["phi"][1])
        )

        self.ui.label_nu_bounds_ll.setText(
            str(self.worker.data_to_update["bounds"]["nu"][0])
        )
        self.ui.label_nu_bounds_hl.setText(
            str(self.worker.data_to_update["bounds"]["nu"][1])
        )

        self.ui.label_del_bounds_ll.setText(
            str(self.worker.data_to_update["bounds"]["del"][0])
        )
        self.ui.label_del_bounds_hl.setText(
            str(self.worker.data_to_update["bounds"]["del"][1])
        )

        self.delay_counter += 1
