"""
Unit tests for daf.utils.experiment_file_store module.
"""
import os
import tempfile

import pytest
import yaml

from daf.utils.experiment_file_store import ExperimentFileStore


class TestExperimentFileStore:
    def test_read_returns_data(self):
        """Test that ExperimentFileStore.read parses YAML and returns a dict."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump({"key": "value", "number": 42}, f)
            filepath = f.name

        try:
            store = ExperimentFileStore(filepath)
            result = store.read()

            assert result["key"] == "value"
            assert result["number"] == 42
        finally:
            os.unlink(filepath)

    def test_write_and_read_cycle(self):
        """Test that ExperimentFileStore.write persists data and read retrieves it."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            filepath = f.name

        try:
            data = {
                "motors": {
                    "mu": {
                        "pv": "test:mu",
                        "value": 10.0,
                        "bounds": [-180, 180],
                        "up": True,
                    }
                },
                "beamline_pvs": {
                    "energy": {
                        "pv": "test:energy",
                        "value": 8000,
                        "up": True,
                        "simulated": False,
                    }
                },
            }

            store = ExperimentFileStore(filepath)
            store.write(data)

            result = store.read()
            assert result["motors"]["mu"]["value"] == 10.0
            assert result["beamline_pvs"]["energy"]["value"] == 8000
        finally:
            os.unlink(filepath)

    def test_write_replaces_existing_file_with_readable_yaml(self, tmp_path):
        """Writing over an existing experiment file leaves readable YAML."""
        filepath = tmp_path / ".Experiment"
        filepath.write_text("Mode: 215\nMaterial: Si\n")

        store = ExperimentFileStore(filepath)
        store.write({"Mode": 400, "Material": "Ge"})

        assert store.read() == {"Mode": 400, "Material": "Ge"}

    def test_only_read_static_method(self):
        """Test only_read static method reads file without instantiation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump({"test": "data"}, f)
            filepath = f.name

        try:
            result = ExperimentFileStore.only_read(filepath)
            assert result["test"] == "data"
        finally:
            os.unlink(filepath)

    def test_write_does_not_zero_offline_motors_implicitly(self):
        """Test that the file store does NOT silently mutate offline motors.

        The offline-motor zeroing policy must live at the seam (DAFIO),
        not be hidden inside the persistence layer.
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            filepath = f.name

        try:
            data = {
                "motors": {"mu": {"value": 50.0, "bounds": [-10, 10], "up": False}},
                "beamline_pvs": {"energy": {"value": 8000, "up": False}},
            }

            store = ExperimentFileStore(filepath)
            store.write(data)

            result = store.read()
            # Persistence layer must NOT touch values
            assert result["motors"]["mu"]["value"] == 50.0
            assert result["motors"]["mu"]["bounds"] == [-10, 10]
            assert result["beamline_pvs"]["energy"]["value"] == 8000
        finally:
            os.unlink(filepath)

    def test_failed_write_keeps_previous_contents(self, tmp_path, monkeypatch):
        """A failed write must not leave a truncated experiment file behind."""
        filepath = tmp_path / ".Experiment"
        filepath.write_text("Mode: 215\nMaterial: Si\n")

        def fail_dump(data, file):
            file.write("Mode: ")
            raise OSError("simulated write failure")

        monkeypatch.setattr(yaml, "dump", fail_dump)

        store = ExperimentFileStore(filepath)

        with pytest.raises(OSError, match="simulated write failure"):
            store.write({"Mode": 400, "Material": "Ge"})

        assert store.read() == {"Mode": 215, "Material": "Si"}
