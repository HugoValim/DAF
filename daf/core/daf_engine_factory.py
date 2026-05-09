#!/usr/bin/env python3
"""
Pure factory for building DAF engine instances from experiment dictionaries.

This module extracts the DAF construction logic from CLIBase so that it can be
used independently of CLI concerns (no EPICS, no file I/O, no sys.argv).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from daf.core.main import DAF


class DAFEngineFactory:
    """Build a fully configured DAF instance from a plain experiment dict."""

    # Motor names in canonical order
    _MOTOR_NAMES = ("mu", "eta", "chi", "phi", "nu", "del")

    # Keys for constraints
    _CONSTRAINT_KEYS = (
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

    @classmethod
    def from_dict(cls, experiment_dict: dict[str, Any]) -> DAF:
        """Return a DAF instance configured from *experiment_dict*.

        The dict is expected to contain the same keys as the ``.Experiment``
        file produced by DAFIO.
        """
        mode = cls._extract_mode(experiment_dict)
        u_mat = cls._extract_u_matrix(experiment_dict)
        idir = experiment_dict["IDir_print"]
        ndir = experiment_dict["NDir_print"]
        rdir = experiment_dict["RDir"]
        bounds = cls._extract_motor_bounds(experiment_dict)
        energy = cls._extract_energy(experiment_dict)

        daf = DAF(*mode)
        cls._configure_material(daf, experiment_dict)
        daf.set_exp_conditions(
            idir=idir,
            ndir=ndir,
            rdir=rdir,
            en=energy,
            sampleor=experiment_dict["Sampleor"],
        )
        daf.set_circle_constrain(**bounds)
        daf.set_constraints(**cls._extract_constraints(experiment_dict))
        daf.set_U(u_mat)
        daf.build_xrd_experiment()
        daf.build_bounds()

        return daf

    @classmethod
    def _extract_mode(cls, experiment_dict: dict[str, Any]) -> tuple[int, ...]:
        """Parse the mode string/tuple into ints."""
        mode_val = experiment_dict["Mode"]
        if isinstance(mode_val, str):
            return tuple(int(ch) for ch in mode_val)
        return tuple(int(i) for i in mode_val)

    @classmethod
    def _extract_u_matrix(cls, experiment_dict: dict[str, Any]) -> np.ndarray:
        """Build the U matrix numpy array."""
        return np.array(experiment_dict["U_mat"])

    @classmethod
    def _extract_motor_bounds(cls, experiment_dict: dict[str, Any]) -> dict[str, list]:
        """Return motor bounds keyed by canonical motor names."""
        motors = experiment_dict["motors"]
        return {m: motors[m]["bounds"] for m in cls._MOTOR_NAMES}

    @classmethod
    def _extract_constraints(cls, experiment_dict: dict[str, Any]) -> dict[str, Any]:
        """Return constraint values keyed by constraint name."""
        return {k: experiment_dict[k] for k in cls._CONSTRAINT_KEYS}

    @classmethod
    def _extract_energy(cls, experiment_dict: dict[str, Any]) -> float:
        """Compute beam energy accounting for the offset."""
        return (
            experiment_dict["beamline_pvs"]["energy"]["value"]
            - experiment_dict["energy_offset"]
        )

    @classmethod
    def _configure_material(cls, daf: DAF, experiment_dict: dict[str, Any]) -> None:
        """Set the sample material on *daf*."""
        material = experiment_dict["Material"]
        if material in experiment_dict.get("user_samples", {}):
            daf.set_material(material, *experiment_dict["user_samples"][material])
        else:
            daf.set_material(
                material,
                experiment_dict["lparam_a"],
                experiment_dict["lparam_b"],
                experiment_dict["lparam_c"],
                experiment_dict["lparam_alpha"],
                experiment_dict["lparam_beta"],
                experiment_dict["lparam_gama"],
            )
