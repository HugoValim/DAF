#!/usr/bin/env python3

import subprocess
import xrayutilities as xu
import numpy as np

import daf.utils.dafutilities as du
from daf.core.matrix_utils import (
    calculate_rotation_matrix_from_diffractometer_angles,
    calculate_pseudo_angle_from_motor_angles,
)


class ReciprocalMapWindow:
    def two_theta_max(self):
        """Method to get the maximum 2theta to show in the 2D reciprocal map"""
        if type(self.bounds[4]) == float:
            nub = self.bounds[4]
        else:
            nub = np.linspace(self.bounds[4][0], self.bounds[4][1], 1000)

        if type(self.bounds[5]) == float:
            delb = self.bounds[5]
        else:
            delb = np.linspace(self.bounds[5][0], self.bounds[5][1], 1000)

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
        import math
        import numpy

        ttmin = None
        exp = xu.HXRD(idir, ndir, en=self.en, qconv=self.qconv, sampleor=self.sampleor)
        exp_real = self.hrxrd

        mat = self.samp
        pi = np.pi
        EPSILON = 1e-7

        def import_matplotlib_pyplot(funcname="XU"):
            """
            lazy import function of matplotlib.pyplot

            Parameters
            ----------
            funcname :      str
                identification string of the calling function

            Returns
            -------
            flag :  bool
                the flag is True if the loading was successful and False otherwise.
            pyplot
                On success pyplot is the matplotlib.pyplot package.
            """
            try:
                from matplotlib import pyplot as plt

                # from .mpl_helper import SqrtAllowNegScale
                return True, plt
            except ImportError:  # print(d['qvec'][m][ind['ind'][0]])
                if config.VERBOSITY >= config.INFO_LOW:
                    print("%s: Warning: plot functionality not available" % funcname)
                return False, None

        def get_peaks(mat, exp, ttmax):
            """
            Parameters
            ----------
            mat:        Crystal
                instance of Crystal for structure factor calculations
            exp:        Experiment
                instance of Experiment (likely HXRD, or FourC)
            tt_cutoff:  float
                maximal 2Theta angle to consider, by default 180deg

            Returns
            -------
            ndarray
                data array with columns for 'q', 'qvec', 'hkl', 'r' for the Bragg
                peaks
            """
            # print(exp)
            ttmax = 180
            # print(d['qvec'][m][ind['ind'][0]])

            # calculate maximal Bragg indices
            hma = int(
                math.ceil(
                    xu.math.vector.VecNorm(mat.a1)
                    * exp.k0
                    / pi
                    * math.sin(math.radians(ttmax / 2.0))
                )
            )
            hmi = -hma
            kma = int(
                math.ceil(
                    xu.math.vector.VecNorm(mat.a2)
                    * exp.k0
                    / pi
                    * math.sin(math.radians(ttmax / 2.0))
                )
            )
            kmi = -kma
            lma = int(
                math.ceil(
                    xu.math.vector.VecNorm(mat.a3)
                    * exp.k0
                    / pi
                    * math.sin(math.radians(ttmax / 2.0))
                )
            )
            lmi = -lma

            # calculate structure factors
            qmax = 2 * exp.k0 * math.sin(math.radians(ttmax / 2.0))
            hkl = (
                numpy.mgrid[hma : hmi - 1 : -1, kma : kmi - 1 : -1, lma : lmi - 1 : -1]
                .reshape(3, -1)
                .T
            )

            q = mat.Q(hkl)
            qnorm = xu.math.vector.VecNorm(q)
            m = qnorm < qmax

            data = numpy.zeros(
                numpy.sum(m),
                dtype=[
                    ("q", numpy.double),
                    ("qvec", numpy.ndarray),
                    ("r", numpy.double),
                    ("hkl", numpy.ndarray),
                ],
            )
            data["q"] = qnorm[m]
            data["qvec"] = list(exp.Transform(q[m]))
            rref = abs(mat.StructureFactor((0, 0, 0), exp.energy)) ** 2
            data["r"] = numpy.abs(mat.StructureFactorForQ(q[m], exp.energy)) ** 2
            data["r"] /= rref
            data["hkl"] = list(hkl[m])

            return data

        plot, plt = import_matplotlib_pyplot("XU.materials")

        if not plot:
            print("matplotlib needed for show_reciprocal_space_plane")
            return

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
        m = numpy.zeros_like(d, dtype=numpy.bool)
        for i, (q, r) in enumerate(zip(d["qvec"], d["r"])):
            if abs(q[0]) < maxqout * k0 and r > EPSILON:
                m[i] = True

        x = numpy.empty_like(d["r"][m])
        y = numpy.empty_like(d["r"][m])
        s = numpy.empty_like(d["r"][m])
        for i, (qv, r) in enumerate(zip(d["qvec"][m], d["r"][m])):
            if projection == "perpendicular":
                x[i] = qv[1]
            else:
                x[i] = numpy.sign(qv[1]) * numpy.sqrt(qv[0] ** 2 + qv[1] ** 2)
            y[i] = qv[2]
            s[i] = r * scalef
        label = label if label else mat.name
        h = plt.scatter(x, y, s=s, zorder=2, label=label)
        from matplotlib import pyplot as plt

        # plt.show(block=True)
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

                if cont:
                    popts = numpy.get_printoptions()
                    numpy.set_printoptions(precision=4, suppress=True)
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
                    angles = [
                        ang[0][0],
                        ang[0][1],
                        ang[0][2],
                        ang[0][3],
                        ang[0][4],
                        ang[0][5],
                        float(ang[0][-1]),
                    ]

                    text = "{}\nhkl: {}\nangles: {}".format(
                        mat.name, str(d["hkl"][m][ind["ind"][0]]), str(angles)
                    )
                    numpy.set_printoptions(**popts)

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
                        if angles[6] < 1e-4:
                            print_str = self.__str__()
                            print(print_str)
                            # print("daf.amv -m {} -e {} -c {} -p {} -n {} -d {}".format(lb(exp_dict['Mu']), lb(exp_dict['Eta']), lb(exp_dict['Chi']), lb(exp_dict['Phi']), lb(exp_dict['Nu']), lb(exp_dict['Del'])))
                            subprocess.Popen(
                                "daf.amv -m {} -e {} -c {} -p {} -n {} -d {}".format(
                                    lb(exp_dict["mu"]),
                                    lb(exp_dict["eta"]),
                                    lb(exp_dict["chi"]),
                                    lb(exp_dict["phi"]),
                                    lb(exp_dict["nu"]),
                                    lb(exp_dict["del"]),
                                ),
                                shell=True,
                            )
                        else:
                            print("Can't find the reflection {}".format(hkl))
                    else:
                        if angles[6] < 1e-4:
                            print_str = self.__str__()
                            print(print_str)
                        else:
                            print("Can't find the reflection {}".format(hkl))

        fig.canvas.mpl_connect("motion_notify_event", hover)
        fig.canvas.mpl_connect("button_press_event", click)
        return ax, h
