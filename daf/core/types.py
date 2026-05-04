from dataclasses import dataclass

import numpy as np


@dataclass
class RotationMatrices:
    mu: np.ndarray
    eta: np.ndarray
    chi: np.ndarray
    phi: np.ndarray
    nu: np.ndarray
    del_: np.ndarray


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


@dataclass
class MotorAngles:
    mu: float
    eta: float
    chi: float
    phi: float
    nu: float
    del_: float
