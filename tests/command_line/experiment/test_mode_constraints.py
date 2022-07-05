import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.mode_constraints import ModeConstraints
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    def setUp(self):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 10000.0
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> ModeConstraints:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = ModeConstraints()
        return obj

    def test_GIVEN_cli_argument_WHEN_inputing_cons_mu_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-m", "1"])
        assert obj.parsed_args_dict["cons_Mu"] == 1.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_eta_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-e", "2"])
        assert obj.parsed_args_dict["cons_Eta"] == 2.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_chi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-c", "3"])
        assert obj.parsed_args_dict["cons_Chi"] == 3.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_phi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-p", "4"])
        assert obj.parsed_args_dict["cons_Phi"] == 4.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_nu_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-n", "5"])
        assert obj.parsed_args_dict["cons_Nu"] == 5.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_del_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-d", "6"])
        assert obj.parsed_args_dict["cons_Del"] == 6.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_alpha_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-a", "7"])
        assert obj.parsed_args_dict["cons_alpha"] == 7.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_beta_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-b", "8"])
        assert obj.parsed_args_dict["cons_beta"] == 8.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_psi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-psi", "9"])
        assert obj.parsed_args_dict["cons_psi"] == 9.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_omega_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-o", "10"])
        assert obj.parsed_args_dict["cons_omega"] == 10.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_qaz_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-q", "11"])
        assert obj.parsed_args_dict["cons_qaz"] == 11.

    def test_GIVEN_cli_argument_WHEN_inputing_cons_naz_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-cnaz", "12"])
        assert obj.parsed_args_dict["cons_naz"] == 12.

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


    # def test_GIVEN_cli_argument_WHEN_inputing_mode_225_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["225"])
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert "225" == dict_now["Mode"]
