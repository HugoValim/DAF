import unittest

from bin.daf import Control

class TestControl(unittest.TestCase):

	MODES_TO_TEST = ((2, 0, 1, 4), (2, 1, 5), (0, 0, 1, 2, 3), (0, 2, 1, 3))

	def test_GIVEN_operation_modes_WHEN_mode_is_correct_THEN_it_is_right_setted(self):
		for test_mode in self.MODES_TO_TEST:
			exp = Control(*test_mode)
			mode = exp.mode
			for mode, setted_mode in zip(test_mode, mode):
				assert mode == setted_mode

	def test_GIVEN_operation_modes_WHEN_mode_is_correct_THEN_check_if_setup_is_correct(self):
		expected = (
				('nu_fix', '--', 'eta_fix', 'phi_fix', '--'),
				('nu_fix', 'alpha = beta', 'eta = delta/2', '--', '--'),
				('--', '--', 'eta_fix', 'mu_fix', 'chi_fix'),
				('--', 'alpha fix', 'eta_fix', 'chi_fix', '--')
			)

		count = 0
		for test_mode in self.MODES_TO_TEST:
			exp = Control(*test_mode)
			setup = exp.setup
			assert expected[count] == setup
			count += 1

	def test_GIVEN_operation_modes_WHEN_building_motor_constraints_THEN_check_if_the_constraints_are_correct(self):
		expected = (
					['Nu', 'Eta', 'Phi', 'x'],
					['Nu', 'x', 'x'],
					['Eta', 'Mu', 'Chi'],
					['Eta', 'Chi', 'x']
				)

		count = 0
		for test_mode in self.MODES_TO_TEST:
			exp = Control(*test_mode)
			motor_constraints = exp.motor_constraints
			assert expected[count] == motor_constraints
			count += 1

	def test_GIVEN_operation_modes_WHEN_building_pseudo_angle_constraints_THEN_check_if_the_constraints_are_correct(self):
		expected = (
					[],
					['aeqb', 'eta=del/2'],
					[],
					['alpha']
				)
		
		count = 0
		for test_mode in self.MODES_TO_TEST:
			exp = Control(*test_mode)
			pseudo_angle_constraints = exp.pseudo_angle_constraints
			assert expected[count] == pseudo_angle_constraints
			count += 1

	def test_GIVEN_operation_modes_WHEN_building_fixed_motor_lists_THEN_check_if_the_lists_are_correct(self):
		expected = (
					['Nu', 'Eta', 'Phi'],
					['Nu'],
					['Eta', 'Mu', 'Chi'],
					['Eta', 'Chi']
				)
		
		count = 0
		for test_mode in self.MODES_TO_TEST:
			exp = Control(*test_mode)
			fixed_motor_list = exp.fixed_motor_list
			assert expected[count] == fixed_motor_list
			count += 1

	def test_GIVEN_operation_modes_WHEN_building_pseudo_constraints_w_value_lists_THEN_check_if_the_lists_are_correct(self):
		expected = (
					[],
					[('aeqb', '--'), ('eta=del/2', '--')],
					[],
					[('alpha', 0)]
				)
		
		count = 0
		for test_mode in self.MODES_TO_TEST:
			exp = Control(*test_mode)
			pseudo_constraints_w_value_list = exp.pseudo_constraints_w_value_list
			assert expected[count] == pseudo_constraints_w_value_list
			count += 1



if __name__ == "__main__":
	obj = TestControl()
	obj.test_GIVEN_operation_modes_WHEN_building_only_pseudo_constraint_lists_THEN_check_if_the_lists_are_correct()