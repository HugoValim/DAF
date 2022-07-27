import os
import sys

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
import daf.utils.daf_paths as dp
from daf.command_line.support.setup import Setup, main
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

    def test_GIVEN_cli_argument_WHEN_inputing_new_THEN_check_if_the_file_was_created(
        self,
    ):
        arg = "-n"
        full_arg = "new"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param[0]
        obj.run_cmd(obj.parsed_args_dict)
        full_file_path = os.path.join(dp.DAF_CONFIGS, param[0])
        assert os.path.isfile(full_file_path)

    def test_GIVEN_cli_argument_WHEN_inputing_checkout_THEN_check_if_the_file_setup_was_succesfully_changed(
        self,
    ):
        arg = "-c"
        full_arg = "checkout"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param[0]
        obj.run_cmd(obj.parsed_args_dict)
        dict_args = du.read()
        os.system("daf.expt -sim")
        assert dict_args["setup"] == param[0]

    def test_GIVEN_cli_argument_WHEN_inputing_save_THEN_check_if_the_setup_was_saved(
        self,
    ):
        arg = "-s"
        full_arg = "save"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True
        obj.checkout_setup("default")
        obj.update_setup_description(".", "test desc")
        obj.run_cmd(obj.parsed_args_dict)
        path_to_the_setup = os.path.join(dp.DAF_CONFIGS, "default")
        dict_args = du.read(filepath=path_to_the_setup)
        assert dict_args["setup_desc"] == "test desc"

    def test_GIVEN_cli_argument_WHEN_inputing_save_as_THEN_check_if_the_setup_was_saved(
        self,
    ):
        arg = "-sa"
        full_arg = "save_as"
        param = ["my_awesome_setup"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == param[0]
        obj.update_setup_description(".", "test desc 2")
        obj.run_cmd(obj.parsed_args_dict)
        path_to_the_setup = os.path.join(dp.DAF_CONFIGS, param[0])
        dict_args = du.read(filepath=path_to_the_setup)
        assert dict_args["setup_desc"] == "test desc 2"

    # def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_test_for_problems(
    #     self,
    # ):
    #     testargs = [
    #         "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
    #         "-a",
    #     ]
    #     with patch.object(sys, "argv", testargs):
    #         main()
