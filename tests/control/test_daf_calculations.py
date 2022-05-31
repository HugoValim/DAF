import unittest
import numpy as np

from bin.matrix_utils import calculate_rotation_matrix_from_diffractometer_angles, calculate_pseudo_angle_from_motor_angles
from bin.daf import Control

class TestControl(unittest.TestCase):

    MODES_TO_TEST = ((2, 0, 1, 4), (2, 1, 5), (0, 0, 1, 2, 3), (0, 2, 1, 3))
    HKLS_TO_TEST = ((1, 1, 1), (0, 1, 1), (0, 0, 1), (1, 0, 1), (2, 3, 10))
    SAMPLE_LIST = ("Si", "Ge", "AlAs", "Mo", "Ir20Mn80")

    def test_GIVEN_diffractometer_angles_WHEN_performing_rotation_matrix_calculation_THEN_check_if_is_correct(
        self,
    ):
        del_, eta, chi, phi, nu, mu = (
            10.73240,
            5.36620,
            35.26439,
            45.00000,
            0.00000,
            0.00000,
        )

        MU = np.array(
            [
                [1.00000000e00, 0.00000000e00, 0.00000000e00],
                [0.00000000e00, 1.00000000e00, -4.78799555e-25],
                [0.00000000e00, 4.78799555e-25, 1.00000000e00],
            ]
        )

        ETA = np.array(
            [
                [0.99561731, 0.09352097, 0.0],
                [-0.09352097, 0.99561731, 0.0],
                [0.0, 0.0, 1.0],
            ]
        )

        CHI = np.array(
            [
                [0.81649658, 0.0, 0.57735027],
                [0.0, 1.0, 0.0],
                [-0.57735027, 0.0, 0.81649658],
            ]
        )

        PHI = np.array(
            [
                [0.70710679, 0.70710677, 0.0],
                [-0.70710677, 0.70710679, 0.0],
                [0.0, 0.0, 1.0],
            ]
        )

        NU = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, -0.0], [0.0, 0.0, 1.0]])

        DEL = np.array(
            [
                [0.98250766, 0.18622219, 0.0],
                [-0.18622219, 0.98250766, 0.0],
                [0.0, 0.0, 1.0],
            ]
        )

        calculated_matrixes = calculate_rotation_matrix_from_diffractometer_angles(
            mu, eta, chi, phi, nu, del_
        )

        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(calculated_matrixes["mu"][i][j], MU[i][j], 5)
                self.assertAlmostEqual(calculated_matrixes["eta"][i][j], ETA[i][j], 5)
                self.assertAlmostEqual(calculated_matrixes["chi"][i][j], CHI[i][j], 5)
                self.assertAlmostEqual(calculated_matrixes["phi"][i][j], PHI[i][j], 5)
                self.assertAlmostEqual(calculated_matrixes["nu"][i][j], NU[i][j], 5)
                self.assertAlmostEqual(calculated_matrixes["del"][i][j], DEL[i][j], 5)

    def test_GIVEN_diffractometer_angles_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct(
        self,
    ):
        del_, eta, chi, phi, nu, mu = (
            10.73240,
            5.36620,
            35.26439,
            45.00000,
            0.00000,
            0.00000,
        )

        exp = Control(2, 1, 5)
        exp.set_material('Si')
        exp.set_hkl((1, 1 ,1))
        exp.set_exp_conditions(idir = (0, 1, 0), ndir = (0, 0, 1), rdir = (0, 0, 1), en = 0.58649)
        calculated_pseudo_angles = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, exp.samp, exp.hkl, 0.58649, (0, 0, 1), exp.U
        )

        pseudo_angles_to_compare = {"twotheta": 10.732397035244944, "theta": 5.366198517622472, "alpha": 3.0951538829252416, "qaz": 90.0, 
                                    "naz": 35.145842304193756, "tau": 54.735629207009254, 
                                    "psi": 90.00000171887339, "beta": 3.095153882925248, "omega": -0.0}
        for key in pseudo_angles_to_compare:
            self.assertAlmostEqual(pseudo_angles_to_compare[key], calculated_pseudo_angles[key], 5)


if __name__ == "__main__":
    obj = TestControl()
    obj.test_GIVEN_diffractometer_angles_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct()
