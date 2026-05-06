#!/usr/bin/env python3
"""Pure YAML persistence for experiment files."""
from __future__ import annotations

import pathlib
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
        """Write the experiment dict to the YAML file."""
        with self.filepath.open("w") as file:
            yaml.dump(data, file)
            file.flush()

    @staticmethod
    def only_read(filepath: str | pathlib.Path | None = None) -> dict[str, Any]:
        """Read the experiment YAML file without instantiating the store."""
        path = pathlib.Path(filepath if filepath is not None else _default_path())
        with path.open() as file:
            return yaml.safe_load(file)
