#!/usr/bin/env python3

import sys
import os
import subprocess
from datetime import datetime
import time
import signal

import pandas as pd
import yaml
import argparse as ap
import h5py
from PyQt5.QtWidgets import QApplication, QDesktopWidget

import numpy
import numpy as np

# Py4Syn imports
import py4syn
from py4syn.utils import scan as scanModule
from py4syn.utils.scan import (
    setFileWriter,
    getFileWriter,
    getOutput,
    createUniqueFileName,
)

# scan-utils imports
from scan_utils.hdf5_writer import HDF5Writer
from scan_utils.scan import ScanOperationCLI

from daf.utils import dafutilities as du


class DAFTimeScan(ScanOperationCLI):
    def __init__(self, args, close_window=False, delay=False, n_points_count=1000):
        self.close_window = close_window
        super().__init__(**args)
        self.delay = delay
        self.n_points_count = n_points_count
        self.io = du.DAFIO()

    def configure_step_mode(self):
        """
        Get step-or-points definition in config.yml, however step-or-points
        can be redefined by the command line argument --points-mode or
        --step-mode
        """
        step_mode = self.configuration["misc"].get("step-or-points") == "step"

        if self.step_mode:
            step_mode = True
        elif self.points_mode:
            step_mode = False
        elif self.is_time_scan:
            step_mode = False

        return step_mode

    def setup(self):
        """Setup scan (param list, plot etc.)"""
        # if not self.is_time_scan:
        #     self.create_devices()
        # else:
        self.configuration.create_runtime_counters()

        self.setup_py4syn_parameters()

        # Call all scan configuration methods
        # if not self.is_time_scan:
        #     self.configure_points_time()
        #     self.configure_scan_args()

        self.configure_file_writer()

        self.configure_plot()

        # print('\nEstimated time: ' + str(self.get_estimated_time(self.times)) + '\n')
        # self.start_time = time()

    def configure_file_writer(self):
        # Change to HDF5 file writer
        self.unique_filename = ".daf_time_scan.hdf"
        if self.writer_type.value == "HDF5":
            sol_writer = HDF5Writer(self.unique_filename, "Scan", self.configuration)
            setFileWriter(sol_writer)

        self.writer = getFileWriter()
        self.storage_path = self.configuration["misc"]["storage-path"]

    def pre_scan_callback(self, **kwargs):
        import py4syn
        import os

        dictionary = {
            "motor": ["None"],
            "config": self.counters_name,
            "start": self.start,
            "end": self.end,
            "step_or_points": self.step_or_points,
            "time": self.time,
            "optimum": self.optimum,
            "sync": self.sync,
            "output": self.output,
            "message": self.message,
            "repeat": self.repeat,
            "repetition": self.repetition,
            "sleep": self.sleep,
            "snake": self.snake,
            "xlabel": self.xlabel,
            "step_mode": self.step_mode,
            "points_mode": self.points_mode,
            "points": [numpy.zeros(int(self.n_points_count), dtype=numpy.int8)],
            "file_points": True,
        }

        for k, v in py4syn.counterDB.items():
            if v["autowrite"]:
                counter_label = self.writer.getCounterLabel(k)
                filepath, filename = os.path.split(self.unique_filename)
                v["device"].setFileName(filename + "_" + counter_label)
                v["device"].setFilePath(filepath)
                v["device"].setOutputFormat("%s%s_%03d.hdf5")
                v["device"].setParams(dictionary)
                v["device"].setWriteParams()
                v["device"].startCapture()

        if self.writer_type.value == "HDF5":
            self.writer.setScanAtributtes(dictionary)
            self.writer.setAtributes()
            import h5py

            for _, counter in py4syn.counterDB.items():
                if counter["autowrite"] and counter["write"]:
                    filename = (
                        counter["device"].getFileName()
                        + "_"
                        + format(counter["device"].getRepeatNumber(), "03")
                    )
                    filepath = counter["device"].getFilePath()
                    device_name = counter["device"].getMnemonic()

                    hdf5_link = h5py.ExternalLink(
                        filepath + filename + ".hdf5", "entry/data/data"
                    )

                    self.writer.insertDeviceData(device_name, hdf5_link)
            self.writer.set_swmr()

    def on_operation_begin(self):
        """Routine to be done before this scan operation."""
        counter_dict = dict(py4syn.counterDB.items())
        # print(counter_dict)
        counter_list = [i for i in counter_dict.keys()]
        dict_args = self.io.read()
        dict_args["scan_running"] = True
        dict_args["scan_counters"] = counter_list
        dict_args["current_scan_file"] = self.unique_filename
        dict_args["main_scan_motor"] = self.xlabel
        self.io.write(dict_args)

    def pos_scan_callback(self, **kwargs):

        print("pos_scan_callback")

        import py4syn
        import h5py

        self.n_trys = 0

        def open_fileH5(detector_file):
            try:
                while self.n_trys < 10:
                    return h5py.File(detector_file, "r")
            except:
                time.sleep(0.5)
                self.n_trys += 1
                return open_fileH5(detector_file)

        for counter_name, counter in py4syn.counterDB.items():
            # Remove dataset aux to 2d scan.
            with h5py.File(self.unique_filename, "a") as h5w:
                scan_idx = list(h5w["Scan"].keys())
                scan_idx = scan_idx[-1]
                _dataset_name = (
                    "Scan/"
                    + scan_idx
                    + "/instrument/"
                    + counter_name
                    + "/"
                    + counter_name
                )
                _dataset_name_aux = _dataset_name + "_aux"
                try:
                    if len(h5w[_dataset_name_aux].shape) == 1:
                        del h5w[_dataset_name_aux]
                    else:
                        del h5w[_dataset_name]
                        h5w[_dataset_name] = h5w[_dataset_name_aux]
                        del h5w[_dataset_name_aux]
                except:
                    pass

                h5w.flush()

            if counter["autowrite"] and counter["write"]:
                filename = (
                    counter["device"].getFileName()
                    + "_"
                    + format(counter["device"].getRepeatNumber(), "03")
                )
                filepath = counter["device"].getFilePath()

                detector_file = filepath + filename + ".hdf5"

                print("Time before open: ", datetime.now())
                print(detector_file)
                h5r = open_fileH5(detector_file)
                print("Time after open: ", datetime.now())

                if h5r is None:
                    print("PROBLEM")
                    continue

                with h5py.File(self.unique_filename, "a") as h5w:
                    for group in h5r.keys():
                        for ds in h5r[group].keys():
                            if "link" in counter.keys():
                                if counter["link"] == "Copy":
                                    ds_arr = h5r[group][ds]["data"]
                                    scan_idx = list(h5w["Scan"].keys())
                                    scan_idx = scan_idx[-1]
                                    _dataset_data = (
                                        "Scan/"
                                        + scan_idx
                                        + "/instrument/"
                                        + counter_name
                                        + "/data"
                                    )

                                    del h5w[_dataset_data]
                                    print("Time before Compression: ", datetime.now())
                                    h5w.create_dataset(
                                        _dataset_data,
                                        data=ds_arr,
                                        shape=ds_arr.shape,
                                        compression="gzip",
                                        compression_opts=2,
                                    )
                                    print("Time after Compression: ", datetime.now())
                print("done")

    def on_operation_end(self):
        """Routine to be done after this scan operation."""
        if self.plot_type == PlotType.pyqtgraph:
            self.pyqtgraph_plot.operation_ends()
        if self.plot_type == PlotType.hdf:
            self.hdf_plot.operation_ends()
        if bool(self.reset):
            print("[scan-utils] Reseting devices positions.")
            self.reset_motors()
        # Close scan window
        if self.close_window:
            self.app.quit()
        # self.scan_status = False
        # display_monitor = 0
        # monitor = QDesktopWidget().screenGeometry(display_monitor)
        # print(monitor)
        # self.pyqtgraph_plot.move(monitor.left(), monitor.top())
        # self.pyqtgraph_plot.showFullScreen()

    def _run(self):
        self.on_operation_begin()

        for i in range(self.repeat):
            self.repetition = i
            self.on_scan_begin()

            if self.plotter is not None:
                next(self.axes)

            # scanModule.scan(*self.scan_args)
            scanModule.timescan(t=self.time[0][0], delay=self.delay)

            self.on_scan_end()

            # except KeyboardInterrupt:
            #     print('oioi')
            # self.fit_values()

        # if self.optimum:
        #     self.goto_optimum()

        cleanup()
        self.on_operation_end()
        if self.plotter is not None and self.wait_plotter:
            self.plotter.plot_process.join()
        # if self.postscan_cmd is not None:
        #     try:
        #         subprocess.run(self.postscan_cmd, shell=True)
        #     except (OSError, RuntimeError) as exception:
        #         die(exception)
