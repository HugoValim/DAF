import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.bounds import Bounds, main
import daf.utils.generate_daf_default as gdd
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
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> Bounds:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = Bounds()
        return obj

    def test_GIVEN_cli_argument_WHEN_inputing_cons_mu_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-m", "-10", "180"])
        assert obj.parsed_args_dict["mu"][0] == -10
        assert obj.parsed_args_dict["mu"][1] == 180

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_eta_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-e", "-11", "181"])
        assert obj.parsed_args_dict["eta"][0] == -11
        assert obj.parsed_args_dict["eta"][1] == 181

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_chi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-c", "-12", "182"])
        assert obj.parsed_args_dict["chi"][0] == -12
        assert obj.parsed_args_dict["chi"][1] == 182

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_phi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-p", "-13", "183"])
        assert obj.parsed_args_dict["phi"][0] == -13
        assert obj.parsed_args_dict["phi"][1] == 183

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_nu_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-n", "-14", "184"])
        assert obj.parsed_args_dict["nu"][0] == -14
        assert obj.parsed_args_dict["nu"][1] == 184

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_del_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-d", "-15", "185"])
        assert obj.parsed_args_dict["del"][0] == -15
        assert obj.parsed_args_dict["del"][1] == 185

    def test_GIVEN_cli_argument_WHEN_inputing_reset_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-r"])
        assert obj.parsed_args_dict["reset"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-l"])
        assert obj.parsed_args_dict["list"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_mu_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-m", "-10", "180"])
        assert obj.parsed_args_dict["mu"][0] == -10
        assert obj.parsed_args_dict["mu"][1] == 180
        obj.run_cmd()
        dict_now = obj.io.read()
        assert dict_now["motors"]["mu"]["bounds"][0] == -10
        assert dict_now["motors"]["mu"]["bounds"][1] == 180

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_eta_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-e", "-11", "181"])
        assert obj.parsed_args_dict["eta"][0] == -11
        assert obj.parsed_args_dict["eta"][1] == 181
        obj.run_cmd()
        dict_now = obj.io.read()
        assert dict_now["motors"]["eta"]["bounds"][0] == -11
        assert dict_now["motors"]["eta"]["bounds"][1] == 181

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_chi_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-c", "-12", "182"])
        assert obj.parsed_args_dict["chi"][0] == -12
        assert obj.parsed_args_dict["chi"][1] == 182
        obj.run_cmd()
        dict_now = obj.io.read()
        assert dict_now["motors"]["chi"]["bounds"][0] == -12
        assert dict_now["motors"]["chi"]["bounds"][1] == 182

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_phi_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-p", "-13", "183"])
        assert obj.parsed_args_dict["phi"][0] == -13
        assert obj.parsed_args_dict["phi"][1] == 183
        obj.run_cmd()
        dict_now = obj.io.read()
        assert dict_now["motors"]["phi"]["bounds"][0] == -13
        assert dict_now["motors"]["phi"]["bounds"][1] == 183

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_nu_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-n", "-14", "184"])
        assert obj.parsed_args_dict["nu"][0] == -14
        assert obj.parsed_args_dict["nu"][1] == 184
        obj.run_cmd()
        dict_now = obj.io.read()
        assert dict_now["motors"]["nu"]["bounds"][0] == -14
        assert dict_now["motors"]["nu"]["bounds"][1] == 184

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_del_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-d", "-15", "185"])
        assert obj.parsed_args_dict["del"][0] == -15
        assert obj.parsed_args_dict["del"][1] == 185
        obj.run_cmd()
        dict_now = obj.io.read()
        assert dict_now["motors"]["del"]["bounds"][0] == -15
        assert dict_now["motors"]["del"]["bounds"][1] == 185

    def test_GIVEN_cli_argument_WHEN_reset_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-r"])
        obj.run_cmd()
        dict_now = obj.io.read()
        assert dict_now["motors"]["mu"]["bounds"][0] == obj.DEFAULT_BOUNDS["mu"][0]
        assert dict_now["motors"]["mu"]["bounds"][1] == obj.DEFAULT_BOUNDS["mu"][1]
        assert dict_now["motors"]["eta"]["bounds"][0] == obj.DEFAULT_BOUNDS["eta"][0]
        assert dict_now["motors"]["eta"]["bounds"][1] == obj.DEFAULT_BOUNDS["eta"][1]
        assert dict_now["motors"]["chi"]["bounds"][0] == obj.DEFAULT_BOUNDS["chi"][0]
        assert dict_now["motors"]["chi"]["bounds"][1] == obj.DEFAULT_BOUNDS["chi"][1]
        assert dict_now["motors"]["phi"]["bounds"][0] == obj.DEFAULT_BOUNDS["phi"][0]
        assert dict_now["motors"]["phi"]["bounds"][1] == obj.DEFAULT_BOUNDS["phi"][1]
        assert dict_now["motors"]["nu"]["bounds"][0] == obj.DEFAULT_BOUNDS["nu"][0]
        assert dict_now["motors"]["nu"]["bounds"][1] == obj.DEFAULT_BOUNDS["nu"][1]
        assert dict_now["motors"]["del"]["bounds"][0] == obj.DEFAULT_BOUNDS["del"][0]
        assert dict_now["motors"]["del"]["bounds"][1] == obj.DEFAULT_BOUNDS["del"][1]

    def test_GIVEN_cli_argument_WHEN_inputing_mu_THEN_search_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-m",
            "-3",
            "30",
        ]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_eta_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-e",
            "-100",
            "100",
        ]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-l",
        ]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_reset_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-r",
        ]
        with patch.object(sys, "argv", testargs):
            main()
