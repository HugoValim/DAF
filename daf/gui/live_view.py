#!/usr/bin/env python3

import threading
import time
from os import path

import silx
from silx.gui.utils import concurrent
from silx.gui.plot import Plot1D
from PyQt5.QtCore import QTimer
from pydm import Display
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QMenu,
    QApplication,
    QAction,
)
import qdarkstyle

import daf.utils.dafutilities as du
import daf.utils.fits_daf as fits


class UpdateThread(threading.Thread):
    """Thread updating the curve of a :class:`~silx.gui.plot.Plot1D`

    :param plot1d: The Plot1D to update."""

    def __init__(self, plots, file, xlabel):
        self.plots = plots
        self.file = file
        self.xlabel = xlabel
        self.running = False
        super(UpdateThread, self).__init__()

    def start(self):
        """Start the update thread"""
        self.running = True
        super(UpdateThread, self).start()

    def get_hdf5_data(self, file):
        """Read Scan data and store into dicts, also creates a dict with simplified data names"""
        counters_data = {}
        motors_data = {}
        for data in [file]:
            with silx.io.open(file) as h5w:
                scan_idx = list(h5w["Scan"].keys())
                scan_idx = scan_idx[-1]
                _dataset_name = "Scan/" + scan_idx + "/instrument/"
                instrument = h5w[_dataset_name]
                for i in instrument:
                    # If the data is called 'data' them its a motor, otherwise its a counter
                    if "data" in instrument[i]:
                        attrs = [j for j in instrument[i].attrs]
                        if "shape" in attrs:
                            if len(instrument[i].attrs["shape"].split(",")) >= 2:
                                continue
                        try:
                            motors_data[i] = instrument[i]["data"][:]
                        except:
                            pass
                    else:
                        counters_data[i] = instrument[i][i][:]

        return motors_data, counters_data

    def run(self):
        """Method implementing thread loop that updates the plot"""
        ntrys = 0
        while self.running:
            try:
                x, y = self.get_hdf5_data(self.file)
                for plot in self.plots.keys():
                    counter = y[plot]
                    if self.xlabel == "points":
                        motor = [i for i in range(len(counter))]
                    else:
                        motor = x[self.xlabel]
                    # Run plot update asynchronously
                    concurrent.submitToQtMainThread(
                        self.plots[plot].addCurve, motor[: len(counter)], counter
                    )
                time.sleep(0.25)
            except:
                ntrys += 1
                if ntrys > 10:
                    break
                time.sleep(0.25)

    def stop(self):
        """Stop the update thread"""
        self.running = False
        self.join(2)


class MyDisplay(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.io = du.DAFIO()
        self.started = False
        self.xlabel = None
        self.fwhm_pos = None
        self.peak_pos = None
        self.app = QApplication.instance()
        self._createMenuBar()
        self.default_theme()
        self.build_basic_layout()
        self.loop()

    def ui_filename(self):
        return "ui/live_view.ui"

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def translate_dict(self):
        """Depending on the motors translate to daf .Experiment format"""
        if du.PV_PREFIX == "EMA:B:PB18":
            data = {
                "huber_mu": "Mu",
                "huber_eta": "Eta",
                "huber_chi": "Chi",
                "huber_phi": "Phi",
                "huber_nu": "Nu",
                "huber_del": "Del",
            }
            return data
        else:
            data = {
                "sol_m3": "Mu",
                "sol_m5": "Eta",
                "sol_m2": "Chi",
                "sol_m1": "Phi",
                "sol_m4": "Nu",
                "sol_m6": "Del",
            }
            return data

    def _createMenuBar(self):
        """Create the menu bar and shortcuts"""
        menu_bar = self.app.main_window.menuBar()
        menu_bar.clear()
        # Creating menus using a QMenu object
        self.option_menu = QMenu("&Options", self)

        menu_bar.addMenu(self.option_menu)
        act = QAction("Dark Theme", self.option_menu, checkable=True)
        style_action = self.option_menu.addAction(act)
        for action in self.option_menu.actions():
            if action.text() == "Dark Theme":
                action.setChecked(True)
        self.option_menu.triggered.connect(self.style_sheet_handler)

    def default_theme(self):
        dict_args = self.io.read()
        if dict_args["dark_mode"]:
            style = qdarkstyle.load_stylesheet_pyqt5()
            self.app.setStyleSheet(style)
            for action in self.option_menu.actions():
                if action.text() == "Dark Theme":
                    action.setChecked(True)
        else:
            self.app.setStyleSheet("")
            for action in self.option_menu.actions():
                if action.text() == "Dark Theme":
                    action.setChecked(False)

    def style_sheet_handler(self):
        dict_args = self.io.read()
        for action in self.option_menu.actions():
            if action.text() == "Dark Theme":
                if action.isChecked():
                    style = qdarkstyle.load_stylesheet_pyqt5()
                    self.app.setStyleSheet(style)
                    dict_args["dark_mode"] = 1
                    du.write(dict_args)
                else:
                    self.app.setStyleSheet("")
                    dict_args["dark_mode"] = 0
                    du.write(dict_args)

    def loop(self):
        """Loop every 1 second to see if a new scan has began"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # trigger every 1 seconds.

    def build_basic_layout(self):
        """Build the first layout just for the GUI not be empty when started"""
        plot = Plot1D()
        plot.show()
        self.tabWidget.setTabText(0, "Waiting")
        self.verticalLayout_single.addWidget(plot)
        self.build_stat_table()

    def clean_plots(self):
        """Clean the layout before building another, avoiding stacks"""
        for i in reversed(range(self.verticalLayout_single.count())):
            self.verticalLayout_single.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.gridLayout_all.count())):
            self.gridLayout_all.itemAt(i).widget().setParent(None)

    def build_stat_table(self):
        """Build the statistic table"""
        self.table_push_buttons = {}
        self.tableWidget_stats = QTableWidget()
        self.tableWidget_stats.setMaximumHeight(130)
        self.tableWidget_stats.verticalHeader().setVisible(False)
        self.tableWidget_stats.horizontalHeader().hide()
        self.push_button_fwhm = QPushButton("Go to FWHM pos")
        self.push_button_fwhm.clicked.connect(self.goto_fwhm)
        self.push_button_peak = QPushButton("Go to peak pos")
        self.push_button_peak.clicked.connect(self.goto_peak)
        header = self.tableWidget_stats.horizontalHeader()
        for i in range(4):
            self.tableWidget_stats.insertRow(i)
        for i in range(5):
            self.tableWidget_stats.insertColumn(i)
            header.setResizeMode(i, QHeaderView.Stretch)

        self.tableWidget_stats.setItem(0, 0, QTableWidgetItem("FWHM:"))
        self.tableWidget_stats.setItem(0, 2, QTableWidgetItem("FWHM pos:"))
        self.tableWidget_stats.setCellWidget(0, 4, self.push_button_fwhm)
        self.tableWidget_stats.setItem(1, 0, QTableWidgetItem("Peak:"))
        self.tableWidget_stats.setItem(1, 2, QTableWidgetItem("Peak pos:"))
        self.tableWidget_stats.setCellWidget(1, 4, self.push_button_peak)
        self.tableWidget_stats.setItem(1, 4, QTableWidgetItem("FWHM pos:"))
        self.tableWidget_stats.setItem(2, 0, QTableWidgetItem("Min:"))
        self.tableWidget_stats.setItem(2, 2, QTableWidgetItem("Min pos:"))
        self.tableWidget_stats.setItem(3, 0, QTableWidgetItem("COM"))
        self.verticalLayout_single.addWidget(self.tableWidget_stats)

    def build_stat(self, plot):
        """Update statistic table after the scan is done"""
        try:
            fmt = lambda x: str("{:.5f}".format(float(x)))
            curve = plot.getCurve()
            x0 = curve.getXData()
            y0 = curve.getYData()
            self.stats = fits.fitGauss(x0, y0)
            self.peak = self.stats[0]
            self.peak_pos = self.stats[1]
            self.min = self.stats[2]
            self.min_pos = self.stats[3]
            self.fwhm = self.stats[4]
            self.fwhm_pos = self.stats[5]
            self.com = self.stats[6]
            # # Update table
            self.tableWidget_stats.setItem(0, 1, QTableWidgetItem(fmt(self.fwhm)))
            self.tableWidget_stats.setItem(0, 3, QTableWidgetItem(fmt(self.fwhm_pos)))
            self.tableWidget_stats.setItem(1, 1, QTableWidgetItem(fmt(self.peak)))
            self.tableWidget_stats.setItem(1, 3, QTableWidgetItem(fmt(self.peak_pos)))
            self.tableWidget_stats.setItem(2, 1, QTableWidgetItem(fmt(self.min)))
            self.tableWidget_stats.setItem(2, 3, QTableWidgetItem(fmt(self.min_pos)))
            self.tableWidget_stats.setItem(3, 1, QTableWidgetItem(fmt(self.com)))
        except:
            pass

    def goto_fwhm(self):
        """Move the xlabel motor to the FWHM pos"""
        if self.xlabel is not None and self.fwhm_pos is not None:
            dict_ = self.translate_dict()
            dict_args = self.io.read()
            dict_args[dict_[self.xlabel]] = float(self.fwhm_pos)
            du.write(dict_args)

    def goto_peak(self):
        """Move the xlabel motor to the peak pos"""
        if self.xlabel is not None and self.peak_pos is not None:
            dict_ = self.translate_dict()
            dict_args = self.io.read()
            dict_args[dict_[self.xlabel]] = float(self.peak_pos)
            du.write(dict_args)

    def update_plot(self):
        """
        Function to generate the plots.
        The plots are fed from another thread, it only need to be instantiated once
        per scan.
        The GUI checks every 1 second to see if a new scan has started
        """
        dict_args = self.io.read()
        if dict_args["scan_running"] and not self.started:
            self.plot_dict = {}
            self.xlabel = dict_args["main_scan_motor"]
            self.clean_plots()
            self.started = True
            n_counters = len(dict_args["scan_counters"])
            n_lines = (n_counters - 1) // 2 + 1
            n_columns = 2  # Number of columns in the grid layout
            j = 0  # Row to add the plot widget in the grid layout
            k = 0  # Colum to add the plot widget in the grid layout
            for counter in dict_args["scan_counters"]:
                if counter == "pilatus_300k":
                    continue  # Detector handlers should be avoided
                self.plot_dict[counter] = Plot1D()
                self.plot_dict[counter].show()
                self.plot_dict[counter].setGraphTitle(
                    dict_args["current_scan_file"].split("/")[-1]
                )
                self.plot_dict[counter].getXAxis().setLabel(self.xlabel)
                self.plot_dict[counter].setDefaultPlotPoints(True)
                self.plot_dict[counter].getYAxis().setLabel(counter)
                if dict_args["main_scan_counter"] == counter:
                    self.tabWidget.setTabText(0, counter)
                    self.verticalLayout_single.addWidget(self.plot_dict[counter])
                    self.plot_dict[counter].setGraphCursor(flag=True)
                    self.build_stat_table()
                else:
                    self.gridLayout_all.addWidget(self.plot_dict[counter], j, k)
                    k += 1
                    if k == n_columns:
                        k = 0
                        j += 1

            self.updateThread = UpdateThread(
                self.plot_dict, dict_args["current_scan_file"], self.xlabel
            )
            self.updateThread.start()  # Start updating the plot
        elif dict_args["scan_running"] and self.started:
            pass
        else:
            if self.started:
                if dict_args["main_scan_counter"] != "":
                    if dict_args["main_scan_counter"] in self.plot_dict.keys():
                        self.build_stat(self.plot_dict[dict_args["main_scan_counter"]])
                self.started = False
                self.updateThread.stop()
