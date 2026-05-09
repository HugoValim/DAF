#!/usr/bin/env python3
"""
Pure factory for building DAF engine instances from experiment dictionaries.

This module extracts the DAF construction logic from CLIBase so that it can be
used independently of CLI concerns (no EPICS, no file I/O, no sys.argv).
"""
from __future__ import annotations

from typing import Any

from daf.core.main import DAF
from daf.utils.experiment_config import ExperimentConfig


class DAFEngineFactory:
    """Build a fully configured DAF instance from a plain experiment dict."""

    @classmethod
    def from_dict(cls, experiment_dict: dict[str, Any]) -> DAF:
        """Return a DAF instance configured from *experiment_dict*.

        The dict is expected to contain the same keys as the ``.Experiment``
        file produced by DAFIO.
        """
        return cls.from_config(ExperimentConfig.from_dict(experiment_dict))

    @classmethod
    def from_config(cls, config: ExperimentConfig) -> DAF:
        """Return a DAF instance configured from typed experiment config."""
        daf = DAF(*config.mode)
        cls._configure_material(daf, config.raw)
        daf.set_exp_conditions(
            idir=config.idir,
            ndir=config.ndir,
            rdir=config.rdir,
            en=config.energy,
            sampleor=config.sample_orientation,
        )
        daf.set_circle_constrain(**config.motor_bounds)
        daf.set_constraints(**config.constraints)
        daf.set_U(config.u_matrix)
        daf.build_xrd_experiment()
        daf.build_bounds()

        return daf

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
