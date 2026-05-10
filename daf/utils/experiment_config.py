"""Typed access to DAF experiment configuration dictionaries."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

import numpy as np


MOTOR_NAMES: tuple[str, ...] = ("mu", "eta", "chi", "phi", "nu", "del")

CONSTRAINT_KEYS: tuple[str, ...] = (
    "cons_mu",
    "cons_eta",
    "cons_chi",
    "cons_phi",
    "cons_nu",
    "cons_del",
    "cons_alpha",
    "cons_beta",
    "cons_psi",
    "cons_omega",
    "cons_qaz",
    "cons_naz",
)


@dataclass(frozen=True)
class ExperimentConfig:
    """Named domain view over the raw ``.Experiment`` YAML dictionary."""

    raw: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentConfig":
        return cls(copy.deepcopy(data))

    @property
    def mode(self) -> tuple[int, ...]:
        mode_val = self.raw["Mode"]
        if isinstance(mode_val, str):
            return tuple(int(ch) for ch in mode_val)
        return tuple(int(i) for i in mode_val)

    @property
    def material(self) -> str:
        return self.raw["Material"]

    @property
    def idir(self) -> list[float]:
        return self.raw["IDir_print"]

    @property
    def ndir(self) -> list[float]:
        return self.raw["NDir_print"]

    @property
    def rdir(self) -> list[float]:
        return self.raw["RDir"]

    @property
    def sample_orientation(self) -> str:
        return self.raw["Sampleor"]

    @property
    def energy(self) -> float:
        return float(
            self.raw["beamline_pvs"]["energy"]["value"] - self.raw["energy_offset"]
        )

    @property
    def u_matrix(self) -> np.ndarray:
        return np.array(self.raw["U_mat"])

    @property
    def motor_values(self) -> dict[str, float]:
        return {motor: self.raw["motors"][motor]["value"] for motor in MOTOR_NAMES}

    @property
    def motor_bounds(self) -> dict[str, list[float]]:
        return {motor: self.raw["motors"][motor]["bounds"] for motor in MOTOR_NAMES}

    @property
    def constraints(self) -> dict[str, Any]:
        return {key: self.raw[key] for key in CONSTRAINT_KEYS}

    @property
    def user_samples(self) -> dict[str, list[float]]:
        return self.raw.get("user_samples", {})

    @property
    def lattice_parameters(self) -> tuple[float, float, float, float, float, float]:
        return (
            self.raw["lparam_a"],
            self.raw["lparam_b"],
            self.raw["lparam_c"],
            self.raw["lparam_alpha"],
            self.raw["lparam_beta"],
            self.raw["lparam_gama"],
        )

    def with_motor_setpoints(self, values: dict[str, Any]) -> dict[str, Any]:
        data = copy.deepcopy(self.raw)
        for motor in data["motors"]:
            if motor in values and values[motor] is not None:
                data["motors"][motor]["value"] = float(values[motor])
        return data

    def with_motor_bounds(self, values: dict[str, Any]) -> dict[str, Any]:
        data = copy.deepcopy(self.raw)
        for motor in data["motors"]:
            if motor in values and values[motor] is not None:
                data["motors"][motor]["bounds"] = values[motor]
        return data
