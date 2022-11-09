#!/usr/bin/env python3

import sys
import os
import subprocess
import signal

# import scan_daf as sd
import pandas as pd
import yaml
import argparse as ap
import h5py
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from datetime import datetime
import time

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
from scan_utils import cleanup, die
from scan_utils import Configuration, processUserField, get_counters_in_config
from scan_utils.scan_pyqtgraph_plot import PlotScan
from scan_utils.scan_hdf_plot import PlotHDFScan
from scan_utils import PlotType
from scan_utils import WriteType
from scan_utils import DefaultParser
from scan_utils.scan import ScanOperationCLI

from daf.utils import dafutilities as du
from daf.core.main import DAF


class DAFScan(ScanOperationCLI):
    def __init__(self, args, close_window=False):
        super().__init__(**args)
        self.close_window = close_window
        self.io = du.DAFIO()

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

    def write_hkl(self):
        """Method to write HKL coordinates for each point as motor in the final hdf5 file"""
        dict_args = self.io.read()
        mode = [int(i) for i in dict_args["Mode"]]
        U = np.array(dict_args["U_mat"])
        idir = dict_args["IDir_print"]
        ndir = dict_args["NDir_print"]
        rdir = dict_args["RDir"]
        mu_bound = dict_args["motors"]["mu"]["bounds"]
        eta_bound = dict_args["motors"]["eta"]["bounds"]
        chi_bound = dict_args["motors"]["chi"]["bounds"]
        phi_bound = dict_args["motors"]["phi"]["bounds"]
        nu_bound = dict_args["motors"]["nu"]["bounds"]
        del_bound = dict_args["motors"]["del"]["bounds"]
        self.en = (
            dict_args["beamline_pvs"]["energy"]["value"] - dict_args["energy_offset"]
        )

        exp = DAF(*mode)
        if dict_args["Material"] in dict_args["user_samples"].keys():
            exp.set_material(
                dict_args["Material"], *dict_args["user_samples"][dict_args["Material"]]
            )
        else:
            exp.set_material(
                dict_args["Material"],
                dict_args["lparam_a"],
                dict_args["lparam_b"],
                dict_args["lparam_c"],
                dict_args["lparam_alpha"],
                dict_args["lparam_beta"],
                dict_args["lparam_gama"],
            )

        exp.set_exp_conditions(
            idir=idir,
            ndir=ndir,
            rdir=rdir,
            en=self.en,
            sampleor=dict_args["Sampleor"],
        )
        exp.set_circle_constrain(
            Mu=mu_bound,
            Eta=eta_bound,
            Chi=chi_bound,
            Phi=phi_bound,
            Nu=nu_bound,
            Del=del_bound,
        )

        exp.set_constraints(
            Mu=dict_args["cons_mu"],
            Eta=dict_args["cons_eta"],
            Chi=dict_args["cons_chi"],
            Phi=dict_args["cons_phi"],
            Nu=dict_args["cons_nu"],
            Del=dict_args["cons_del"],
            alpha=dict_args["cons_alpha"],
            beta=dict_args["cons_beta"],
            psi=dict_args["cons_psi"],
            omega=dict_args["cons_omega"],
            qaz=dict_args["cons_qaz"],
            naz=dict_args["cons_naz"],
        )

        exp.set_U(U)
        exp.build_xrd_experiment()
        exp.build_bounds()
        mu = dict_args["motors"]["mu"]["value"]
        eta = dict_args["motors"]["eta"]["value"]
        chi = dict_args["motors"]["chi"]["value"]
        phi = dict_args["motors"]["phi"]["value"]
        nu = dict_args["motors"]["nu"]["value"]
        delta = dict_args["motors"]["del"]["value"]
        exp_points = {
            "mu": mu,
            "eta": eta,
            "chi": chi,
            "phi": phi,
            "nu": nu,
            "del": delta,
        }
        data = {
            dict_args["motors"]["mu"]["scan_utils_mnemonic"]: "mu",
            dict_args["motors"]["eta"]["scan_utils_mnemonic"]: "eta",
            dict_args["motors"]["chi"]["scan_utils_mnemonic"]: "chi",
            dict_args["motors"]["phi"]["scan_utils_mnemonic"]: "phi",
            dict_args["motors"]["nu"]["scan_utils_mnemonic"]: "nu",
            dict_args["motors"]["del"]["scan_utils_mnemonic"]: "del",
        }
        dict_ = {}
        for motor in self.motor:
            # Add statistic data as attributes
            with h5py.File(self.unique_filename, "a") as h5w:
                scan_idx = list(h5w["Scan"].keys())
                scan_idx = scan_idx[-1]
                _motors_name = "Scan/" + scan_idx + "/instrument/" + motor + "/data"
                if motor in data.keys():
                    dict_[data[motor]] = h5w[_motors_name][:]
                    npoints = len(h5w[_motors_name][:])
                    del data[motor]
        for motor in data.keys():
            dict_[data[motor]] = [exp_points[data[motor]] for i in range(npoints)]
        hkl_dict = {"H": [], "K": [], "L": []}
        for i in range(npoints):
            hklnow = exp.calc_from_angs(
                dict_["mu"][i],
                dict_["eta"][i],
                dict_["chi"][i],
                dict_["phi"][i],
                dict_["nu"][i],
                dict_["del"][i],
            )
            hkl_dict["H"].append(hklnow[0])
            hkl_dict["K"].append(hklnow[1])
            hkl_dict["L"].append(hklnow[2])
        with h5py.File(self.unique_filename, "a") as h5w:
            _motors_path = "Scan/" + scan_idx + "/instrument/"
            h5w[_motors_path].create_group("H")
            h5w[_motors_path].create_group("K")
            h5w[_motors_path].create_group("L")
            h5w[_motors_path + "/H"].create_dataset(
                "data", data=np.array(hkl_dict["H"])
            )
            h5w[_motors_path + "/K"].create_dataset(
                "data", data=np.array(hkl_dict["K"])
            )
            h5w[_motors_path + "/L"].create_dataset(
                "data", data=np.array(hkl_dict["L"])
            )

    def write_stat(self):
        """Method to write scan stats to the .Experiment file, so it can be used in scripts"""
        dict_ = {}
        for counter_name, counter in py4syn.counterDB.items():
            # Add statistic data as attributes
            with h5py.File(self.unique_filename, "a") as h5w:
                scan_idx = list(h5w["Scan"].keys())
                scan_idx = scan_idx[-1]

                _dataset_name = "Scan/" + scan_idx + "/instrument/" + counter_name
                _xlabel_points = (
                    "Scan/" + scan_idx + "/instrument/" + self.xlabel + "/data"
                )
                try:
                    y = h5w[_dataset_name][counter_name][:]
                except:
                    continue
                if self.xlabel == "points":
                    x = [i for i in range(len(y))]
                else:
                    x = h5w[_xlabel_points][:]

                scanModule.fitData(x[: len(y)], y)
                dict_[counter_name] = {}
                dict_[counter_name]["peak"] = float(scanModule.PEAK)
                dict_[counter_name]["peak_at"] = float(scanModule.PEAK_AT)
                dict_[counter_name]["FWHM"] = float(scanModule.FWHM)
                dict_[counter_name]["FWHM_at"] = float(scanModule.FWHM_AT)
                dict_[counter_name]["COM"] = float(scanModule.COM)

                dict_args = self.io.read()
                dict_args["scan_stats"] = dict_
                dict_args["scan_running"] = False
                self.io.write(dict_args)

    def add_scan_attrs(self):
        with h5py.File(self.unique_filename, "a") as h5w:
            scan_idx = list(h5w["Scan"].keys())
            scan_idx = scan_idx[-1]

            _instrument_path = "Scan/" + scan_idx + "/instrument/"

            dict_args = self.io.read()
            default_counter = dict_args["main_scan_counter"]

            h5w["Scan/" + scan_idx + "/instrument/"].attrs["main_motor"] = self.motor[0]
            if default_counter in self.counters_name:
                h5w["Scan/" + scan_idx + "/instrument/"].attrs[
                    "main_counter"
                ] = default_counter
            else:
                h5w["Scan/" + scan_idx + "/instrument/"].attrs[
                    "main_counter"
                ] = self.counters_name[0]

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
        self.write_stat()
        self.write_hkl()
        self.add_scan_attrs()
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

            scanModule.scan(*self.scan_args)

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
