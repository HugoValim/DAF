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
        assert obj.parsed_args_dict["bound_Mu"][0] == -10
        assert obj.parsed_args_dict["bound_Mu"][1] == 180

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_eta_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-e", "-11", "181"])
        assert obj.parsed_args_dict["bound_Eta"][0] == -11
        assert obj.parsed_args_dict["bound_Eta"][1] == 181

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_chi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-c", "-12", "182"])
        assert obj.parsed_args_dict["bound_Chi"][0] == -12
        assert obj.parsed_args_dict["bound_Chi"][1] == 182

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_phi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-p", "-13", "183"])
        assert obj.parsed_args_dict["bound_Phi"][0] == -13
        assert obj.parsed_args_dict["bound_Phi"][1] == 183

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_nu_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-n", "-14", "184"])
        assert obj.parsed_args_dict["bound_Nu"][0] == -14
        assert obj.parsed_args_dict["bound_Nu"][1] == 184

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_del_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-d", "-15", "185"])
        assert obj.parsed_args_dict["bound_Del"][0] == -15
        assert obj.parsed_args_dict["bound_Del"][1] == 185

    def test_GIVEN_cli_argument_WHEN_inputing_reset_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-r"])
        assert obj.parsed_args_dict["Reset"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-l"])
        assert obj.parsed_args_dict["List"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_mu_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-m", "-10", "180"])
        assert obj.parsed_args_dict["bound_Mu"][0] == -10
        assert obj.parsed_args_dict["bound_Mu"][1] == 180
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["bound_Mu"][0] == -10
        assert dict_now["bound_Mu"][1] == 180

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_eta_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-e", "-11", "181"])
        assert obj.parsed_args_dict["bound_Eta"][0] == -11
        assert obj.parsed_args_dict["bound_Eta"][1] == 181
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["bound_Eta"][0] == -11
        assert dict_now["bound_Eta"][1] == 181

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_chi_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-c", "-12", "182"])
        assert obj.parsed_args_dict["bound_Chi"][0] == -12
        assert obj.parsed_args_dict["bound_Chi"][1] == 182
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["bound_Chi"][0] == -12
        assert dict_now["bound_Chi"][1] == 182

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_phi_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-p", "-13", "183"])
        assert obj.parsed_args_dict["bound_Phi"][0] == -13
        assert obj.parsed_args_dict["bound_Phi"][1] == 183
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["bound_Phi"][0] == -13
        assert dict_now["bound_Phi"][1] == 183

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_nu_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-n", "-14", "184"])
        assert obj.parsed_args_dict["bound_Nu"][0] == -14
        assert obj.parsed_args_dict["bound_Nu"][1] == 184
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["bound_Nu"][0] == -14
        assert dict_now["bound_Nu"][1] == 184

    def test_GIVEN_cli_argument_WHEN_inputing_bounds_del_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-d", "-15", "185"])
        assert obj.parsed_args_dict["bound_Del"][0] == -15
        assert obj.parsed_args_dict["bound_Del"][1] == 185
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["bound_Del"][0] == -15
        assert dict_now["bound_Del"][1] == 185

    def test_GIVEN_cli_argument_WHEN_reset_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-r"])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["bound_Mu"][0] == obj.DEFAULT_BOUNDS["bound_Mu"][0]
        assert dict_now["bound_Mu"][1] == obj.DEFAULT_BOUNDS["bound_Mu"][1]
        assert dict_now["bound_Eta"][0] == obj.DEFAULT_BOUNDS["bound_Eta"][0]
        assert dict_now["bound_Eta"][1] == obj.DEFAULT_BOUNDS["bound_Eta"][1]
        assert dict_now["bound_Chi"][0] == obj.DEFAULT_BOUNDS["bound_Chi"][0]
        assert dict_now["bound_Chi"][1] == obj.DEFAULT_BOUNDS["bound_Chi"][1]
        assert dict_now["bound_Phi"][0] == obj.DEFAULT_BOUNDS["bound_Phi"][0]
        assert dict_now["bound_Phi"][1] == obj.DEFAULT_BOUNDS["bound_Phi"][1]
        assert dict_now["bound_Nu"][0] == obj.DEFAULT_BOUNDS["bound_Nu"][0]
        assert dict_now["bound_Nu"][1] == obj.DEFAULT_BOUNDS["bound_Nu"][1]
        assert dict_now["bound_Del"][0] == obj.DEFAULT_BOUNDS["bound_Del"][0]
        assert dict_now["bound_Del"][1] == obj.DEFAULT_BOUNDS["bound_Del"][1]

    def test_GIVEN_cli_argument_WHEN_inputing_anything_THEN_search_for_problems(
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
