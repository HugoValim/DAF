from dataclasses import dataclass, fields
from typing import Any

import numpy as np


@dataclass
class RotationMatrices:
    mu: np.ndarray
    eta: np.ndarray
    chi: np.ndarray
    phi: np.ndarray
    nu: np.ndarray
    del_: np.ndarray

    def __getitem__(self, key: str) -> np.ndarray:
        return getattr(self, "del_" if key == "del" else key)

    def keys(self) -> list[str]:
        return ["mu", "eta", "chi", "phi", "nu", "del"]


@dataclass
class PseudoAngles:
    twotheta: float
    theta: float
    alpha: float
    qaz: float
    naz: float
    tau: float
    psi: float
    beta: float
    omega: float
    q_vector: np.ndarray
    q_vector_norm: float

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def keys(self) -> list[str]:
        return [f.name for f in fields(self)]


@dataclass
class MotorAngles:
    mu: float
    eta: float
    chi: float
    phi: float
    nu: float
    del_: float
