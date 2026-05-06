"""Reciprocal-space map widget for the DAF GUI.

This module owns all matplotlib canvas creation, interactive callbacks
(mouse hover / click), and the ``daf.amv`` subprocess spawn that moves
the diffractometer to a clicked reflection.

The pure Bragg-peak geometry (peak positions, structure factors) is
delegated to ``daf.core.reciprocal_map.get_peaks`` and the ``DAF`` engine.
"""
from __future__ import annotations

import logging
import subprocess
from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import matplotlib.patches

import daf.utils.dafutilities as du
from daf.core.main import DAF
from daf.core.reciprocal_map import get_peaks, _EPSILON, _ANGLE_TOO_SMALL_THRESHOLD
from daf.core.matrix_utils import calculate_pseudo_angle_from_motor_angles

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.collections import PathCollection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper drawing functions (GUI-only, not part of the core engine)
# ---------------------------------------------------------------------------


def _setup_figure(ax: Axes | None, k0: float) -> tuple[Any, Axes]:
    """Create or reuse a matplotlib figure/axes, set fixed axis limits.

    Parameters
    ----------
    ax:
        Existing :class:`matplotlib.axes.Axes` to reuse, or ``None`` to
        create a fresh figure.
    k0:
        Wave-vector magnitude used to set axis limits.

    Returns
    -------
    tuple[Figure, Axes]
    """
    if ax is None:
        fig = plt.figure(figsize=(9, 5))
        ax = plt.subplot(111)
    else:
        fig = ax.get_figure()
        plt.sca(ax)
    plt.axis("scaled")
    ax.set_autoscaley_on(False)
    ax.set_autoscalex_on(False)
    plt.xlim(-2.05 * k0, 2.05 * k0)
    plt.ylim(-0.05 * k0, 2.05 * k0)
    return fig, ax


def _draw_laue_zones(
    ax: Axes,
    k0: float,
    ttmax: float,
    ttmin: float | None,
) -> None:
    """Draw Laue-zone circles onto *ax*.

    Parameters
    ----------
    ax:
        Target axes.
    k0:
        Wave-vector magnitude.
    ttmax:
        Maximum 2-theta angle in degrees.
    ttmin:
        Minimum 2-theta angle in degrees, or ``None`` to skip the inner ring.
    """
    import math

    c = matplotlib.patches.Circle(
        (0, 0), 2 * k0, facecolor="#FF9180", edgecolor="none"
    )
    ax.add_patch(c)
    qmax = 2 * k0 * math.sin(math.radians(ttmax / 2.0))
    c = matplotlib.patches.Circle(
        (0, 0), qmax, facecolor="#FFFFFF", edgecolor="none"
    )
    ax.add_patch(c)
    if ttmin:
        qmin = 2 * k0 * math.sin(math.radians(ttmin / 2.0))
        c = matplotlib.patches.Circle(
            (0, 0), qmin, facecolor="#FF9180", edgecolor="none"
        )
        ax.add_patch(c)
    for cx, cy, r in [(0, 0, 2 * k0), (k0, 0, k0), (-k0, 0, k0)]:
        c = matplotlib.patches.Circle(
            (cx, cy), r, facecolor="none", edgecolor="0.5"
        )
        ax.add_patch(c)
    plt.hlines(0, -2 * k0, 2 * k0, color="0.5", lw=0.5)
    plt.vlines(0, -2 * k0, 2 * k0, color="0.5", lw=0.5)


def _plot_peaks(
    ax: Axes,
    x: np.ndarray,
    y: np.ndarray,
    s: np.ndarray,
    mat_name: str,
    label: str | None,
    color: str | None,
) -> PathCollection:
    """Scatter-plot Bragg peaks and return the :class:`PathCollection` handle.

    Parameters
    ----------
    ax:
        Target axes.
    x, y:
        In-plane and out-of-plane Q coordinates.
    s:
        Marker sizes (scaled structure-factor intensities).
    mat_name:
        Material name used as a default legend label.
    label:
        Optional override for the legend label.
    color:
        Optional colour string passed to :meth:`PathCollection.set_color`.

    Returns
    -------
    PathCollection
    """
    legend_label = label if label else mat_name
    h = plt.scatter(x, y, s=s, zorder=2, label=legend_label)
    if color:
        h.set_color(color)
    plt.xlabel(r"$Q$ inplane ($\mathrm{\AA^{-1}}$)")
    plt.ylabel(r"$Q$ out of plane ($\mathrm{\AA^{-1}}$)")
    return h


def show_reciprocal_space_plane(
    exp: DAF,
    ttmax: float | None = None,
    ttmin: float | None = None,
    maxqout: float = 0.01,
    scalef: float = 100,
    ax: Axes | None = None,
    color: str | None = None,
    show_Laue: bool = True,
    show_legend: bool = True,
    projection: str = "perpendicular",
    label: str | None = None,
    idir: tuple | None = None,
    ndir: tuple | None = None,
    move: bool = True,
) -> tuple[Axes, PathCollection] | None:
    """Plot the coplanar diffraction plane with Bragg peak positions.

    Spot sizes are scaled by the structure-factor intensity.  Clicking a
    spot triggers a ``daf.amv`` subprocess call to move the diffractometer
    (when *move* is ``True``).  Hovering shows the reflection index in a
    floating annotation.

    Parameters
    ----------
    exp:
        Fully configured :class:`~daf.core.main.DAF` instance.
    ttmax:
        Maximum 2-theta angle to consider (default 180 °).
    ttmin:
        Minimum 2-theta angle to shade (optional).
    maxqout:
        Maximum out-of-plane Q as a fraction of ``exp.k0``.
    scalef:
        Scale factor for marker sizes.
    ax:
        Existing axes to draw into, or ``None`` to create a new figure.
    color:
        Colour override for the scatter markers.
    show_Laue:
        Whether to draw the Laue-zone rings.
    show_legend:
        Whether to show the legend.
    projection:
        ``'perpendicular'`` (default) or ``'polar'`` projection for peaks
        that are slightly out of the diffraction plane.
    label:
        Legend label override.  Defaults to the material name.
    idir:
        In-plane reference direction override.
    ndir:
        Normal reference direction override.
    move:
        If ``True``, clicking a peak calls ``daf.amv`` to move motors.

    Returns
    -------
    tuple[Axes, PathCollection] or None
        The axes and scatter handle, or ``None`` if matplotlib is unavailable.
    """
    import xrayutilities as xu

    hxrd = xu.HXRD(idir, ndir, en=exp.en, qconv=exp.qconv, sampleor=exp.sampleor)
    mat = exp.sample

    if ttmax is None:
        ttmax = 180

    d = get_peaks(mat, hxrd, ttmax)
    k0 = hxrd.k0

    fig, ax = _setup_figure(ax, k0)

    if show_Laue:
        _draw_laue_zones(ax, k0, ttmax, ttmin)

    # Build mask for peaks that are close enough to the diffraction plane
    m = np.zeros_like(d, dtype=bool)
    for i, (q, r) in enumerate(zip(d["qvec"], d["r"])):
        if abs(q[0]) < maxqout * k0 and r > _EPSILON:
            m[i] = True

    x = np.empty_like(d["r"][m])
    y = np.empty_like(d["r"][m])
    s = np.empty_like(d["r"][m])
    for i, (qv, r) in enumerate(zip(d["qvec"][m], d["r"][m])):
        if projection == "perpendicular":
            x[i] = qv[1]
        else:
            x[i] = np.sign(qv[1]) * np.sqrt(qv[0] ** 2 + qv[1] ** 2)
        y[i] = qv[2]
        s[i] = r * scalef

    h = _plot_peaks(ax, x, y, s, mat.name, label, color)

    if show_legend:
        if len(fig.legends) == 1:
            fig.legends[0].remove()
        fig.legend(*ax.get_legend_handles_labels(), loc="upper right")
    plt.tight_layout()

    # -----------------------------------------------------------------------
    # Interactive annotations
    # -----------------------------------------------------------------------

    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(20, 20),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
    )
    annot.set_visible(False)

    def _update_annot(ind: dict) -> None:
        pos = h.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "{}\n{}".format(mat.name, str(d["hkl"][m][ind["ind"][0]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(h.get_facecolor()[0])
        annot.get_bbox_patch().set_alpha(0.2)

    def _hover(event: Any) -> None:
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = h.contains(event)
            if cont:
                _update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    def _click(event: Any) -> None:
        if event.inaxes != ax:
            return
        cont, ind = h.contains(event)
        if not cont:
            return

        popts = np.get_printoptions()
        np.set_printoptions(precision=4, suppress=True)
        io = du.DAFIO()
        dict_args = io.read()
        startvalue = [
            float(dict_args["motors"]["mu"]["value"]),
            float(dict_args["motors"]["eta"]["value"]),
            float(dict_args["motors"]["chi"]["value"]),
            float(dict_args["motors"]["phi"]["value"]),
            float(dict_args["motors"]["nu"]["value"]),
            float(dict_args["motors"]["del"]["value"]),
        ]

        hkl = d["hkl"][m][ind["ind"][0]]
        exp.hkl = hkl
        ang = exp.motor_angles(exp, start_values=startvalue, flagmap=True)
        angles = list(ang[0][:6]) + [float(ang[0][-1])]

        np.set_printoptions(**popts)

        pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
            *angles[:6], exp.sample, exp.hkl, exp.lam, exp.nref, exp.U
        )
        exp_dict = {
            "mu": angles[0],
            "eta": angles[1],
            "chi": angles[2],
            "phi": angles[3],
            "nu": angles[4],
            "del": angles[5],
            "alpha": pseudo_angles_dict.alpha,
            "qaz": pseudo_angles_dict.qaz,
            "naz": pseudo_angles_dict.naz,
            "tau": pseudo_angles_dict.tau,
            "psi": pseudo_angles_dict.psi,
            "beta": pseudo_angles_dict.beta,
            "omega": pseudo_angles_dict.omega,
            "hklnow": list(exp.hkl_calc),
        }
        exp.set_print_options(marker="", column_marker="", space=14)
        lb = lambda x: "{:.5f}".format(float(x))  # noqa: E731
        if move:
            if angles[6] < _ANGLE_TOO_SMALL_THRESHOLD:
                logger.info(str(exp))
                subprocess.Popen(
                    [
                        "daf.amv",
                        "-m", lb(exp_dict["mu"]),
                        "-e", lb(exp_dict["eta"]),
                        "-c", lb(exp_dict["chi"]),
                        "-p", lb(exp_dict["phi"]),
                        "-n", lb(exp_dict["nu"]),
                        "-d", lb(exp_dict["del"]),
                    ],
                    shell=False,
                )
            else:
                logger.warning("Can't find the reflection %s", hkl)
        else:
            if angles[6] < _ANGLE_TOO_SMALL_THRESHOLD:
                logger.info(str(exp))
            else:
                logger.warning("Can't find the reflection %s", hkl)

    fig.canvas.mpl_connect("motion_notify_event", _hover)
    fig.canvas.mpl_connect("button_press_event", _click)
    return ax, h


# ---------------------------------------------------------------------------
# Qt widget
# ---------------------------------------------------------------------------


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
            mode, dict_args, idir, ndir, rdir,
            Mu_bound, Eta_bound, Chi_bound, Phi_bound, Nu_bound, Del_bound, U,
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
                en=dict_args["beamline_pvs"]["energy"]["value"] - dict_args["energy_offset"],
                sampleor=dict_args["Sampleor"],
            )
            extra_exp.set_circle_constrain(
                Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound,
                Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound,
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
            exp.set_material(dict_args["Material"], *dict_args["user_samples"][dict_args["Material"]])
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
            en=dict_args["beamline_pvs"]["energy"]["value"] - dict_args["energy_offset"],
            sampleor=dict_args["Sampleor"],
        )
        exp.set_circle_constrain(
            Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound,
            Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound,
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
