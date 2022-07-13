import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.manage_counters import ManageCounters, main
import daf.utils.generate_daf_default as gdd
from daf.utils import daf_paths as dp
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 10000.0
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    @classmethod
    def tearDownClass(cls):
        os.remove(".Experiment")
        os.remove("Log")

    @staticmethod
    def make_obj(command_line_args: list) -> ManageCounters:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = ManageCounters()
        return obj

    def test_GIVEN_cli_argument_WHEN_inputing_set_default_THEN_check_parsed_args(
        self,
    ):
        arg = "-s"
        full_arg = "set_default"
        param = "test_counter"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == param

    def test_GIVEN_cli_argument_WHEN_inputing_new_THEN_check_parsed_args(
        self,
    ):
        arg = "-n"
        full_arg = "new"
        param = "test_counter"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == param

    def test_GIVEN_cli_argument_WHEN_inputing_add_counter_THEN_check_parsed_args(
        self,
    ):
        arg = "-a"
        full_arg = "add_counter"
        param = "test_counter"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == [param]

    def test_GIVEN_cli_argument_WHEN_inputing_remove_counter_THEN_check_parsed_args(
        self,
    ):
        arg = "-rc"
        full_arg = "remove_counter"
        param = "test_counter"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == [param]

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_check_parsed_args(
        self,
    ):
        arg = "-l"
        full_arg = "list"
        param = True
        obj = self.make_obj([arg])
        assert obj.parsed_args_dict[full_arg] == param

    def test_GIVEN_cli_argument_WHEN_inputing_list_counters_THEN_check_parsed_args(
        self,
    ):
        arg = "-lc"
        full_arg = "list_counters"
        param = "test_counters"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == [param]

    def test_GIVEN_cli_argument_WHEN_inputing_list_all_counters_THEN_check_parsed_args(
        self,
    ):
        arg = "-lac"
        full_arg = "list_all_counters"
        param = True
        obj = self.make_obj([arg])
        assert obj.parsed_args_dict[full_arg] == param

    def test_GIVEN_cli_argument_WHEN_inputing_main_counter_THEN_check_parsed_args(
        self,
    ):
        arg = "-m"
        full_arg = "main_counter"
        param = "test_counter"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == param

    def test_GIVEN_cli_argument_WHEN_inputing_new_THEN_check_if_the_file_was_created(
        self,
    ):
        arg = "-n"
        full_arg = "new"
        param = "new_config"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == param
        obj.run_cmd(obj.parsed_args_dict)
        full_file_path = obj.get_full_file_path(param)
        assert os.path.isfile(full_file_path)

    def test_GIVEN_cli_argument_WHEN_inputing_add_counter_THEN_check_if_it_was_written(
        self,
    ):
        arg = "-a"
        full_arg = "add_counter"
        param = ["test_add", "ringcurrent"]
        obj = self.make_obj([arg, param[0], param[1]])
        obj.create_new_configuration_file(param[0])
        obj.run_cmd(obj.parsed_args_dict)
        obj.get_full_file_path(param[0])
        full_file_path = obj.get_full_file_path(param[0])
        data = obj.read_yaml(full_file_path)
        assert param[1] in data

    def test_GIVEN_cli_argument_WHEN_inputing_delte_counter_THEN_check_if_it_was_written(
        self,
    ):
        arg = "-rc"
        full_arg = "remove_counter"
        param = ["test_delete", "ringcurrent"]
        obj = self.make_obj([arg, param[0], param[1]])
        obj.create_new_configuration_file(param[0])
        obj.add_counters_to_a_file(param[0], [param[1]])
        obj.run_cmd(obj.parsed_args_dict)
        obj.get_full_file_path(param[0])
        full_file_path = obj.get_full_file_path(param[0])
        data = obj.read_yaml(full_file_path)
        assert param[1] not in data

    def test_GIVEN_cli_argument_WHEN_inputing_remove_THEN_check_if_the_file_was_created(
        self,
    ):
        arg = "-r"
        full_arg = "remove"
        param = "file_to_remove"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == [param]
        obj.create_new_configuration_file("file_to_remove")
        obj.run_cmd(obj.parsed_args_dict)
        full_file_path = obj.get_full_file_path(param)
        assert os.path.isfile(full_file_path) == False

    def test_GIVEN_cli_argument_WHEN_inputing_set_default_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-s"
        full_arg = "set_default"
        param = "daf_default"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == param
        obj.create_new_configuration_file(param)
        obj.run_cmd(obj.parsed_args_dict)
        dict_args = du.read()
        assert dict_args["default_counters"] == obj.YAML_PREFIX + param + obj.YAML_SUFIX

    def test_GIVEN_cli_argument_WHEN_inputing_main_counter_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-m"
        full_arg = "main_counter"
        param = "ringcurrent"
        obj = self.make_obj([arg, param])
        assert obj.parsed_args_dict[full_arg] == param
        obj.run_cmd(obj.parsed_args_dict)
        dict_args = du.read()
        assert dict_args["main_scan_counter"] == param

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-l"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_list_all_counters_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-lac"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_list_counters_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-n",
            "test_list",
            "-lc",
            "test_list",
        ]
        with patch.object(sys, "argv", testargs):
            main()
