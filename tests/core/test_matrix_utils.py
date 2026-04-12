"""
Unit tests for daf.core.matrix_utils module
"""
import unittest
import numpy as np
from daf.core.matrix_utils import (
    calculate_rotation_matrix_from_diffractometer_angles,
    calculate_pseudo_angle_from_motor_angles,
)


class TestMatrixUtils(unittest.TestCase):
    def test_rotation_matrices_unity_angles(self):
        """Test rotation matrices with all zero angles"""
        result = calculate_rotation_matrix_from_diffractometer_angles(0, 0, 0, 0, 0, 0)

        # Identity matrix for all rotations at 0 degrees
        identity = np.eye(3)
        for key in ["mu", "eta", "chi", "phi", "nu", "del"]:
            np.testing.assert_array_almost_equal(result[key], identity)

    def test_rotation_matrices_mu_only(self):
        """Test rotation matrix with only Mu angle"""
        mu = 45.0
        eta, chi, phi, nu, del_ = 0, 0, 0, 0, 0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            mu, eta, chi, phi, nu, del_
        )

        # Check Mu rotation (rotation around x-axis)
        expected_mu = np.array(
            [
                [1, 0, 0],
                [0, np.cos(np.deg2rad(mu)), -np.sin(np.deg2rad(mu))],
                [0, np.sin(np.deg2rad(mu)), np.cos(np.deg2rad(mu))],
            ]
        )
        np.testing.assert_array_almost_equal(result["mu"], expected_mu)

    def test_rotation_matrices_eta_only(self):
        """Test rotation matrix with only Eta angle"""
        eta = 30.0
        mu, chi, phi, nu, del_ = 0, 0, 0, 0, 0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            mu, eta, chi, phi, nu, del_
        )

        # Check Eta rotation (rotation around z-axis)
        expected_eta = np.array(
            [
                [np.cos(np.deg2rad(eta)), np.sin(np.deg2rad(eta)), 0],
                [-np.sin(np.deg2rad(eta)), np.cos(np.deg2rad(eta)), 0],
                [0, 0, 1],
            ]
        )
        np.testing.assert_array_almost_equal(result["eta"], expected_eta)

    def test_rotation_matrices_chi_only(self):
        """Test rotation matrix with only Chi angle"""
        chi = 90.0
        mu, eta, phi, nu, del_ = 0, 0, 0, 0, 0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            mu, eta, chi, phi, nu, del_
        )

        # Check Chi rotation (rotation around x-axis)
        expected_chi = np.array(
            [
                [np.cos(np.deg2rad(chi)), 0, np.sin(np.deg2rad(chi))],
                [0, 1, 0],
                [-np.sin(np.deg2rad(chi)), 0, np.cos(np.deg2rad(chi))],
            ]
        )
        np.testing.assert_array_almost_equal(result["chi"], expected_chi)

    def test_rotation_matrices_phi_only(self):
        """Test rotation matrix with only Phi angle"""
        phi = 90.0
        mu, eta, chi, nu, del_ = 0, 0, 0, 0, 0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            mu, eta, chi, phi, nu, del_
        )

        # Check Phi rotation (rotation around z-axis)
        expected_phi = np.array(
            [
                [np.cos(np.deg2rad(phi)), np.sin(np.deg2rad(phi)), 0],
                [-np.sin(np.deg2rad(phi)), np.cos(np.deg2rad(phi)), 0],
                [0, 0, 1],
            ]
        )
        np.testing.assert_array_almost_equal(result["phi"], expected_phi)

    def test_rotation_matrices_nu_only(self):
        """Test rotation matrix with only Nu angle"""
        nu = 45.0
        mu, eta, chi, phi, del_ = 0, 0, 0, 0, 0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            mu, eta, chi, phi, nu, del_
        )

        # Check Nu rotation (rotation around x-axis)
        expected_nu = np.array(
            [
                [1, 0, 0],
                [0, np.cos(np.deg2rad(nu)), -np.sin(np.deg2rad(nu))],
                [0, np.sin(np.deg2rad(nu)), np.cos(np.deg2rad(nu))],
            ]
        )
        np.testing.assert_array_almost_equal(result["nu"], expected_nu)

    def test_rotation_matrices_del_only(self):
        """Test rotation matrix with only Del angle"""
        del_ = 30.0
        mu, eta, chi, phi, nu = 0, 0, 0, 0, 0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            mu, eta, chi, phi, nu, del_
        )

        # Check Del rotation (rotation around z-axis)
        expected_del = np.array(
            [
                [np.cos(np.deg2rad(del_)), np.sin(np.deg2rad(del_)), 0],
                [-np.sin(np.deg2rad(del_)), np.cos(np.deg2rad(del_)), 0],
                [0, 0, 1],
            ]
        )
        np.testing.assert_array_almost_equal(result["del"], expected_del)

    def test_rotation_matrices_all_same_angle(self):
        """Test rotation matrices with all same non-zero angle"""
        angle = 10.0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            angle, angle, angle, angle, angle, angle
        )

        # All matrices should be different since rotations are around different axes
        # Just verify they all have correct shape and determinant = 1 (rotation matrices)
        for key in ["mu", "eta", "chi", "phi", "nu", "del"]:
            self.assertEqual(result[key].shape, (3, 3))
            self.assertAlmostEqual(np.linalg.det(result[key]), 1.0, places=5)

    def test_rotation_matrix_orthogonality(self):
        """Test that rotation matrices are orthogonal (R^T R = I)"""
        angle = 45.0
        result = calculate_rotation_matrix_from_diffractometer_angles(
            angle, angle, angle, angle, angle, angle
        )

        for key in ["mu", "eta", "chi", "phi", "nu", "del"]:
            r = result[key]
            rt_r = np.dot(r.T, r)
            identity = np.eye(3)
            np.testing.assert_array_almost_equal(rt_r, identity, decimal=5)

    def test_pseudo_angle_structure(self):
        """Test that pseudo angle calculation returns expected keys"""
        import xrayutilities as xu

        mu, eta, chi, phi, nu, del_ = (
            10.73240,
            5.36620,
            35.26439,
            45.00000,
            0.00000,
            0.00000,
        )
        sample = xu.materials.Si
        hkl = np.array([1, 1, 1])
        wave_length = 0.58649
        rdir = np.array([0, 0, 1])
        U = np.eye(3)

        result = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, sample, hkl, wave_length, rdir, U
        )

        expected_keys = {
            "alpha",
            "qaz",
            "naz",
            "tau",
            "psi",
            "beta",
            "omega",
            "twotheta",
            "theta",
            "q_vector",
            "q_vector_norm",
        }
        self.assertEqual(set(result.keys()), expected_keys)


class TestPseudoAngleCalculation(unittest.TestCase):
    """Tests for pseudo angle calculations with specific HKL positions"""

    def test_pseudo_angles_at_000(self):
        """Test pseudo angles at origin HKL (0, 0, 0)"""
        import xrayutilities as xu

        mu, eta, chi, phi, nu, del_ = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        sample = xu.materials.Si
        hkl = np.array([0, 0, 0])
        wave_length = 1.0
        rdir = np.array([0, 0, 1])
        U = np.eye(3)

        result = calculate_pseudo_angle_from_motor_angles(
            mu, eta, chi, phi, nu, del_, sample, hkl, wave_length, rdir, U
        )

        # At HKL 000, q_vector should be zero
        self.assertAlmostEqual(result["q_vector_norm"], 0.0)


if __name__ == "__main__":
    unittest.main()
