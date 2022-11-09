import os
import sys
import psutil

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
from daf.command_line.support.gui_all import GUIAll, main
import daf.utils.generate_daf_default as gdd
from daf.command_line.support.init import Init


class TestDAF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_sim = Init.build_current_file(Init, True)
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 1
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    @classmethod
    def tearDownClass(cls):
        os.remove(".Experiment")
        os.remove("Log")

    @staticmethod
    def check_if_process_is_running(process_name: str) -> bool:
        """
        Check if there is any running process that contains the given name processName.
        """
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    @staticmethod
    def make_obj(command_line_args: list) -> GUIAll:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = GUIAll()
        return obj

    def test_GIVEN_cli_argument_WHEN_running_cli_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        with patch.object(sys, "argv", testargs):
            main()
        assert self.check_if_process_is_running("daf_gui.py")
