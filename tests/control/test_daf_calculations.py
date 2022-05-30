import unittest
import numpy as np

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

        exp = Control(2, 1, 5)
        calculated_matrixes = exp.calculate_rotation_matrix_from_diffractometer_angles(
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


if __name__ == "__main__":
    obj = TestControl()
    obj.test_GIVEN_diffractometer_angles_WHEN_performing_rotation_matrix_calculation_THEN_check_if_is_correct()
