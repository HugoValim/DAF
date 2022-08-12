import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.mode_constraints import ModeConstraints, main
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
        assert obj.parsed_args_dict["cons_mu"] == 1.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_eta_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-e", "2"])
        assert obj.parsed_args_dict["cons_eta"] == 2.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_chi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-c", "3"])
        assert obj.parsed_args_dict["cons_chi"] == 3.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_phi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-p", "4"])
        assert obj.parsed_args_dict["cons_phi"] == 4.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_nu_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-n", "5"])
        assert obj.parsed_args_dict["cons_nu"] == 5.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_del_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-d", "6"])
        assert obj.parsed_args_dict["cons_del"] == 6.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_alpha_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-a", "7"])
        assert obj.parsed_args_dict["cons_alpha"] == 7.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_beta_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-b", "8"])
        assert obj.parsed_args_dict["cons_beta"] == 8.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_psi_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-psi", "9"])
        assert obj.parsed_args_dict["cons_psi"] == 9.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_omega_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-o", "10"])
        assert obj.parsed_args_dict["cons_omega"] == 10.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_qaz_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-q", "11"])
        assert obj.parsed_args_dict["cons_qaz"] == 11.0

    def test_GIVEN_cli_argument_WHEN_inputing_cons_naz_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-naz", "12"])
        assert obj.parsed_args_dict["cons_naz"] == 12.0

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

    def test_GIVEN_cli_argument_WHEN_inputing_cons_mu_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-m", "1"])
        assert obj.parsed_args_dict["cons_mu"] == 1.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 1.0 == dict_now["cons_mu"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_eta_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-e", "2"])
        assert obj.parsed_args_dict["cons_eta"] == 2.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 2.0 == dict_now["cons_eta"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_chi_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-c", "3"])
        assert obj.parsed_args_dict["cons_chi"] == 3.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 3.0 == dict_now["cons_chi"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_phi_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-p", "4"])
        assert obj.parsed_args_dict["cons_phi"] == 4.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 4.0 == dict_now["cons_phi"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_nu_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-n", "5"])
        assert obj.parsed_args_dict["cons_nu"] == 5.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 5.0 == dict_now["cons_nu"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_del_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-d", "6"])
        assert obj.parsed_args_dict["cons_del"] == 6.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 6.0 == dict_now["cons_del"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_alpha_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-a", "7"])
        assert obj.parsed_args_dict["cons_alpha"] == 7.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 7.0 == dict_now["cons_alpha"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_beta_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-b", "8"])
        assert obj.parsed_args_dict["cons_beta"] == 8.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 8.0 == dict_now["cons_beta"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_psi_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-psi", "9"])
        assert obj.parsed_args_dict["cons_psi"] == 9.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 9.0 == dict_now["cons_psi"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_omega_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-o", "10"])
        assert obj.parsed_args_dict["cons_omega"] == 10.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 10.0 == dict_now["cons_omega"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_qaz_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-q", "11"])
        assert obj.parsed_args_dict["cons_qaz"] == 11.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 11.0 == dict_now["cons_qaz"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_naz_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-naz", "12"])
        assert obj.parsed_args_dict["cons_naz"] == 12.0
        obj.run_cmd()
        dict_now = obj.io.read()
        assert 12.0 == dict_now["cons_naz"]

    def test_GIVEN_cli_argument_WHEN_inputing_cons_mu_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 1
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-m",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_mu"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_eta_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 2
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-e",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_eta"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_chi_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 3
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-c",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_chi"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_phi_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 4
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-p",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_phi"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_nu_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 5
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-n",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_nu"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_del_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 6
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-d",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_del"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_alpha_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 7
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-a",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_alpha"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_beta_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 8
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-b",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_beta"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_psi_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 9
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-psi",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_psi"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_omega_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 10
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-o",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_omega"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_qaz_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 11
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-q",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_qaz"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_cons_naz_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        val_to_cons = 12
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-naz",
            str(val_to_cons),
        ]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["cons_naz"] == val_to_cons

    def test_GIVEN_cli_argument_WHEN_inputing_reset_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert 0 == dict_now["cons_mu"]
        assert 0 == dict_now["cons_eta"]
        assert 0 == dict_now["cons_chi"]
        assert 0 == dict_now["cons_phi"]
        assert 0 == dict_now["cons_nu"]
        assert 0 == dict_now["cons_del"]
        assert 0 == dict_now["cons_alpha"]
        assert 0 == dict_now["cons_beta"]
        assert 0 == dict_now["cons_psi"]
        assert 0 == dict_now["cons_omega"]
        assert 0 == dict_now["cons_qaz"]
        assert 0 == dict_now["cons_naz"]

    def test_GIVEN_cli_argument_WHEN_inputing_reset_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-l"]
        with patch.object(sys, "argv", testargs):
            main()
