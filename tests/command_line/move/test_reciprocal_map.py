import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np
from matplotlib.pyplot import show

import daf.utils.dafutilities as du
from daf.command_line.move.reciprocal_space_map import ReciprocalSpace, GraphAttributes
import daf.utils.generate_daf_default as gdd
from daf.command_line.support.init import Init
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    samples = ["Si", "Cu", "Fe"]

    def setUp(self):
        show(block=False)
        data_sim = Init.build_current_file(Init, True)
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 10000.0
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> ReciprocalSpace:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = ReciprocalSpace()
        return obj

    def test_GIVEN_cli_argument_WHEN_inputing_idir_THEN_check_parsed_args(self):
        obj = self.make_obj(["-i", "1", "1", "0"])
        assert obj.parsed_args_dict["idir"] == [1.0, 1.0, 0]

    def test_GIVEN_cli_argument_WHEN_inputing_ndir_THEN_check_parsed_args(self):
        obj = self.make_obj(["-n", "0", "1", "1"])
        assert obj.parsed_args_dict["ndir"] == [0.0, 1.0, 1.0]

    def test_GIVEN_cli_argument_WHEN_inputing_scale_THEN_check_parsed_args(self):
        obj = self.make_obj(["-s", "150"])
        assert obj.parsed_args_dict["scale"] == 150.0

    def test_GIVEN_cli_argument_WHEN_passing_hkl_111_THEN_check_parsed_args(self):
        obj = self.make_obj(["-m", "Si", "Cu"])
        assert obj.parsed_args_dict["materials"][0] == "Si"
        assert obj.parsed_args_dict["materials"][1] == "Cu"

    def test_GIVEN_cli_argument_WHEN_inputing_several_arguments_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(
            ["-s", "150", "-m", "Si", "Cu", "-n", "0", "1", "1", "-i", "1", "1", "0"]
        )
        assert obj.parsed_args_dict["idir"] == [1.0, 1.0, 0]
        assert obj.parsed_args_dict["ndir"] == [0.0, 1.0, 1.0]
        assert obj.parsed_args_dict["scale"] == 150.0
        assert obj.parsed_args_dict["materials"][0] == "Si"
        assert obj.parsed_args_dict["materials"][1] == "Cu"

    def test_GIVEN_cli_argument_WHEN_no_args_THEN_check_if_exp_was_created(self):
        obj = self.make_obj(["-s", "100"])
        assert isinstance(obj.exp, DAF)

    def test_GIVEN_cli_argument_WHEN_no_args_THEN_check_if_figure_was_created(self):
        obj = self.make_obj(["-s", "100"])
        graph_att_obj = obj.build_graph_att_obj([1, 1, 0], [0, 0, 1], 100)
        assert graph_att_obj.idir == [1, 1, 0]
        assert graph_att_obj.ndir == [0, 0, 1]
        assert graph_att_obj.idir == 100

    def test_GIVEN_cli_argument_WHEN_no_args_THEN_check_if_figure_was_created(self):
        obj = self.make_obj(["-s", "100"])
        graph_att_obj = obj.build_graph_att_obj([1, 1, 0], [0, 0, 1], 100)
        ax, h = obj.build_reciprocal_map(graph_att_obj)
        assert ax is not None

    def test_GIVEN_cli_argument_WHEN_no_args_THEN_check_if_figure_was_created(self):

        obj = self.make_obj(["-s", "100"])
        graph_att_obj = obj.build_graph_att_obj([1, 1, 0], [0, 0, 1], 100)
        ax, h = obj.build_reciprocal_map(graph_att_obj)
        for sample in self.samples:
            ax2, h2 = obj.append_to_reciprocal_map(sample, ax, graph_att_obj)
            assert ax2 is not None
            assert h2 is not None
