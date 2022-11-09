import os
import sys
import time

import pytest
import unittest
from unittest.mock import patch

import daf.utils.dafutilities as du
from daf.gui.scripts.live_view_caller import main
import daf.utils.generate_daf_default as gdd


class TestDAF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 1
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    @classmethod
    def tearDownClass(cls):
        os.remove(".Experiment")
        os.remove("Log")

    def test_GIVEN_cli_argument_WHEN_running_cli_THEN_test_for_problems(
        self,
    ):
        proc = main()
        time.sleep(2)
        assert proc.poll() != 1
