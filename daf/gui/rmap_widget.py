import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# DAF GUIs imports
from daf.core.main import DAF


class RMapWidget(FigureCanvasQTAgg):
    """Class to handle the RMap plot in the GUI"""

    def __init__(
        self,
        parent=None,
        dict_args=None,
        move=False,
        samples=None,
        idirp=None,
        ndirp=None,
    ):
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

        exp = DAF(*mode)
        if dict_args["Material"] in dict_args["user_samples"].keys():
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

        exp.build_xrd_experiment()
        exp.build_bounds()
        ttmax, ttmin = exp.two_theta_max()
        self.ax, h = exp.show_reciprocal_space_plane(
            ttmax=ttmax, ttmin=ttmin, idir=paradir, ndir=normdir, scalef=100, move=move
        )
        for i in samples:
            exp = DAF(*mode)
            exp.set_material(str(i))
            exp.set_exp_conditions(
                idir=idir,
                ndir=ndir,
                rdir=rdir,
                en=dict_args["PV_energy"] - dict_args["energy_offset"],
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
            exp.build_xrd_experiment()
            exp.build_bounds()
            ttmax, ttmin = exp.two_theta_max()
            ax, h2 = exp.show_reciprocal_space_plane(
                ttmax=ttmax,
                ttmin=ttmin,
                idir=paradir,
                ndir=normdir,
                scalef=100,
                ax=self.ax,
                move=move,
            )

        super().__init__(self.ax.figure)
