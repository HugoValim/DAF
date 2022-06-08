import os
import sys

import pytest
import unittest
from unittest.mock import patch

from daf.command_line.support.init import Init

class TestDAF(unittest.TestCase):
    
    @staticmethod
    def make_obj(command_line_args: list) -> Init:
        testargs = ['/home/hugo/work/SOL/tmp/daf/command_line/daf.init']
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, 'argv', testargs):
            obj = Init()
        return obj


    def test_GIVEN_cli_argument_WHEN_passing_simulated_option_THEN_check_parsed_args(self):
        obj = self.make_obj(['--simulated'])
        assert obj.parsed_args_dict['simulated'] == True

    def test_GIVEN_cli_argument_WHEN_passing_all_option_THEN_check_parsed_args(self):
        obj = self.make_obj(['--all'])
        assert obj.parsed_args_dict['all'] == True

    def test_GIVEN_cli_argument_WHEN_passing_all_options_THEN_check_parsed_args(self):
        obj = self.make_obj(['--all', '--simulated'])
        assert obj.parsed_args_dict['simulated'] == True
        assert obj.parsed_args_dict['all'] == True

    
