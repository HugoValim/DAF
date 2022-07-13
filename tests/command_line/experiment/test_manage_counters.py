import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.manage_counters import ManageCounters, main
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
        obj = self.make_obj(["-s", "test_counter"])
        assert obj.parsed_args_dict['set_default'] == "test_counter"

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_eta_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-e", "2"])
    #     assert obj.parsed_args_dict["cons_Eta"] == 2.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_chi_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-c", "3"])
    #     assert obj.parsed_args_dict["cons_Chi"] == 3.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_phi_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-p", "4"])
    #     assert obj.parsed_args_dict["cons_Phi"] == 4.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_nu_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-n", "5"])
    #     assert obj.parsed_args_dict["cons_Nu"] == 5.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_del_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-d", "6"])
    #     assert obj.parsed_args_dict["cons_Del"] == 6.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_alpha_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-a", "7"])
    #     assert obj.parsed_args_dict["cons_alpha"] == 7.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_beta_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-b", "8"])
    #     assert obj.parsed_args_dict["cons_beta"] == 8.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_psi_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-psi", "9"])
    #     assert obj.parsed_args_dict["cons_psi"] == 9.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_omega_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-o", "10"])
    #     assert obj.parsed_args_dict["cons_omega"] == 10.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_qaz_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-q", "11"])
    #     assert obj.parsed_args_dict["cons_qaz"] == 11.0

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_naz_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-cnaz", "12"])
    #     assert obj.parsed_args_dict["cons_naz"] == 12.0

    # def test_GIVEN_cli_argument_WHEN_inputing_reset_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-r"])
    #     assert obj.parsed_args_dict["Reset"] == True

    # def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_check_parsed_args(
    #     self,
    # ):
    #     obj = self.make_obj(["-l"])
    #     assert obj.parsed_args_dict["List"] == True

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_mu_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-m", "1"])
    #     assert obj.parsed_args_dict["cons_Mu"] == 1.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 1.0 == dict_now["cons_Mu"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_eta_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-e", "2"])
    #     assert obj.parsed_args_dict["cons_Eta"] == 2.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 2.0 == dict_now["cons_Eta"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_chi_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-c", "3"])
    #     assert obj.parsed_args_dict["cons_Chi"] == 3.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 3.0 == dict_now["cons_Chi"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_phi_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-p", "4"])
    #     assert obj.parsed_args_dict["cons_Phi"] == 4.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 4.0 == dict_now["cons_Phi"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_nu_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-n", "5"])
    #     assert obj.parsed_args_dict["cons_Nu"] == 5.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 5.0 == dict_now["cons_Nu"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_del_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-d", "6"])
    #     assert obj.parsed_args_dict["cons_Del"] == 6.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 6.0 == dict_now["cons_Del"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_alpha_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-a", "7"])
    #     assert obj.parsed_args_dict["cons_alpha"] == 7.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 7.0 == dict_now["cons_alpha"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_beta_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-b", "8"])
    #     assert obj.parsed_args_dict["cons_beta"] == 8.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 8.0 == dict_now["cons_beta"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_psi_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-psi", "9"])
    #     assert obj.parsed_args_dict["cons_psi"] == 9.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 9.0 == dict_now["cons_psi"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_omega_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-o", "10"])
    #     assert obj.parsed_args_dict["cons_omega"] == 10.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 10.0 == dict_now["cons_omega"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_qaz_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-q", "11"])
    #     assert obj.parsed_args_dict["cons_qaz"] == 11.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 11.0 == dict_now["cons_qaz"]

    # def test_GIVEN_cli_argument_WHEN_inputing_cons_naz_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-cnaz", "12"])
    #     assert obj.parsed_args_dict["cons_naz"] == 12.0
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 12.0 == dict_now["cons_naz"]

    # def test_GIVEN_cli_argument_WHEN_reset_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-r"])
    #     # assert obj.parsed_args_dict["cons_naz"] == 12.
    #     # obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert 1 == dict_now["cons_Mu"]
    #     assert 2 == dict_now["cons_Eta"]
    #     assert 3 == dict_now["cons_Chi"]
    #     assert 4 == dict_now["cons_Phi"]
    #     assert 5 == dict_now["cons_Nu"]
    #     assert 6 == dict_now["cons_Del"]
    #     assert 7 == dict_now["cons_alpha"]
    #     assert 8 == dict_now["cons_beta"]
    #     assert 9 == dict_now["cons_psi"]
    #     assert 10 == dict_now["cons_omega"]
    #     assert 11 == dict_now["cons_qaz"]
    #     assert 12 == dict_now["cons_naz"]

    def test_GIVEN_cli_argument_WHEN_inputing_anything_THEN_search_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-l"]
        with patch.object(sys, "argv", testargs):
            main()
