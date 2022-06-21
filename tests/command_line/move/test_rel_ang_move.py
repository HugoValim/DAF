import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.move.rel_ang_move import RelAngleMove
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    predefined_dict = {
        "Mu": 1.1971657231936314e-22,
        "Eta": 11.402686406409414,
        "Chi": 35.26439476525327,
        "Phi": 44.999999194854674,
        "Nu": 0.0,
        "Del": 22.805372812818828,
        "tt": 22.805372812818835,
        "theta": 11.402686406409417,
        "alpha": 6.554258723031806,
        "qaz": 90.0,
        "naz": 34.727763787897146,
        "tau": 54.735629207009254,
        "psi": 90.00000458366236,
        "beta": 6.554258723031807,
        "omega": -0.0,
        "hklnow": np.array([1.0, 1.0, 1.0]),
    }

    def setUp(self):
        data_sim = gdd.default
        data_sim["simulated"] = True
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> RelAngleMove:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = RelAngleMove()
        return obj

    def test_GIVEN_cli_argument_WHEN_mu_is_30_THEN_check_parsed_args(self):
        obj = self.make_obj(["-m", "30"])
        assert float(obj.parsed_args_dict["Mu"]) == 30

    def test_GIVEN_cli_argument_WHEN_eta_is_10_THEN_check_parsed_args(self):
        obj = self.make_obj(["-e", "10"])
        assert float(obj.parsed_args_dict["Eta"]) == 10

    def test_GIVEN_cli_argument_WHEN_chi_is_15_THEN_check_parsed_args(self):
        obj = self.make_obj(["-c", "15"])
        assert float(obj.parsed_args_dict["Chi"]) == 15

    def test_GIVEN_cli_argument_WHEN_phi_is_20_THEN_check_parsed_args(self):
        obj = self.make_obj(["-p", "20"])
        assert float(obj.parsed_args_dict["Phi"]) == 20

    def test_GIVEN_cli_argument_WHEN_nu_is_25_THEN_check_parsed_args(self):
        obj = self.make_obj(["-n", "25"])
        assert float(obj.parsed_args_dict["Nu"]) == 25

    def test_GIVEN_cli_argument_WHEN_del_is_30_THEN_check_parsed_args(self):
        obj = self.make_obj(["-d", "33"])
        assert float(obj.parsed_args_dict["Del"]) == 33

    def test_GIVEN_cli_argument_WHEN_several_arguments_are_passed_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-n", "25", "-e", "10", "-d", "5"])
        assert float(obj.parsed_args_dict["Nu"]) == 25
        assert float(obj.parsed_args_dict["Eta"]) == 10
        assert float(obj.parsed_args_dict["Del"]) == 5

    def test_GIVEN_cli_argument_WHEN_mu_is_moved_THEN_check_if_written(
        self,
    ):
        dict_before = du.read()
        pos_to_move = 1
        obj = self.make_obj(["-m", str(pos_to_move)])
        obj.write_angles(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["Mu"] == dict_before["Mu"] + pos_to_move

    def test_GIVEN_cli_argument_WHEN_eta_is_moved_THEN_check_if_written(
        self,
    ):
        dict_before = du.read()
        pos_to_move = -2
        obj = self.make_obj(["-e", str(pos_to_move)])
        obj.write_angles(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["Eta"] == dict_before["Eta"] + pos_to_move

    def test_GIVEN_cli_argument_WHEN_chi_is_moved_THEN_check_if_written(
        self,
    ):
        dict_before = du.read()
        pos_to_move = 22
        obj = self.make_obj(["-c", str(pos_to_move)])
        obj.write_angles(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["Chi"] == dict_before["Chi"] + pos_to_move

    def test_GIVEN_cli_argument_WHEN_phi_is_moved_THEN_check_if_written(
        self,
    ):
        dict_before = du.read()
        pos_to_move = 4
        obj = self.make_obj(["-p", str(pos_to_move)])
        obj.write_angles(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["Phi"] == dict_before["Phi"] + pos_to_move

    def test_GIVEN_cli_argument_WHEN_nu_is_moved_THEN_check_if_written(
        self,
    ):
        dict_before = du.read()
        pos_to_move = 5
        obj = self.make_obj(["-n", str(pos_to_move)])
        obj.write_angles(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["Nu"] == dict_before["Nu"] + pos_to_move

    def test_GIVEN_cli_argument_WHEN_del_is_moved_THEN_check_if_written(
        self,
    ):
        dict_before = du.read()
        pos_to_move = -6
        obj = self.make_obj(["-d", str(pos_to_move)])
        obj.write_angles(obj.parsed_args_dict)
        dict_now = du.read()
        assert dict_now["Del"] == dict_before["Del"] + pos_to_move

    def test_GIVEN_cli_argument_WHEN_any_motor_is_moved_THEN_check_pseudo_angles_write(
        self,
    ):
        pos_to_move = 10
        obj = self.make_obj(["-e", str(pos_to_move)])
        obj.write_angles(obj.parsed_args_dict)
        pseudo_dict = obj.get_pseudo_angles_from_motor_angles()
        obj.write_to_experiment_file(pseudo_dict)
        dict_now = du.read()
        del pseudo_dict["q_vector"]
        del pseudo_dict["q_vector_norm"]
        for key, value in pseudo_dict.items():
            self.assertAlmostEqual(dict_now[key], pseudo_dict[key], 5)
