import os
import sys

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
from daf.command_line.support.command_help import CommandHelp, main
import daf.utils.generate_daf_default as gdd
from daf.command_line.support.init import Init


class TestDAF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_sim = Init.build_current_file(Init, True)
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 1
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    @classmethod
    def tearDownClass(cls):
        os.remove(".Experiment")
        os.remove("Log")

    @staticmethod
    def make_obj(command_line_args: list) -> CommandHelp:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = CommandHelp()
        return obj

    def test_GIVEN_cli_argument_WHEN_running_cli_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        with patch.object(sys, "argv", testargs):
            main()
