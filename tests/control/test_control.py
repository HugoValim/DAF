import unittest

from bin.daf import Control


class TestControl(unittest.TestCase):

    MODES_TO_TEST = ((2, 0, 1, 4), (2, 1, 5), (0, 0, 1, 2, 3), (0, 2, 1, 3))
    HKLS_TO_TEST = ((1, 1, 1), (0, 1, 1), (0, 0, 1), (1, 0, 1), (2, 3, 10))
    SAMPLE_LIST = ("Si", "Ge", "AlAs", "Mo", "Ir20Mn80")

    def test_GIVEN_operation_modes_WHEN_mode_is_correct_THEN_it_is_right_setted(self):
        for test_mode in self.MODES_TO_TEST:
            exp = Control(*test_mode)
            mode = exp.mode
            for mode, setted_mode in zip(test_mode, mode):
                assert mode == setted_mode

    def test_GIVEN_operation_modes_WHEN_mode_is_correct_THEN_check_if_setup_is_correct(
        self,
    ):
        expected = (
            ("nu_fix", "--", "eta_fix", "phi_fix", "--"),
            ("nu_fix", "alpha = beta", "eta = delta/2", "--", "--"),
            ("--", "--", "eta_fix", "mu_fix", "chi_fix"),
            ("--", "alpha fix", "eta_fix", "chi_fix", "--"),
        )

        count = 0
        for test_mode in self.MODES_TO_TEST:
            exp = Control(*test_mode)
            setup = exp.setup
            assert expected[count] == setup
            count += 1

    def test_GIVEN_operation_modes_WHEN_building_motor_constraints_THEN_check_if_the_constraints_are_correct(
        self,
    ):
        expected = (
            ["Nu", "Eta", "Phi", "x"],
            ["Nu", "x", "x"],
            ["Eta", "Mu", "Chi"],
            ["Eta", "Chi", "x"],
        )

        count = 0
        for test_mode in self.MODES_TO_TEST:
            exp = Control(*test_mode)
            motor_constraints = exp.motor_constraints
            assert expected[count] == motor_constraints
            count += 1

    def test_GIVEN_operation_modes_WHEN_building_pseudo_angle_constraints_THEN_check_if_the_constraints_are_correct(
        self,
    ):
        expected = ([], ["aeqb", "eta=del/2"], [], ["alpha"])

        count = 0
        for test_mode in self.MODES_TO_TEST:
            exp = Control(*test_mode)
            pseudo_angle_constraints = exp.pseudo_angle_constraints
            assert expected[count] == pseudo_angle_constraints
            count += 1

    def test_GIVEN_operation_modes_WHEN_building_fixed_motor_lists_THEN_check_if_the_lists_are_correct(
        self,
    ):
        expected = (["Nu", "Eta", "Phi"], ["Nu"], ["Eta", "Mu", "Chi"], ["Eta", "Chi"])

        count = 0
        for test_mode in self.MODES_TO_TEST:
            exp = Control(*test_mode)
            fixed_motor_list = exp.fixed_motor_list
            assert expected[count] == fixed_motor_list
            count += 1

    def test_GIVEN_operation_modes_WHEN_building_pseudo_constraints_w_value_lists_THEN_check_if_the_lists_are_correct(
        self,
    ):
        expected = ([], [("aeqb", "--"), ("eta=del/2", "--")], [], [("alpha", 0)])

        count = 0
        for test_mode in self.MODES_TO_TEST:
            exp = Control(*test_mode)
            pseudo_constraints_w_value_list = exp.pseudo_constraints_w_value_list
            assert expected[count] == pseudo_constraints_w_value_list
            count += 1

    def test_GIVEN_a_predefined_sample_list_WHEN_defining_a_new_sample_THEN_check_if_the_sample_was_correctly_defined(
        self,
    ):
        count = 0
        for sample in self.SAMPLE_LIST:
            exp = Control(2, 1, 5)
            exp.set_material(sample)
            sample_now = exp.samp
            assert sample_now.name == sample
            count += 1

    def test_GIVEN_a_motor_or_pseudo_constraint_WHEN_user_set_new_value_THEN_check_if_was_correctly_defined(
        self,
    ):
        constraints_dict = {
            "Mu": 30,
            "Eta": 20,
            "Chi": 2,
            "Phi": 23,
            "Nu": 67,
            "Del": 38,
            "qaz": 41,
            "naz": 35.3,
            "alpha": 22.5,
            "beta": 44,
            "psi": 47,
            "omega": 90,
            "aeqb": "--",
            "eta=del/2": "--",
            "mu=nu/2": "--",
        }

        exp = Control(2, 0, 1, 2)
        motor_constraint, pseudo_constraints = exp.set_constraints(**constraints_dict)
        assert motor_constraint[4] == 67
        assert motor_constraint[1] == 20
        assert motor_constraint[0] == 30

        exp = Control(1, 0, 3, 4)
        motor_constraint, pseudo_constraints = exp.set_constraints(**constraints_dict)
        assert motor_constraint[5] == 38
        assert motor_constraint[2] == 2
        assert motor_constraint[3] == 23

        exp = Control(3, 1, 5)
        motor_constraint, pseudo_constraints = exp.set_constraints(**constraints_dict)
        for constraint in pseudo_constraints:
            if "qaz" in constraint:
                assert constraint[1] == 41
            if "aeqb" in constraint:
                assert constraint[1] == "--"
            if "eta=del/2" in constraint:
                assert constraint[1] == "--"

        exp = Control(4, 3, 1)
        motor_constraint, pseudo_constraints = exp.set_constraints(**constraints_dict)
        for constraint in pseudo_constraints:
            if "naz" in constraint:
                assert constraint[1] == 35.3
            if "beta" in constraint:
                assert constraint[1] == 44
            if "omega" in constraint:
                assert constraint[1] == 90

        exp = Control(0, 2, 1, 1)
        motor_constraint, pseudo_constraints = exp.set_constraints(**constraints_dict)
        for constraint in pseudo_constraints:
            if "alpha" in constraint:
                assert constraint[1] == 22.5

        exp = Control(0, 4, 1, 1)
        motor_constraint, pseudo_constraints = exp.set_constraints(**constraints_dict)
        for constraint in pseudo_constraints:
            if "psi" in constraint:
                assert constraint[1] == 47


if __name__ == "__main__":
    obj = TestControl()
    obj.test_GIVEN_a_motor_or_pseudo_constraint_WHEN_user_set_new_value_THEN_check_if_was_correctly_defined()
