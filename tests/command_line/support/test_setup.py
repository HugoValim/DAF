import os
import sys

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
from daf.command_line.support.setup import Setup, main
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
        # os.remove("Log")

    @staticmethod
    def make_obj(command_line_args: list) -> Setup:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = Setup()
        return obj

    def test_GIVEN_cli_argument_WHEN_inputing_new_THEN_check_parsed_args(
        self,
    ):
        arg = "-n"
        full_arg = "new"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param[0]

    def test_GIVEN_cli_argument_WHEN_inputing_checkout_THEN_check_parsed_args(
        self,
    ):
        arg = "-c"
        full_arg = "checkout"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param[0]

    def test_GIVEN_cli_argument_WHEN_inputing_save_THEN_check_parsed_args(
        self,
    ):
        arg = "-s"
        full_arg = "save"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_save_as_THEN_check_parsed_args(
        self,
    ):
        arg = "-sa"
        full_arg = "save_as"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param[0]

    def test_GIVEN_cli_argument_WHEN_inputing_remove_THEN_check_parsed_args(
        self,
    ):
        arg = "-r"
        full_arg = "remove"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_check_parsed_args(
        self,
    ):
        arg = "-l"
        full_arg = "list"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_description_THEN_check_parsed_args(
        self,
    ):
        arg = "-d"
        full_arg = "description"
        param = ["my_awesome_setup", "my awesome description"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param

    def test_GIVEN_cli_argument_WHEN_inputing_info_THEN_check_parsed_args(
        self,
    ):
        arg = "-i"
        full_arg = "info"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param[0]


    # def test_GIVEN_cli_argument_WHEN_inputing_hard_option_THEN_check_parsed_args(self):
    #     obj = self.make_obj(["--hard"])
    #     assert obj.parsed_args_dict["hard"] == True

    # def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     dict_now = du.read()
    #     dict_now["Mode"] = "2023"
    #     du.write(dict_now)
    #     arg = "-a"
    #     full_arg = "all"
    #     param = []
    #     obj = self.make_obj([arg, *param])
    #     assert obj.experiment_file_dict["Mode"] == "2023"
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert dict_now["Mode"] == "2052"

    # def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_test_for_problems(
    #     self,
    # ):
    #     testargs = [
    #         "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
    #         "-a",
    #     ]
    #     with patch.object(sys, "argv", testargs):
    #         main()
