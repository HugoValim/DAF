#!/usr/bin/env python3
"""Reciprocal space geometry for diffraction experiments.

This module contains only pure Bragg-peak geometry (math that computes
peak positions).  All matplotlib canvas, interactive callbacks, and
subprocess spawning live in ``daf.core.reciprocal_map_plot``.
"""
from __future__ import annotations

import logging
import math
from typing import Any

import numpy as np
import xrayutilities as xu

from daf.core.math_utils import vec_norm

logger = logging.getLogger(__name__)

__all__ = [
    "ReciprocalMapGeometry",
    "get_peaks",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_EPSILON = 1e-7  # Threshold for filtering peaks by structure-factor strength
_ANGLE_TOO_SMALL_THRESHOLD = (
    1e-4  # Threshold for checking if a calculated angle is valid
)
_MOTOR_NAMES = ("mu", "eta", "chi", "phi", "nu", "del")


# ---------------------------------------------------------------------------
# Pure functions — Bragg peak computation
# ---------------------------------------------------------------------------


def _compute_bragg_indices(
    mat: Any, exp: Any, ttmax: float
) -> tuple[int, int, int, int, int, int]:
    """Compute maximal h, k, l indices for Bragg peaks within *ttmax* degrees."""
    pi = math.pi
    sin_half = math.sin(math.radians(ttmax / 2.0))
    hma = int(math.ceil(vec_norm(mat.a1) * exp.k0 / pi * sin_half))
    kma = int(math.ceil(vec_norm(mat.a2) * exp.k0 / pi * sin_half))
    lma = int(math.ceil(vec_norm(mat.a3) * exp.k0 / pi * sin_half))
    return hma, -hma, kma, -kma, lma, -lma


def get_peaks(mat: Any, exp: Any, ttmax: float = 180) -> np.ndarray:
    """Compute Bragg peak data for a material in the diffraction plane.

    Returns a numpy structured array with fields:
        q, qvec, r, hkl

    Parameters
    ----------
    mat:
        ``xu.materials.Crystal`` instance for structure factor calculations.
    exp:
        ``xu.HXRD`` (or compatible) experiment instance.  Defines the in-plane
        and out-of-plane directions as well as the sample azimuth.
    ttmax:
        Maximal 2-theta angle to consider (default 180 °).

    Returns
    -------
    numpy.ndarray
        Structured array with dtype fields ``q``, ``qvec``, ``r``, ``hkl``.
    """
    pi = math.pi
    hma, hmi, kma, kmi, lma, lmi = _compute_bragg_indices(mat, exp, ttmax)

    qmax = 2 * exp.k0 * math.sin(math.radians(ttmax / 2.0))
    hkl = (
        np.mgrid[hma : hmi - 1 : -1, kma : kmi - 1 : -1, lma : lmi - 1 : -1]
        .reshape(3, -1)
        .T
    )

    q = mat.Q(hkl)
    qnorm = vec_norm(q)
    m = qnorm < qmax

    data = np.zeros(
        np.sum(m),
        dtype=[
            ("q", np.double),
            ("qvec", np.ndarray),
            ("r", np.double),
            ("hkl", np.ndarray),
        ],
    )
    data["q"] = qnorm[m]
    data["qvec"] = list(exp.Transform(q[m]))
    rref = abs(mat.StructureFactor((0, 0, 0), exp.energy)) ** 2
    data["r"] = np.abs(mat.StructureFactorForQ(q[m], exp.energy)) ** 2
    data["r"] /= rref
    data["hkl"] = list(hkl[m])

    return data


# ---------------------------------------------------------------------------
# Pure geometry mixin
# ---------------------------------------------------------------------------


class ReciprocalMapGeometry:
    """Mixin providing pure Bragg-peak geometry for the DAF engine.

    Methods here depend only on ``self.bounds`` (motor angle limits) and
    mathematical operations — no matplotlib, no subprocess, no I/O.
    """

    def two_theta_max(self) -> tuple[float, float]:
        """Return (ttmax, ttmin) from the current motor angle bounds.

        Uses the Nu (index 4) and Del (index 5) bounds to determine the
        maximum and minimum 2-theta angles accessible in the diffraction
        plane.

        Returns
        -------
        tuple[float, float]
            ``(ttmax_deg, ttmin_deg)`` as floats.
        """

        def to_linspace(val: Any) -> Any:
            return (
                val
                if isinstance(val, (int, float))
                else np.linspace(val[0], val[1], 1000)
            )

        nub = to_linspace(self.bounds[4])
        delb = to_linspace(self.bounds[5])

        delb_grid, nub_grid = np.meshgrid(delb, nub)
        cos_product = np.cos(np.radians(delb_grid)) * np.cos(np.radians(nub_grid))
        two_theta = np.arccos(cos_product)

        return float(np.degrees(np.max(two_theta))), float(
            np.degrees(np.min(two_theta))
        )
