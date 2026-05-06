"""Reciprocal-space map widget for the DAF GUI.

This module owns the Qt widget that embeds a matplotlib canvas.
All drawing logic is delegated to :mod:`daf.core.reciprocal_map_plot`.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from daf.core.main import DAF
from daf.core.reciprocal_map_plot import show_reciprocal_space_plane


class RMapWidget(FigureCanvasQTAgg):
    """Qt widget that displays the reciprocal-space map for the DAF GUI."""

    def __init__(
        self,
        parent: Any = None,
        dict_args: dict | None = None,
        move: bool = False,
        samples: list | None = None,
        idirp: list | None = None,
        ndirp: list | None = None,
    ) -> None:
        if samples is None:
            samples = []

        U = np.array(dict_args["U_mat"])
        mode = [int(i) for i in dict_args["Mode"]]
        idir = dict_args["IDir"]
        ndir = dict_args["NDir"]
        rdir = dict_args["RDir"]
        paradir = idirp
        normdir = ndirp
        Mu_bound = dict_args["motors"]["mu"]["bounds"]
        Eta_bound = dict_args["motors"]["eta"]["bounds"]
        Chi_bound = dict_args["motors"]["chi"]["bounds"]
        Phi_bound = dict_args["motors"]["phi"]["bounds"]
        Nu_bound = dict_args["motors"]["nu"]["bounds"]
        Del_bound = dict_args["motors"]["del"]["bounds"]

        exp = self._build_exp(
            mode,
            dict_args,
            idir,
            ndir,
            rdir,
            Mu_bound,
            Eta_bound,
            Chi_bound,
            Phi_bound,
            Nu_bound,
            Del_bound,
            U,
        )

        exp.build_xrd_experiment()
        exp.build_bounds()
        ttmax, ttmin = exp.two_theta_max()
        self.ax, _ = show_reciprocal_space_plane(
            exp,
            ttmax=ttmax,
            ttmin=ttmin,
            idir=paradir,
            ndir=normdir,
            scalef=100,
            move=move,
        )
        for sample_name in samples:
            extra_exp = DAF(*mode)
            extra_exp.set_material(str(sample_name))
            extra_exp.set_exp_conditions(
                idir=idir,
                ndir=ndir,
                rdir=rdir,
                en=dict_args["beamline_pvs"]["energy"]["value"]
                - dict_args["energy_offset"],
                sampleor=dict_args["Sampleor"],
            )
            extra_exp.set_circle_constrain(
                Mu=Mu_bound,
                Eta=Eta_bound,
                Chi=Chi_bound,
                Phi=Phi_bound,
                Nu=Nu_bound,
                Del=Del_bound,
            )
            extra_exp.set_U(U)
            extra_exp.set_constraints(
                Mu=dict_args["cons_mu"],
                Eta=dict_args["cons_eta"],
                Chi=dict_args["cons_chi"],
                Phi=dict_args["cons_phi"],
                Nu=dict_args["cons_nu"],
                Del=dict_args["cons_del"],
                alpha=dict_args["cons_alpha"],
                beta=dict_args["cons_beta"],
                psi=dict_args["cons_psi"],
                omega=dict_args["cons_omega"],
                qaz=dict_args["cons_qaz"],
                naz=dict_args["cons_naz"],
            )
            extra_exp.build_xrd_experiment()
            extra_exp.build_bounds()
            ttmax, ttmin = extra_exp.two_theta_max()
            self.ax, _ = show_reciprocal_space_plane(
                extra_exp,
                ttmax=ttmax,
                ttmin=ttmin,
                idir=paradir,
                ndir=normdir,
                scalef=100,
                ax=self.ax,
                move=move,
            )

        super().__init__(self.ax.figure)

    @staticmethod
    def _build_exp(
        mode: list[int],
        dict_args: dict,
        idir: Any,
        ndir: Any,
        rdir: Any,
        Mu_bound: Any,
        Eta_bound: Any,
        Chi_bound: Any,
        Phi_bound: Any,
        Nu_bound: Any,
        Del_bound: Any,
        U: np.ndarray,
    ) -> DAF:
        """Construct and configure a ``DAF`` instance from experiment data."""
        exp = DAF(*mode)
        if dict_args["Material"] in dict_args["user_samples"]:
            exp.set_material(
                dict_args["Material"], *dict_args["user_samples"][dict_args["Material"]]
            )
        else:
            exp.set_material(
                dict_args["Material"],
                dict_args["lparam_a"],
                dict_args["lparam_b"],
                dict_args["lparam_c"],
                dict_args["lparam_alpha"],
                dict_args["lparam_beta"],
                dict_args["lparam_gama"],
            )
        exp.set_exp_conditions(
            idir=idir,
            ndir=ndir,
            rdir=rdir,
            en=dict_args["beamline_pvs"]["energy"]["value"]
            - dict_args["energy_offset"],
            sampleor=dict_args["Sampleor"],
        )
        exp.set_circle_constrain(
            Mu=Mu_bound,
            Eta=Eta_bound,
            Chi=Chi_bound,
            Phi=Phi_bound,
            Nu=Nu_bound,
            Del=Del_bound,
        )
        exp.set_U(U)
        exp.set_constraints(
            Mu=dict_args["cons_mu"],
            Eta=dict_args["cons_eta"],
            Chi=dict_args["cons_chi"],
            Phi=dict_args["cons_phi"],
            Nu=dict_args["cons_nu"],
            Del=dict_args["cons_del"],
            alpha=dict_args["cons_alpha"],
            beta=dict_args["cons_beta"],
            psi=dict_args["cons_psi"],
            omega=dict_args["cons_omega"],
            qaz=dict_args["cons_qaz"],
            naz=dict_args["cons_naz"],
        )
        return exp
