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



    # def test_GIVEN_cli_argument_WHEN_inputing_mode_225_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["225"])
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert "225" == dict_now["Mode"]
