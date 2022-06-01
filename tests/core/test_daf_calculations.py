import unittest
import numpy as np

from daf.core.matrix_utils import calculate_rotation_matrix_from_diffractometer_angles, calculate_pseudo_angle_from_motor_angles
from daf.core.main import DAF

class TestDAF(unittest.TestCase):

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

    def test_GIVEN_mode_215_and_hkl_111_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct(
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

        exp = DAF(2, 1, 5)
        exp.set_material('Si')
        exp.set_hkl((1, 1 ,1))
        calculated_pseudo_angles = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, exp.samp, exp.hkl, 0.58649, (0, 0, 1), exp.U
        )

        pseudo_angles_to_compare = {"twotheta": 10.732397035244944, "theta": 5.366198517622472, "alpha": 3.0951538829252416, "qaz": 90.0, 
                                    "naz": 35.145842304193756, "tau": 54.735629207009254, 
                                    "psi": 90.00000171887339, "beta": 3.095153882925248, "omega": -0.0}
        for key in pseudo_angles_to_compare:
            self.assertAlmostEqual(pseudo_angles_to_compare[key], calculated_pseudo_angles[key], 5)

    def test_GIVEN_mode_215_and_hkl_203_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct(
        self,
    ):
        del_, eta, chi, phi, nu, mu = (
            48.60477,
            24.30238,
            56.30993,
            0.00000,
            0.00000,
            0.00000,
        )

        exp = DAF(2, 1, 5)
        exp.set_material('Si')
        exp.set_hkl((2, 0 ,3))
        calculated_pseudo_angles = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, exp.samp, exp.hkl, 1.23984, (0, 0, 1), exp.U
        )

        pseudo_angles_to_compare = {"twotheta": 48.604768720506975, "theta": 24.302384360253487, "alpha": 20.025125597165456, 
                                    "qaz": 90.0, 
                                    "naz": 53.81503362188652, "tau": 33.69009792854607, 
                                    "psi": 90.00001260507149, "beta": 20.025126994673688, "omega": -0.0}
        for key in pseudo_angles_to_compare:
            self.assertAlmostEqual(pseudo_angles_to_compare[key], calculated_pseudo_angles[key], 4)

    def test_GIVEN_mode_2023_and_hkl_123_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct(
        self,
    ):
        del_, eta, chi, phi, nu, mu = (
            50.56580,
            61.98212,
            90.00000,
            -26.56505,
            0.00000,
            0.00000,
        )

        exp = DAF(2, 0, 2, 3)
        exp.set_material('Si')
        exp.set_hkl((1, 2 ,3))
        calculated_pseudo_angles = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, exp.samp, exp.hkl, 1.23984, (0, 0, 1), exp.U
        )

        pseudo_angles_to_compare = {"twotheta": 50.56579614878003, "theta": 25.282898074390015, "alpha": 61.98212340176453, 
                                    "qaz": 90.0, 
                                    "naz": 89.99999999999999, "tau": 36.699582400990124, 
                                    "psi": 179.80995840071695, "beta": -11.416327252984509, "omega": 36.698917587899125}
        for key in pseudo_angles_to_compare:
            self.assertAlmostEqual(pseudo_angles_to_compare[key], calculated_pseudo_angles[key], 4)

    def test_GIVEN_mode_2023_and_hkl_111_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct(
        self,
    ):
        del_, eta, chi, phi, nu, mu = (
            22.80538,
            66.13830,
            90.00000,
            -45.00000,
            0.00000,
            0.00000,
        )

        exp = DAF(2, 0, 2, 3)
        exp.set_material('Si')
        exp.set_hkl((1, 1 ,1))
        exp.set_constraints(chi = 90)
        calculated_pseudo_angles = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, exp.samp, exp.hkl, 1.23984, (0, 0, 1), exp.U
        )

        pseudo_angles_to_compare = {"twotheta": 22.805375914195388, "theta": 11.402687957097694, "alpha": 66.13829805185105, 
                                    "qaz": 90.0, 
                                    "naz": 90.0, "tau": 54.735629207009254, 
                                    "psi": 179.9665911061182, "beta": -43.33292213765566, "omega": 54.735949624667434}
        for key in pseudo_angles_to_compare:
            self.assertAlmostEqual(pseudo_angles_to_compare[key], calculated_pseudo_angles[key], 4)

    def test_GIVEN_mode_2023_and_hkl_423_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct(
        self,
    ):
        del_, eta, chi, phi, nu, mu = (
            75.85801,
            94.07449,
            90.00000,
            -63.43495,
            0.00000,
            0.00000,
        )

        exp = DAF(2, 0, 2, 3)
        exp.set_material('Si')
        exp.set_hkl((4, 2 ,3))
        calculated_pseudo_angles = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, exp.samp, exp.hkl, 1.23984, (0, 0, 1), exp.U
        )

        pseudo_angles_to_compare = {"twotheta": 75.85801418311007, "theta": 37.929007091555036, "alpha": 85.92550772049013, 
                                    "qaz": 90.0, 
                                    "naz": -89.99999999999997, "tau": 56.14521021646941, 
                                    "psi": 179.94156953791418, "beta": -18.21647809639981, "omega": 56.14499166543039}
        for key in pseudo_angles_to_compare:
            self.assertAlmostEqual(pseudo_angles_to_compare[key], calculated_pseudo_angles[key], 4)

if __name__ == "__main__":
    obj = TestDAF()
    obj.test_GIVEN_diffractometer_angles_WHEN_performing_pseudo_angle_calculation_THEN_check_if_is_correct()


    