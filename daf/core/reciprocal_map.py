#!/usr/bin/env python3
"""Reciprocal space mapping and visualization for diffraction experiments."""

import logging
import subprocess
import math
import numpy as np
import xrayutilities as xu

import daf.utils.dafutilities as du
from daf.core.matrix_utils import calculate_pseudo_angle_from_motor_angles
from daf.core.math_utils import vec_norm

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------
# Lazy matplotlib import
# --------------------------------------------------------------------


def _get_matplotlib_pyplot(funcname="XU"):
    """Lazy import of matplotlib.pyplot.

    Returns (success, plt_or_None).
    """
    try:
        from matplotlib import pyplot as plt

        return True, plt
    except ImportError:
        logger.warning("%s: Warning: plot functionality not available", funcname)
        return False, None


# --------------------------------------------------------------------
# Peak computation (pure functions)
# --------------------------------------------------------------------

_EPSILON = 1e-7  # Threshold for filtering peaks by strength
_ANGLE_TOO_SMALL_THRESHOLD = 1e-4  # Threshold for checking if calculated angle is valid
_MOTOR_NAMES = ("mu", "eta", "chi", "phi", "nu", "del")
_PI = math.pi


def _compute_bragg_indices(mat, exp, ttmax):
    """Compute maximal h,k,l indices for Bragg peaks within ttmax."""
    pi = math.pi
    hma = int(
        math.ceil(vec_norm(mat.a1) * exp.k0 / pi * math.sin(math.radians(ttmax / 2.0)))
    )
    kma = int(
        math.ceil(vec_norm(mat.a2) * exp.k0 / pi * math.sin(math.radians(ttmax / 2.0)))
    )
    lma = int(
        math.ceil(vec_norm(mat.a3) * exp.k0 / pi * math.sin(math.radians(ttmax / 2.0)))
    )
    return hma, -hma, kma, -kma, lma, -lma


def get_peaks(mat, exp, ttmax=180):
    """Compute Bragg peak data for a material in the diffraction plane.

    Returns a numpy structured array with fields:
        q, qvec, r, hkl

    Parameters
    ----------
    mat : xu.materials.Crystal
    exp : xu.HXRD or similar experiment
    ttmax : float
        maximal 2theta angle to consider (default 180)
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


class ReciprocalMapWindow:
    def two_theta_max(self):
        """Method to get the maximum 2theta to show in the 2D reciprocal map"""

        def to_linspace(val):
            return val if isinstance(val, float) else np.linspace(val[0], val[1], 1000)

        nub = to_linspace(self.bounds[4])
        delb = to_linspace(self.bounds[5])

        delb, nub = np.meshgrid(delb, nub)
        R = np.cos(np.radians(delb)) * np.cos(np.radians(nub))
        Z = np.arccos(R)

        return np.degrees(np.max(Z)), np.degrees(np.min(Z))

    def show_reciprocal_space_plane(
        self,
        ttmax=None,
        ttmin=None,
        maxqout=0.01,
        scalef=100,
        ax=None,
        color=None,
        show_Laue=True,
        show_legend=True,
        projection="perpendicular",
        label=None,
        idir=None,
        ndir=None,
        move=True,
    ):
        """
        show a plot of the coplanar diffraction plane with peak positions for the
        respective material. the size of the spots is scaled with the strength of
        the structure factor

        Parameters
        ----------
        mat:        Crystal
            instance of Crystal for structure factor calculations
        exp:        Experiment
            instance of Experiment (needs to be HXRD, or FourC for onclick action
            to work correctly). defines the inplane and out of plane direction as
            well as the sample azimuth
        ttmax:      float, optional
            maximal 2Theta angle to consider, by default 180deg
        maxqout:    float, optional
            maximal out of plane q for plotted Bragg peaks as fraction of exp.k0
        scalef:     float, optional
            scale factor for the marker size
        ax:         matplotlib.Axes, optional
            matplotlib Axes to use for the plot, useful if multiple materials
            should be plotted in one plot
        color:      matplotlib color, optional
        show_Laue:  bool, optional
            flag to indicate if the Laue zones should be indicated
        show_legend:    bool, optional
            flag to indiate if a legend should be shown
        projection: 'perpendicular', 'polar', optional
            type of projection for Bragg peaks which do not fall into the
            diffraction plane. 'perpendicular' (default) uses only the inplane
            component in the scattering plane, whereas 'polar' uses the vectorial
            absolute value of the two inplane components. See also the 'maxqout'
            option.
        label:  None or str, optional
            label to be used for the legend. If 'None' the name of the material
            will be used.

        Returns
        -------
        Axes, plot_handle
        """
        plot, plt = _get_matplotlib_pyplot("XU.materials")
        if not plot:
            logger.error("matplotlib needed for show_reciprocal_space_plane")
            return

        exp = xu.HXRD(idir, ndir, en=self.en, qconv=self.qconv, sampleor=self.sampleor)
        mat = self.samp

        if ttmax is None:
            ttmax = 180

        d = get_peaks(mat, exp, ttmax)
        k0 = exp.k0

        if not ax:
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

        if show_Laue:
            c = plt.matplotlib.patches.Circle(
                (0, 0), 2 * k0, facecolor="#FF9180", edgecolor="none"
            )
            ax.add_patch(c)
            qmax = 2 * k0 * math.sin(math.radians(ttmax / 2.0))
            c = plt.matplotlib.patches.Circle(
                (0, 0), qmax, facecolor="#FFFFFF", edgecolor="none"
            )
            ax.add_patch(c)
            if ttmin:
                qmax = 2 * k0 * math.sin(math.radians(ttmin / 2.0))
                c = plt.matplotlib.patches.Circle(
                    (0, 0), qmax, facecolor="#FF9180", edgecolor="none"
                )
                ax.add_patch(c)

            c = plt.matplotlib.patches.Circle(
                (0, 0), 2 * k0, facecolor="none", edgecolor="0.5"
            )
            ax.add_patch(c)
            c = plt.matplotlib.patches.Circle(
                (k0, 0), k0, facecolor="none", edgecolor="0.5"
            )
            ax.add_patch(c)
            c = plt.matplotlib.patches.Circle(
                (-k0, 0), k0, facecolor="none", edgecolor="0.5"
            )
            ax.add_patch(c)
            plt.hlines(0, -2 * k0, 2 * k0, color="0.5", lw=0.5)
            plt.vlines(0, -2 * k0, 2 * k0, color="0.5", lw=0.5)

        # generate mask for plotting
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
        label = label if label else mat.name
        h = plt.scatter(x, y, s=s, zorder=2, label=label)

        if color:
            h.set_color(color)

        plt.xlabel(r"$Q$ inplane ($\mathrm{\AA^{-1}}$)")
        plt.ylabel(r"$Q$ out of plane ($\mathrm{\AA^{-1}}$)")

        if show_legend:
            if len(fig.legends) == 1:
                fig.legends[0].remove()
            fig.legend(*ax.get_legend_handles_labels(), loc="upper right")
        plt.tight_layout()

        annot = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        annot.set_visible(False)

        def update_annot(ind):
            pos = h.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            text = "{}\n{}".format(mat.name, str(d["hkl"][m][ind["ind"][0]]))
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor(h.get_facecolor()[0])
            annot.get_bbox_patch().set_alpha(0.2)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = h.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        def click(event):
            if event.inaxes == ax:
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
                self.hkl = hkl
                ang = self.motor_angles(self, sv=startvalue, flagmap=True)
                angles = list(ang[0][:6]) + [float(ang[0][-1])]

                np.set_printoptions(**popts)

                pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
                    *angles[:6], self.samp, self.hkl, self.lam, self.nref, self.U
                )
                exp_dict = {
                    "mu": angles[0],
                    "eta": angles[1],
                    "chi": angles[2],
                    "phi": angles[3],
                    "nu": angles[4],
                    "del": angles[5],
                    "alpha": pseudo_angles_dict["alpha"],
                    "qaz": pseudo_angles_dict["qaz"],
                    "naz": pseudo_angles_dict["naz"],
                    "tau": pseudo_angles_dict["tau"],
                    "psi": pseudo_angles_dict["psi"],
                    "beta": pseudo_angles_dict["beta"],
                    "omega": pseudo_angles_dict["omega"],
                    "hklnow": list(self.hkl_calc),
                }
                self.set_print_options(marker="", column_marker="", space=14)
                lb = lambda x: "{:.5f}".format(float(x))
                if move:
                    if angles[6] < _ANGLE_TOO_SMALL_THRESHOLD:
                        logger.info(self.__str__())
                        subprocess.Popen(
                            [
                                "daf.amv",
                                "-m",
                                lb(exp_dict["mu"]),
                                "-e",
                                lb(exp_dict["eta"]),
                                "-c",
                                lb(exp_dict["chi"]),
                                "-p",
                                lb(exp_dict["phi"]),
                                "-n",
                                lb(exp_dict["nu"]),
                                "-d",
                                lb(exp_dict["del"]),
                            ],
                            shell=False,
                        )
                    else:
                        logger.warning("Can't find the reflection %s", hkl)
                else:
                    if angles[6] < _ANGLE_TOO_SMALL_THRESHOLD:
                        logger.info(self.__str__())
                    else:
                        logger.warning("Can't find the reflection %s", hkl)

        fig.canvas.mpl_connect("motion_notify_event", hover)
        fig.canvas.mpl_connect("button_press_event", click)
        return ax, h
