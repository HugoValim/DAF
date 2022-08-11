import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.move.hkl_move import HKLMove, main
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    predefined_motor_dict = {
        "mu": 1.1971657231936314e-22,
        "eta": 11.402686406409414,
        "chi": 35.26439476525327,
        "phi": 44.999999194854674,
        "nu": 0.0,
        "del": 22.805372812818828,
        "hklnow": np.array([1.0, 1.0, 1.0]),
    }

    predefined_pseudo_dict ={
        "twotheta": 22.805372812818835,
        "theta": 11.402686406409417,
        "alpha": 6.554258723031806,
        "qaz": 90.0,
        "naz": 34.727763787897146,
        "tau": 54.735629207009254,
        "psi": 90.00000458366236,
        "beta": 6.554258723031807,
        "omega": -0.0,
    }

    def setUp(self):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 10000.0
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> HKLMove:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = HKLMove()
        return obj

    def test_GIVEN_cli_argument_WHEN_passing_hkl_111_THEN_check_parsed_args(self):
        obj = self.make_obj(["1", "1", "1"])
        assert obj.parsed_args_dict["hkl-position"] == [1.0, 1.0, 1.0]

    def test_GIVEN_cli_argument_WHEN_passing_quiet_option_THEN_check_parsed_args(self):
        obj = self.make_obj(["1", "1", "1", "--quiet"])
        assert obj.parsed_args_dict["quiet"] == True

    def test_GIVEN_cli_argument_WHEN_passing_marker_option_THEN_check_parsed_args(self):
        obj = self.make_obj(["1", "1", "1", "-m", "-"])
        assert obj.parsed_args_dict["marker"] == "-"

    def test_GIVEN_cli_argument_WHEN_passing_column_marker_option_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["1", "1", "1", "-cm", "%"])
        assert obj.parsed_args_dict["column_marker"] == "%"

    def test_GIVEN_cli_argument_WHEN_passing_size_option_THEN_check_parsed_args(self):
        obj = self.make_obj(["1", "1", "1", "-s", "16"])
        assert obj.parsed_args_dict["size"] == 16

    def test_GIVEN_cli_argument_WHEN_passing_several_option_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(
            ["1", "1", "1", "--quiet", "-m", "-", "-cm", "%", "-s", "16"]
        )
        assert obj.parsed_args_dict["hkl-position"] == [1.0, 1.0, 1.0]
        assert obj.parsed_args_dict["quiet"] == True
        assert obj.parsed_args_dict["marker"] == "-"
        assert obj.parsed_args_dict["column_marker"] == "%"
        assert obj.parsed_args_dict["size"] == 16

    def test_GIVEN_cli_argument_WHEN_any_hkl_THEN_check_if_exp_was_created(self):
        obj = self.make_obj(["1", "1", "1"])
        assert isinstance(obj.exp, DAF)

    def test_GIVEN_cli_argument_WHEN_hkl_111_passed_THEN_check_if_it_was_calculated_right(
        self,
    ):
        obj = self.make_obj(["1", "1", "1"])
        error = obj.calculate_hkl(obj.parsed_args_dict["hkl-position"])
        assert error < 1e-4

    def test_GIVEN_cli_argument_WHEN_hkl_111_passed_THEN_check_calculated_angles(self):
        obj = self.make_obj(["1", "1", "1"])
        error = obj.calculate_hkl(obj.parsed_args_dict["hkl-position"])
        exp_dict = obj.get_angles_from_calculated_exp()
        # Do not need to compare the hkl value, only angles
        iter_list = list(self.predefined_motor_dict.keys())[:-1]
        for key in iter_list:
            self.assertAlmostEqual(self.predefined_motor_dict[key], exp_dict[key], 4)

    def test_GIVEN_cli_argument_WHEN_hkl_111_passed_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["1", "1", "1"])
        error = obj.calculate_hkl(obj.parsed_args_dict["hkl-position"])
        exp_dict = obj.get_angles_from_calculated_exp()
        obj.write_angles_if_small_error(error)
        io = du.DAFIO()
        dict_now = io.read()
        iter_list = list(self.predefined_motor_dict.keys())[:-1]
        for key in iter_list:
            self.assertAlmostEqual(self.predefined_motor_dict[key], dict_now["motors"][key]["value"], 2)
        for key in self.predefined_pseudo_dict.keys():
            self.assertAlmostEqual(self.predefined_pseudo_dict[key], dict_now[key], 2)


    def test_GIVEN_cli_argument_WHEN_inputing_1_1_1_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "1", "1", "1"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_2_0_0_quiet_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "2", "0", "0", "-q"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_printing_options_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "1",
            "2",
            "2",
            '-m',
            '*',
            '-cm',
            'I',
            '-s',
            '16'
        ]
        with patch.object(sys, "argv", testargs):
            main()


