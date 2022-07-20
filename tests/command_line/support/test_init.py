import os
import sys

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
from daf.command_line.support.init import Init, main
import daf.utils.generate_daf_default as gdd

class TestDAF(unittest.TestCase):

    def setUp(self):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 1
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> Init:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = Init()
        return obj

    def test_GIVEN_cli_argument_WHEN_passing_simulated_option_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--simulated"])
        assert obj.parsed_args_dict["simulated"] == True

    def test_GIVEN_cli_argument_WHEN_passing_all_option_THEN_check_parsed_args(self):
        obj = self.make_obj(["--all"])
        assert obj.parsed_args_dict["all"] == True

    def test_GIVEN_cli_argument_WHEN_passing_all_options_THEN_check_parsed_args(self):
        obj = self.make_obj(["--all", "--simulated"])
        assert obj.parsed_args_dict["simulated"] == True
        assert obj.parsed_args_dict["all"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_simulated_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-s",
        ]
        with patch.object(sys, "argv", testargs):
            main()

