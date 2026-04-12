"""
Unit tests for daf.utils.experiment_configs module
"""
import unittest
from daf.utils.experiment_configs import samples, Hi


class TestSamples(unittest.TestCase):
    def test_samples_is_dict(self):
        """Test that samples is a dictionary"""
        self.assertIsInstance(samples, dict)

    def test_samples_contains_common_materials(self):
        """Test that common materials are present"""
        common_materials = ["Si", "Ge", "Cu", "Al", "Fe", "Au", "Ag"]
        for material in common_materials:
            self.assertIn(material, samples)

    def test_samples_si_is_xray_material(self):
        """Test that Si sample is from xrayutilities"""
        si = samples["Si"]
        self.assertTrue(hasattr(si, "a"))  # Should have lattice parameter 'a'
        self.assertTrue(hasattr(si, "b"))
        self.assertTrue(hasattr(si, "c"))

    def test_samples_all_have_name(self):
        """Test that all samples have a name attribute"""
        for name, sample in samples.items():
            self.assertTrue(
                hasattr(sample, "name"), f"Sample {name} missing 'name' attribute"
            )

    def test_samples_all_have_lattice_params(self):
        """Test that all samples have lattice parameters"""
        for name, sample in samples.items():
            # All crystals should have a, b, c lattice parameters
            self.assertTrue(hasattr(sample, "a"))
            self.assertTrue(hasattr(sample, "b"))
            self.assertTrue(hasattr(sample, "c"))

    def test_some_samples_have_alpha_beta_gamma(self):
        """Test that some samples have non-90 degree angles (triclinic/monoclinic)"""
        # Si has cubic structure with all 90 degree angles
        si = samples["Si"]
        self.assertEqual(si.alpha, 90)
        self.assertEqual(si.beta, 90)
        self.assertEqual(si.gamma, 90)

    def test_gaas_has_correct_lattice_constant(self):
        """Test GaAs has zincblende structure"""
        gaas = samples["GaAs"]
        # GaAs lattice constant is approximately 5.65 Angstrom
        self.assertAlmostEqual(gaas.a, 5.65, places=1)

    def test_si_has_correct_lattice_constant(self):
        """Test Si has correct lattice constant"""
        si = samples["Si"]
        # Si lattice constant is approximately 5.43 Angstrom
        self.assertAlmostEqual(si.a, 5.43, places=1)

    def test_number_of_samples(self):
        """Test that there are expected number of samples"""
        # Should have at least 50 predefined samples
        self.assertGreater(len(samples), 50)


class TestHiDataclass(unittest.TestCase):
    def test_hi_default_one(self):
        """Test default value of 'one' attribute"""
        hi = Hi()
        self.assertEqual(hi.one, "oioi")

    def test_hi_default_two(self):
        """Test default value of 'two' attribute"""
        hi = Hi()
        self.assertEqual(hi.two, "oi")

    def test_hi_custom_values(self):
        """Test Hi with custom values"""
        hi = Hi(one="hello", two="world")
        self.assertEqual(hi.one, "hello")
        self.assertEqual(hi.two, "world")


if __name__ == "__main__":
    unittest.main()
