#!/usr/bin/env python3
"""Library for reading and writing experiment files."""
from __future__ import annotations

import logging
from typing import Any

import epics
import yaml

from daf.utils.daf_paths import DAFPaths as dp
from daf.utils.experiment_file_schema import ExperimentFile
from daf.utils.experiment_file_store import ExperimentFileStore
from daf.utils.epics_motor_client import EpicsMotorClient

logger = logging.getLogger(__name__)


def _default_path():
    return dp.check_for_local_config()


DEFAULT = _default_path


def read_yml(filepath: str = None):
    """Just get the data from .Experiment file without any epics command"""
    with open(filepath) as file:
        data = yaml.safe_load(file)
        return data


def fetch_pvs_and_check_for_connection():
    """Fetch all motos PVs to check if it is connect or not. If it is not connected change the up bit to 0"""
    data = ExperimentFileStore.only_read()
    for key in data["motors"].keys():
        val = epics.caget(data["motors"][key]["pv"], timeout=2)
        if val is None:
            logger.warning(
                "Cannot connect to %s, PV: %s", key, data["motors"][key]["pv"]
            )
            data["motors"][key]["up"] = 0
    return data


def zero_offline_motors_and_bl_pvs(dict_: dict[str, Any]) -> None:
    """Explicit policy: zero out offline motors and beamline PVs before persisting.

    This is applied at the seam between EPICS communication and file storage
    so the policy is visible, not hidden inside the persistence layer.
    """
    for motor in dict_["motors"].keys():
        if not dict_["motors"][motor]["up"]:
            dict_["motors"][motor]["value"] = 0
            dict_["motors"][motor]["bounds"][0] = 0
            dict_["motors"][motor]["bounds"][1] = 0

    for bl_pv in dict_["beamline_pvs"].keys():
        if not dict_["beamline_pvs"][bl_pv]["up"]:
            dict_["beamline_pvs"][bl_pv]["value"] = 0


class DAFIO:
    def __init__(self, read=True):
        self.file_store = ExperimentFileStore()
        if read:
            self.epics_client = EpicsMotorClient()
            if self.file_store.filepath.exists():
                self.epics_client.build_epics_pvs(self.file_store.read())
            self.epics_put_flag = True
            self.epics_get_flag = True
        else:
            self.epics_client = None
            self.epics_put_flag = False
            self.epics_get_flag = False

    def sync_with_environment(self):
        """Get PVs and sync with it"""
        self.write(self.read())

    @staticmethod
    def only_read(filepath=None):
        """Just get the data from .Experiment file without any epics command"""
        return ExperimentFileStore.only_read(filepath)

    def stop(self):
        """Stop all motors"""
        if self.epics_client is not None:
            self.epics_client.stop()

    def wait(self):
        """Wait for all motors to reach its position"""
        if self.epics_client is not None:
            self.epics_client.wait()

    def epics_get(self, dict_):
        """Method to sync DAF with PVs"""
        if self.epics_client is not None:
            return self.epics_client.epics_get(dict_)
        return dict_

    def epics_put(self, dict_):
        """Method to write inputed values to PV"""
        if self.epics_client is not None:
            self.epics_client.epics_put(dict_)

    def read(self, filepath=None) -> ExperimentFile:
        """Read data from the experiment file."""
        if filepath is not None:
            store = ExperimentFileStore(filepath)
        else:
            store = self.file_store
        data = store.read()
        if self.epics_get_flag:
            data = self.epics_get(data)
        return data

    def check_for_offline_motors_and_bl_pvs_before_write(self, dict_: dict):
        """Check for a offline motor before writing, if it is offline, set all values as 0"""
        zero_offline_motors_and_bl_pvs(dict_)

    def write(self, dict_, filepath=None):
        """Write data to experiment file and also move motors if needed"""
        if filepath is not None:
            store = ExperimentFileStore(filepath)
        else:
            store = self.file_store
        if self.epics_put_flag:
            self.epics_put(dict_)
        # Explicit zeroing policy at the seam before persistence
        zero_offline_motors_and_bl_pvs(dict_)
        store.write(dict_)


def iter_motors(experiment_dict: dict):
    """Yield motor names from an experiment file dict."""
    yield from experiment_dict["motors"].keys()
