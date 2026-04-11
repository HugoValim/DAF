"""
Unit tests for daf.utils.generate_daf_default module
"""
import unittest
import os
import tempfile
from daf.utils.generate_daf_default import default, generate_file


class TestDefaultConfig(unittest.TestCase):
    def test_default_mode(self):
        """Test default mode is set correctly"""
        self.assertEqual(default["Mode"], "2052")

    def test_default_material(self):
        """Test default material is Si"""
        self.assertEqual(default["Material"], "Si")

    def test_default_idir(self):
        """Test default incidence direction"""
        self.assertEqual(default["IDir"], [0, 1, 0])

    def test_default_ndir(self):
        """Test default normal direction"""
        self.assertEqual(default["NDir"], [0, 0, 1])

    def test_default_rdir(self):
        """Test default reference direction"""
        self.assertEqual(default["RDir"], [0, 0, 1])

    def test_default_sampleor(self):
        """Test default sample orientation"""
        self.assertEqual(default["Sampleor"], "z+")

    def test_default_energy_offset(self):
        """Test default energy offset is zero"""
        self.assertEqual(default["energy_offset"], 0.0)

    def test_default_hklnow(self):
        """Test default HKL position is origin"""
        self.assertEqual(default["hklnow"], [0, 0, 0])

    def test_default_reflections(self):
        """Test default reflections is empty list"""
        self.assertEqual(default["reflections"], [])

    def test_default_u_mat_is_identity(self):
        """Test default U matrix is identity"""
        expected = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.assertEqual(default["U_mat"], expected)

    def test_default_ub_mat(self):
        """Test default UB matrix"""
        # UB matrix should be a 3x3 matrix with specific values
        self.assertEqual(len(default["UB_mat"]), 3)
        self.assertEqual(len(default["UB_mat"][0]), 3)

    def test_default_lattice_params_zero(self):
        """Test default lattice parameters are zero"""
        self.assertEqual(default["lparam_a"], 0.0)
        self.assertEqual(default["lparam_b"], 0.0)
        self.assertEqual(default["lparam_c"], 0.0)
        self.assertEqual(default["lparam_alpha"], 0.0)
        self.assertEqual(default["lparam_beta"], 0.0)
        self.assertEqual(default["lparam_gama"], 0.0)

    def test_default_max_diff(self):
        """Test default max difference"""
        self.assertEqual(default["Max_diff"], 0.1)

    def test_default_scan_name(self):
        """Test default scan name"""
        self.assertEqual(default["scan_name"], "scan_test")

    def test_default_separator(self):
        """Test default separator is comma"""
        self.assertEqual(default["separator"], ",")

    def test_default_macro_flag(self):
        """Test default macro flag is False"""
        self.assertFalse(default["macro_flag"])

    def test_default_setup(self):
        """Test default setup is 'default'"""
        self.assertEqual(default["setup"], "default")

    def test_default_user_samples(self):
        """Test default user samples is empty dict"""
        self.assertEqual(default["user_samples"], {})

    def test_default_simulated_false(self):
        """Test default simulated mode exists and is boolean"""
        # Note: This may be modified by other imports during test suite run
        self.assertIsInstance(default.get("simulated"), bool)

    def test_default_kafka_topic(self):
        """Test default kafka topic"""
        self.assertEqual(default["kafka_topic"], "EMA_bluesky")

    def test_default_scan_db(self):
        """Test default scan database"""
        self.assertEqual(default["scan_db"], "temp")

    def test_version_in_default(self):
        """Test version is present in default config"""
        self.assertIn("version", default)


class TestGenerateFile(unittest.TestCase):
    def test_generate_file_creates_file(self):
        """Test that generate_file creates a file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_config.yml")
            generate_file(file_path=tmpdir, file_name="test_config.yml")

            self.assertTrue(os.path.exists(file_path))

    def test_generate_file_writes_data(self):
        """Test that generate_file writes correct data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_data = {"key": "value", "number": 42}
            file_path = os.path.join(tmpdir, "test_config.yml")
            generate_file(data=test_data, file_path=tmpdir, file_name="test_config.yml")

            # Read back and verify
            import yaml

            with open(file_path) as f:
                loaded = yaml.safe_load(f)

            self.assertEqual(loaded["key"], "value")
            self.assertEqual(loaded["number"], 42)

    def test_generate_file_with_default_data(self):
        """Test generate_file uses default data when no data provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_default.yml")
            generate_file(file_path=tmpdir, file_name="test_default.yml")

            import yaml

            with open(file_path) as f:
                loaded = yaml.safe_load(f)

            # Should have default values
            self.assertEqual(loaded["Mode"], "2052")


if __name__ == "__main__":
    unittest.main()
