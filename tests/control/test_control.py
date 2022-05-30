import unittest

from bin.daf import Control

class TestControl(unittest.TestCase):

	def test_GIVEN_an_operation_mode_WHEN_mode_is_correct_THEN_it_is_right_setted(self):
		mode_to_set = (2, 0, 1, 5)
		exp = Control(*mode)
		mode = exp.mode
		for i in mode:
			assert mode_to_set[i] == mode[i]
			
