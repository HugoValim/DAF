#!/usr/bin/env python3
"""Pure YAML persistence for experiment files."""
from __future__ import annotations

import os
import pathlib
import tempfile
from typing import Any

import yaml

from daf.utils.daf_paths import DAFPaths as dp


def _default_path() -> pathlib.Path:
    """Resolve the default experiment file path."""
    return dp.check_for_local_config()


class ExperimentFileStore:
    """Handles read/write of .Experiment YAML files without EPICS side effects."""

    def __init__(self, filepath: str | pathlib.Path | None = None) -> None:
        self.filepath: pathlib.Path = pathlib.Path(
            filepath if filepath is not None else _default_path()
        )

    def read(self) -> dict[str, Any]:
        """Read and parse the experiment YAML file."""
        with self.filepath.open() as file:
            return yaml.safe_load(file)

    def write(self, data: dict[str, Any]) -> None:
        """Write the experiment dict to the YAML file atomically."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        temp_path: pathlib.Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=self.filepath.parent,
                prefix=f".{self.filepath.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temp_path = pathlib.Path(file.name)
                yaml.dump(data, file)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temp_path, self.filepath)
        except Exception:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def only_read(filepath: str | pathlib.Path | None = None) -> dict[str, Any]:
        """Read the experiment YAML file without instantiating the store."""
        path = pathlib.Path(filepath if filepath is not None else _default_path())
        with path.open() as file:
            return yaml.safe_load(file)
