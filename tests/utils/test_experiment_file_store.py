"""
Unit tests for daf.utils.experiment_file_store module.
"""
import copy
import os
import tempfile

import pytest
import yaml

import daf.utils.generate_daf_default as gdd
from daf.config.beamline_pvs_sim import beamline_pvs
from daf.config.motors_sim_config import motors
from daf.utils.experiment_file_store import ExperimentFileStore


def valid_experiment_data():
    data = copy.deepcopy(gdd.default)
    data["motors"] = copy.deepcopy(motors)
    data["beamline_pvs"] = copy.deepcopy(beamline_pvs)
    return data


class TestExperimentFileStore:
    def test_read_returns_data(self):
        """Test that ExperimentFileStore.read parses YAML and returns a dict."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump(valid_experiment_data(), f)
            filepath = f.name

        try:
            store = ExperimentFileStore(filepath)
            result = store.read()

            assert result["Mode"] == "2052"
            assert result["Material"] == "Si"
        finally:
            os.unlink(filepath)

    def test_generated_default_experiment_passes_validation(self, tmp_path):
        """The generated default experiment shape must be loadable."""
        gdd.generate_file(
            data=valid_experiment_data(),
            file_path=str(tmp_path),
            file_name=".Experiment",
        )

        result = ExperimentFileStore(tmp_path / ".Experiment").read()

        assert result["Material"] == "Si"

    def test_write_and_read_cycle(self):
        """Test that ExperimentFileStore.write persists data and read retrieves it."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            filepath = f.name

        try:
            data = valid_experiment_data()
            data["motors"]["mu"]["value"] = 10.0
            data["beamline_pvs"]["energy"]["value"] = 8000

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
        original_data = valid_experiment_data()
        filepath.write_text(yaml.dump(original_data))

        store = ExperimentFileStore(filepath)
        new_data = valid_experiment_data()
        new_data["Mode"] = "400"
        new_data["Material"] = "Ge"
        store.write(new_data)

        result = store.read()
        assert result["Mode"] == "400"
        assert result["Material"] == "Ge"

    def test_only_read_static_method(self):
        """Test only_read static method reads file without instantiation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.dump(valid_experiment_data(), f)
            filepath = f.name

        try:
            result = ExperimentFileStore.only_read(filepath)
            assert result["Material"] == "Si"
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
            data = valid_experiment_data()
            data["motors"]["mu"]["value"] = 50.0
            data["motors"]["mu"]["bounds"] = [-10, 10]
            data["motors"]["mu"]["up"] = False
            data["beamline_pvs"]["energy"]["value"] = 8000
            data["beamline_pvs"]["energy"]["up"] = False

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
        original_data = valid_experiment_data()
        original_data["Mode"] = "215"
        filepath.write_text(yaml.dump(original_data))

        def fail_dump(data, file):
            file.write("Mode: ")
            raise OSError("simulated write failure")

        monkeypatch.setattr(yaml, "dump", fail_dump)

        store = ExperimentFileStore(filepath)

        with pytest.raises(OSError, match="simulated write failure"):
            store.write({"Mode": 400, "Material": "Ge"})

        assert store.read()["Mode"] == "215"

    def test_read_rejects_experiment_missing_required_key(self, tmp_path):
        """A loaded experiment file must fail fast when a required key is absent."""
        filepath = tmp_path / ".Experiment"
        data = valid_experiment_data()
        del data["Material"]
        filepath.write_text(yaml.dump(data))

        store = ExperimentFileStore(filepath)

        with pytest.raises(ValueError, match="Material"):
            store.read()

    def test_read_rejects_motor_with_wrong_shaped_bounds(self, tmp_path):
        """Nested motor validation names the invalid field path."""
        filepath = tmp_path / ".Experiment"
        data = valid_experiment_data()
        data["motors"]["mu"]["bounds"] = [-10.0]
        filepath.write_text(yaml.dump(data))

        store = ExperimentFileStore(filepath)

        with pytest.raises(ValueError, match="motors.mu.bounds"):
            store.read()
