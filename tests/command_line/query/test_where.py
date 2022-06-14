import os
import sys

import pytest
import unittest
from unittest.mock import patch

from daf.command_line.query.where import Where
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    def setUp(self):
        gdd.generate_file(file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> Where:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.wh"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = Where()
        return obj

    def test_GIVEN_a_real_position_WHEN_calling_dafwh_THEN_do_sanity_check(self):
        obj = self.make_obj([])
        obj.experiment_file_dict["Phi"] = 45.00006
        obj.experiment_file_dict["Eta"] = 15.66943
        obj.experiment_file_dict["Del"] = 31.33886
        obj.experiment_file_dict["Chi"] = 35.26414
        obj.exp.set_exp_conditions(en=7320)
        h, k, l = obj.calc_hkl(obj.experiment_file_dict)
        self.assertAlmostEqual(h, 1.00000, 5)
        self.assertAlmostEqual(k, 1.00001, 5)
        self.assertAlmostEqual(l, 0.99999, 5)
