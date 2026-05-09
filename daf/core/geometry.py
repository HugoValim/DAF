"""Diffractometer geometry inputs for pseudo angle calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class DiffractometerGeometry:
    motor_angles: tuple[float, float, float, float, float, float]
    sample: Any
    hkl: np.ndarray
    wave_length: float
    reference_direction: np.ndarray
    u_matrix: np.ndarray
