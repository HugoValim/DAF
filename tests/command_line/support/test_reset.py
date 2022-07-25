import os
import sys

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
from daf.command_line.support.reset import Reset, main
import daf.utils.generate_daf_default as gdd


class TestDAF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 1
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    @classmethod
    def tearDownClass(cls):
        os.remove(".Experiment")
        os.remove("Log")

    @staticmethod
    def make_obj(command_line_args: list) -> Reset:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = Reset()
        return obj

    def test_GIVEN_cli_argument_WHEN_inputing_all_option_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--all"])
        assert obj.parsed_args_dict["all"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_hard_option_THEN_check_parsed_args(self):
        obj = self.make_obj(["--hard"])
        assert obj.parsed_args_dict["hard"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_check_if_it_was_written_correctly(
        self,
    ):
        dict_now = du.read()
        dict_now["Mode"] = "2023"
        du.write(dict_now)
        arg = "-a"
        full_arg = "all"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.experiment_file_dict["Mode"] == "2023"
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["Mode"] == "2052"

    def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-a",
        ]
        with patch.object(sys, "argv", testargs):
            main()
