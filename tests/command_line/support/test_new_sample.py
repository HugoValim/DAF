import os
import sys
import psutil
import shutil
import time

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
from daf.command_line.support.new_sample import NewSample, main
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
    def make_obj(command_line_args: list) -> NewSample:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = NewSample()
        return obj

    def test_GIVEN_cli_argument_WHEN_running_cli_THEN_test_for_problems(
        self,
    ):
        path_to_created_setup = "/home/hugo/pytest_folder"
        if os.path.isdir(path_to_created_setup):
            shutil.rmtree(path_to_created_setup)
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            path_to_created_setup,
        ]
        with patch.object(sys, "argv", testargs):
            main()
        assert os.path.isdir(path_to_created_setup)
        path_to_experiment_file = os.path.join(path_to_created_setup, du.DEFAULT)
        print(path_to_experiment_file)
        time.sleep(1)
        assert os.path.isfile(path_to_experiment_file)
