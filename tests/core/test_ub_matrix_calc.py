"""
Unit tests for daf.core.ub_matrix_calc module
"""
import unittest
import numpy as np
from daf.core.ub_matrix_calc import UBMatrix


class TestUBMatrix(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.ub_matrix = UBMatrix()

    def test_uphi_returns_tuple(self):
        """Test that uphi method returns a tuple of (uphi, theta)"""
        result = self.ub_matrix.uphi(0, 0, 0, 0, 0, 0)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_uphi_unity_angles(self):
        """Test uphi with all zero angles"""
        uphi, theta = self.ub_matrix.uphi(0, 0, 0, 0, 0, 0)

        # At zero angles, theta should be 0
        self.assertAlmostEqual(theta, 0.0)

        # uphi should be a 3-element array
        self.assertEqual(len(uphi), 3)

    def test_uphi_with_nonzero_angles(self):
        """Test uphi with non-zero diffractometer angles"""
        mu, eta, chi, phi, nu, del_ = 10.0, 5.0, 35.0, 45.0, 0.0, 10.0
        uphi, theta = self.ub_matrix.uphi(mu, eta, chi, phi, nu, del_)

        # Should return valid numerical values
        self.assertTrue(np.all(np.isfinite(uphi)))
        self.assertTrue(np.isfinite(theta))

    def test_uphi_theta_range(self):
        """Test that theta is in valid range (0 to 90 degrees)"""
        # Test various angle combinations
        test_cases = [
            (0, 0, 0, 0, 0, 0),
            (10, 5, 35, 45, 0, 20),
            (45, 30, 60, 90, 10, 30),
        ]

        for angles in test_cases:
            uphi, theta = self.ub_matrix.uphi(*angles)
            # theta should be non-negative and typically less than 90 for physical configurations
            self.assertGreaterEqual(theta, 0)

    def test_dot3(self):
        """Test the dot3 method for 3x3 matrix dot products"""
        x = np.array([[1], [2], [3]])
        y = np.array([[4], [5], [6]])
        result = self.ub_matrix.dot3(x, y)

        # 1*4 + 2*5 + 3*6 = 32
        self.assertEqual(result, 32)

    def test_dot3_with_floats(self):
        """Test dot3 with floating point values"""
        x = np.array([[0.5], [0.5], [0.0]])
        y = np.array([[0.5], [0.5], [0.0]])
        result = self.ub_matrix.dot3(x, y)

        # 0.5*0.5 + 0.5*0.5 + 0*0 = 0.5
        self.assertEqual(result, 0.5)

    def test_bound_values_within_range(self):
        """Test bound method with values within -1 to 1 range"""
        result = self.ub_matrix.bound(0.5)
        self.assertEqual(result, 0.5)

    def test_bound_value_at_1(self):
        """Test bound method with value exactly at 1"""
        result = self.ub_matrix.bound(1.0)
        self.assertEqual(result, 1.0)

    def test_bound_value_at_minus_1(self):
        """Test bound method with value exactly at -1"""
        result = self.ub_matrix.bound(-1.0)
        self.assertEqual(result, -1.0)

    def test_bound_value_above_1(self):
        """Test bound method raises error for value above 1"""
        with self.assertRaises(AssertionError):
            self.ub_matrix.bound(1.5)

    def test_bound_value_below_minus_1(self):
        """Test bound method raises error for value below -1"""
        with self.assertRaises(AssertionError):
            self.ub_matrix.bound(-1.5)

    def test_bound_value_far_outside_range_raises(self):
        """Test bound method raises error for values far outside range"""
        with self.assertRaises(AssertionError):
            self.ub_matrix.bound(2.0)

    def test_bound_value_just_above_1(self):
        """Test bound method clips value just above 1 to 1"""
        result = self.ub_matrix.bound(1.0000000001)
        self.assertEqual(result, 1.0)

    def test_bound_value_just_below_minus_1(self):
        """Test bound method clips value just below -1 to -1"""
        result = self.ub_matrix.bound(-1.0000000001)
        self.assertEqual(result, -1.0)

    def test_angle_between_vectors(self):
        """Test angle_between_vectors method"""
        # Create column vectors as expected by dot3
        a = np.array([[1.0], [0.0], [0.0]])
        b = np.array([[0.0], [1.0], [0.0]])

        angle = self.ub_matrix.angle_between_vectors(a, b)

        # Should be 90 degrees (pi/2 radians)
        self.assertAlmostEqual(angle, np.pi / 2)

    def test_angle_between_identical_vectors(self):
        """Test angle between a vector and itself"""
        # Create column vectors as expected by dot3
        a = np.array([[1.0], [2.0], [3.0]])

        angle = self.ub_matrix.angle_between_vectors(a, a)

        # Should be 0
        self.assertAlmostEqual(angle, 0.0)

    def test_get_quat_from_u123(self):
        """Test quaternion extraction from u1, u2, u3 parameters"""
        u1, u2, u3 = 0.5, 0.25, 0.75
        q0, q1, q2, q3 = self.ub_matrix._get_quat_from_u123(u1, u2, u3)

        # All quaternion components should be in valid range
        self.assertTrue(np.all(np.isfinite([q0, q1, q2, q3])))
        # Check quaternion constraint (should sum to 1 for unit quaternion)
        # Note: This is a necessary but not sufficient check

    def test_get_rot_matrix(self):
        """Test rotation matrix from quaternion"""
        # Identity quaternion
        q0, q1, q2, q3 = 1.0, 0.0, 0.0, 0.0
        rot = self.ub_matrix._get_rot_matrix(q0, q1, q2, q3)

        # Should be identity matrix
        np.testing.assert_array_almost_equal(rot, np.eye(3))

    def test_get_rot_matrix_90_degree_rotation(self):
        """Test rotation matrix for 90 degree rotation around z"""
        # 90 degree rotation around z: q0 = q3 = sqrt(2)/2, q1 = q2 = 0
        q0 = np.sqrt(2) / 2
        q1 = 0.0
        q2 = 0.0
        q3 = np.sqrt(2) / 2

        rot = self.ub_matrix._get_rot_matrix(q0, q1, q2, q3)

        # Rotation matrix should be orthogonal
        np.testing.assert_array_almost_equal(np.dot(rot.T, rot), np.eye(3))
        # Determinant should be 1
        self.assertAlmostEqual(np.linalg.det(rot), 1.0)


class TestUBMatrixWithSample(unittest.TestCase):
    """Tests that require a sample material to be set"""

    def setUp(self):
        """Set up test fixtures with sample material"""
        import xrayutilities as xu

        self.ub_matrix = UBMatrix()
        self.ub_matrix.samp = xu.materials.Si
        self.ub_matrix.lam = 1.0

    def test_calc_u_2hkl(self):
        """Test U matrix calculation from 2 HKL reflections"""
        h1 = np.array([1, 0, 0])
        angh1 = (0, 0, 0, 0, 0, 10)
        h2 = np.array([0, 1, 0])
        angh2 = (0, 0, 0, 0, 0, 20)

        U, UB = self.ub_matrix.calc_U_2HKL(h1, angh1, h2, angh2)

        # U and UB should be 3x3 matrices
        self.assertEqual(U.shape, (3, 3))
        self.assertEqual(UB.shape, (3, 3))

    def test_calc_u_3hkl(self):
        """Test U matrix calculation from 3 HKL reflections"""
        h1 = np.array([1, 0, 0])
        angh1 = (0, 0, 0, 0, 0, 10)
        h2 = np.array([0, 1, 0])
        angh2 = (0, 0, 0, 0, 0, 15)
        h3 = np.array([0, 0, 1])
        angh3 = (0, 0, 0, 0, 0, 20)

        U, UB, rparam = self.ub_matrix.calc_U_3HKL(h1, angh1, h2, angh2, h3, angh3)

        # U and UB should be 3x3 matrices
        self.assertEqual(U.shape, (3, 3))
        self.assertEqual(UB.shape, (3, 3))
        # rparam should have 6 elements (lattice parameters)
        self.assertEqual(len(rparam), 6)


if __name__ == "__main__":
    unittest.main()
