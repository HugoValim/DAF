"""
Unit tests for daf.core.math_utils module
"""
import unittest
import numpy as np
from daf.core.math_utils import unit_vector, vector_angle, vec_norm


class TestMathUtils(unittest.TestCase):

    def test_unit_vector_1d(self):
        """Test unit_vector with 1D array"""
        v = np.array([3.0, 4.0, 0.0])
        expected = np.array([0.6, 0.8, 0.0])
        result = unit_vector(v)
        np.testing.assert_array_almost_equal(result, expected)

    def test_unit_vector_2d(self):
        """Test unit_vector with 2D array"""
        v = np.array([1.0, 1.0, 1.0])
        expected = np.array([1/np.sqrt(3), 1/np.sqrt(3), 1/np.sqrt(3)])
        result = unit_vector(v)
        np.testing.assert_array_almost_equal(result, expected)

    def test_unit_vector_zeros(self):
        """Test unit_vector with zero vector - numpy returns NaN for 0/0"""
        v = np.array([0.0, 0.0, 0.0])
        result = unit_vector(v)
        # numpy returns [nan, nan, nan] for 0/0
        self.assertTrue(np.all(np.isnan(result)))

    def test_vector_angle_perpendicular(self):
        """Test angle between perpendicular vectors"""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        result = vector_angle(v1, v2)
        self.assertAlmostEqual(result, np.pi/2)

    def test_vector_angle_parallel(self):
        """Test angle between parallel vectors"""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([2.0, 0.0, 0.0])
        result = vector_angle(v1, v2)
        self.assertAlmostEqual(result, 0.0)

    def test_vector_angle_opposite(self):
        """Test angle between opposite vectors"""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([-1.0, 0.0, 0.0])
        result = vector_angle(v1, v2)
        self.assertAlmostEqual(result, np.pi)

    def test_vector_angle_degrees(self):
        """Test vector_angle with deg=True"""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        result = vector_angle(v1, v2, deg=True)
        self.assertAlmostEqual(result, 90.0)

    def test_vector_angle_radians(self):
        """Test vector_angle returns radians by default"""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        result = vector_angle(v1, v2, deg=False)
        self.assertAlmostEqual(result, np.pi/2)

    def test_vec_norm_single_vector(self):
        """Test vec_norm with a single 3D vector"""
        v = [3.0, 4.0, 0.0]
        result = vec_norm(v)
        self.assertAlmostEqual(result, 5.0)

    def test_vec_norm_array_of_vectors(self):
        """Test vec_norm with array of vectors"""
        v = np.array([[3.0, 4.0, 0.0], [0.0, 0.0, 5.0]])
        result = vec_norm(v)
        expected = np.array([5.0, 5.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_vec_norm_invalid_length(self):
        """Test vec_norm raises error for invalid vector length"""
        v = [1.0, 2.0]  # Not length 3
        with self.assertRaises(ValueError):
            vec_norm(v)

    def test_vector_angle_45_degrees(self):
        """Test vector angle at 45 degrees"""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 1.0, 0.0])
        result = vector_angle(v1, v2, deg=True)
        self.assertAlmostEqual(result, 45.0, places=5)

    def test_vector_angle_with_negative_components(self):
        """Test vector angle with negative vector components"""
        v1 = np.array([1.0, 1.0, 0.0])
        v2 = np.array([-1.0, 1.0, 0.0])
        result = vector_angle(v1, v2, deg=True)
        self.assertAlmostEqual(result, 90.0, places=5)


if __name__ == '__main__':
    unittest.main()
