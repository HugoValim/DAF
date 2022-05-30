import unittest

from bin.daf import Control

class TestControl(unittest.TestCase):

	def test_GIVEN_an_operation_mode_WHEN_mode_is_correct_THEN_it_is_right_setted(self):
		mode_to_set = (2, 0, 1, 5)
		exp = Control(*mode_to_set)
		mode = exp.mode
		for mode, setted_mode in zip(mode_to_set, mode):
			assert mode == setted_mode
