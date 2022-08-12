#!/usr/bin/env python3

import xrayutilities as xu
import numpy as np
import pandas as pd
from tqdm import tqdm

from daf.utils.print_utils import TablePrinter
from daf.core.reciprocal_map import ReciprocalMapWindow
from daf.core.minimization import MinimizationProc


class DAF(MinimizationProc, ReciprocalMapWindow):

    COLUMNS = {
        1: {
            0: "--",
            1: "del_fix",
            2: "nu_fix",
            3: "qaz_fix",
            4: "naz_fix",
            5: "zone",
            6: "--",
        },
        2: {
            0: "--",
            1: "alpha = beta",
            2: "alpha fix",
            3: "beta fix",
            4: "psi_fix",
            5: "--",
            6: "--",
        },
        3: {
            0: "omega fix",
            1: "eta_fix",
            2: "mu_fix",
            3: "chi_fix",
            4: "phi_fix",
            5: "eta = delta/2",
            6: "mu = nu/2",
        },
        4: {
            0: "--",
            1: "eta_fix",
            2: "mu_fix",
            3: "chi_fix",
            4: "phi_fix",
            5: "--",
            6: "--",
        },
        5: {
            0: "--",
            1: "eta_fix",
            2: "mu_fix",
            3: "chi_fix",
            4: "phi_fix",
            5: "--",
            6: "--",
        },
    }

    def __init__(self, *args):

        self.setup = self.parse_mode_args(args)
        self.handle_constraints()
        self.define_standard_experiment()
        self.define_standard_print_parameters()

    def parse_mode_args(self, mode):
        self.mode = mode

        for i in mode:
            if i not in (0, 1, 2, 3, 4, 5, 6):
                raise ValueError("The values of columns must be between 0 and 6")

        if mode[0] == 0 and mode[1] == 0:
            if len(mode) <= 3:
                raise ValueError(
                    """If de two first columns are set to 0, the columns 4 and 5 must be given"""
                )
            elif mode[3] == 0 or mode[4] == 0:
                raise ValueError(
                    """If de two first columns are set to 0, the columns 4 and 5 must not be 0"""
                )

        if mode[0] == 5:
            raise ("Zone mode was not implemented yet")
        if mode[0] == 6:
            raise ("Energy mode was not implemented yet")

        self.col1 = mode[0]
        self.col2 = mode[1]
        self.col3 = mode[2]

        if len(mode) >= 4:
            self.col4 = mode[3]
        else:
            self.col4 = 0

        if len(mode) == 5:
            self.col5 = mode[4]
        else:
            self.col5 = 0

        return (
            self.COLUMNS[1][self.col1],
            self.COLUMNS[2][self.col2],
            self.COLUMNS[3][self.col3],
            self.COLUMNS[4][self.col4],
            self.COLUMNS[5][self.col5],
        )

    def handle_constraints(self):
        """Logic to set up the constraints based on the given operation mode"""
        angles = {
            "--": "x",
            "del_fix": "Del",
            "nu_fix": "Nu",
            "mu_fix": "Mu",
            "eta_fix": "Eta",
            "chi_fix": "Chi",
            "phi_fix": "Phi",
        }

        cons = {
            "--": "x",
            "qaz_fix": "qaz",
            "naz_fix": "naz",
            "alpha = beta": "aeqb",
            "alpha fix": "alpha",
            "beta fix": "beta",
            "psi_fix": "psi",
            "omega fix": "omega",
            "eta = delta/2": "eta=del/2",
            "mu = nu/2": "mu=nu/2",
        }

        self.motor_constraints = []
        self.pseudo_angle_constraints = []

        for i in range(len(self.setup)):
            if self.setup[i] in angles.keys():
                if i == 0 and self.setup[i] == "--":
                    pass

                elif i == 1 and self.setup[i] == "--":
                    pass

                else:
                    self.motor_constraints.append(angles[self.setup[i]])

            else:
                if self.setup[i] in cons.keys():
                    self.pseudo_angle_constraints.append(cons[self.setup[i]])

        self.fixed_motor_list = []
        for i in self.motor_constraints:
            if i != "x":
                self.fixed_motor_list.append(i)
        if "Mu" in self.fixed_motor_list:
            self.Mu_bound = 0
        else:
            self.Mu_bound = (-180, 180)
        if "Eta" in self.fixed_motor_list:
            self.Eta_bound = 0
        else:
            self.Eta_bound = (-180, 180)
        if "Chi" in self.fixed_motor_list:
            self.Chi_bound = 0
        else:
            self.Chi_bound = (-5, 95)
        if "Phi" in self.fixed_motor_list:
            self.Phi_bound = 0
        else:
            self.Phi_bound = (30, 400)
        if "Nu" in self.fixed_motor_list:
            self.Nu_bound = 0
        else:
            self.Nu_bound = (-180, 180)
        if "Del" in self.fixed_motor_list:
            self.Del_bound = 0
        else:
            self.Del_bound = (-180, 180)

        self.pseudo_constraints_w_value_list = [
            (self.pseudo_angle_constraints[i], 0)
            if self.pseudo_angle_constraints[i] not in ("eta=del/2", "mu=nu/2", "aeqb")
            else (self.pseudo_angle_constraints[i], "--")
            for i in range(len(self.pseudo_angle_constraints))
        ]

    def define_standard_experiment(self):
        self.nref = (0, 0, 1)
        self.idir = (0, 0, 1)
        self.ndir = (1, 1, 0)
        self.sampleor = "x+"
        self.en = 8000
        self.lam = xu.en2lam(self.en)
        self.posrestrict = ()
        self.negrestrict = ()
        self.fcsv = "{0:.4f}".format
        self.U = np.identity(3)
        # self.qconv = xu.experiment.QConversion(['y+', 'x-', 'z+', 'x-'], ['y+', 'x-'], [0, 0, 1]) # Sirius coordinate axes system
        self.qconv = xu.experiment.QConversion(
            ["x+", "z-", "y+", "z-"], ["x+", "z-"], [0, 1, 0]
        )  # Coordenada YOU 1999

    def define_standard_print_parameters(self):
        self.space = 12
        self.marker = "-"
        self.column_marker = "|"
        self.center = (
            self.column_marker + "{:^" + str(self.space - 2) + "}" + self.column_marker
        )
        self.roundfit = 5
        self.centshow = "{:^" + str(16 - 2) + "}"

    def show(self, sh, ident=3, space=20):

        self.centshow = "{:^" + str(space - 2) + "}"

        dprint = {
            "x": "--",
            "Mu": self.Mu_bound,
            "Eta": self.Eta_bound,
            "Chi": self.Chi_bound,
            "Phi": self.Phi_bound,
            "Nu": self.Nu_bound,
            "Del": self.Del_bound,
        }

        lb = lambda x: "{:.5f}".format(float(x))

        self.forprint = self.pseudo_constraints_w_value_list.copy()

        if self.col1 in (1, 2):
            if self.col1 == 1:
                self.forprint.insert(0, (self.setup[0], self.Del_bound))
            elif self.col1 == 2:
                self.forprint.insert(0, (self.setup[0], self.Nu_bound))
            for i in self.motor_constraints:
                if i not in ("Del", "Nu"):
                    self.forprint.append((i, dprint[i]))
            if self.col2 == 0:
                self.forprint.insert(1, ("XD", "--"))

        else:
            if self.col1 == 0 and self.col2 == 0:

                self.forprint.insert(0, ("XD", "--"))
                self.forprint.insert(0, ("XD", "--"))

                for i in self.motor_constraints:
                    self.forprint.append((i, dprint[i]))

            elif self.col1 == 0:

                self.forprint.insert(0, ("XD", "--"))

                for i in self.motor_constraints:
                    self.forprint.append((i, dprint[i]))

            elif self.col2 == 0:
                self.forprint.insert(1, ("XD", "--"))
                # self.forprint.pop()

                for i in self.motor_constraints:
                    self.forprint.append((i, dprint[i]))
            else:
                for i in self.motor_constraints:
                    self.forprint.append((i, dprint[i]))

        conscols = [self.col1, self.col2, self.col3, self.col4, self.col5]
        experiment_list = [
            self.sampleor,
            lb(self.lam),
            lb(self.en / 1000),
            "["
            + str(self.idir[0])
            + ","
            + str(self.idir[1])
            + ","
            + str(self.idir[2])
            + "]",
            "["
            + str(self.ndir[0])
            + ","
            + str(self.ndir[1])
            + ","
            + str(self.ndir[2])
            + "]",
            "["
            + str(self.nref[0])
            + ","
            + str(self.nref[1])
            + ","
            + str(self.nref[2])
            + "]",
        ]
        sample_info = [
            self.samp.name,
            self.samp.a,
            self.samp.b,
            self.samp.c,
            self.samp.alpha,
            self.samp.beta,
            self.samp.gamma,
        ]

        fmt = [
            ("", "ident", ident),
            ("", "col1", space),
            ("", "col2", space),
            ("", "col3", space),
            ("", "col4", space),
            ("", "col5", space),
            ("", "col6", space),
        ]

        if sh == "mode":

            data = [
                {
                    "ident": "",
                    "col1": self.centshow.format("MODE"),
                    "col2": self.centshow.format(self.setup[0]),
                    "col3": self.centshow.format(self.setup[1]),
                    "col4": self.centshow.format(self.setup[2]),
                    "col5": self.centshow.format(self.setup[3]),
                    "col6": self.centshow.format(self.setup[4]),
                },
                {
                    "ident": "",
                    "col1": self.centshow.format(
                        str(self.col1)
                        + str(self.col2)
                        + str(self.col3)
                        + str(self.col4)
                        + str(self.col5)
                    ),
                    "col2": self.centshow.format(self.forprint[0][1]),
                    "col3": self.centshow.format(self.forprint[1][1]),
                    "col4": self.centshow.format(self.forprint[2][1]),
                    "col5": self.centshow.format(self.forprint[3][1]),
                    "col6": self.centshow.format(self.forprint[4][1]),
                },
            ]

            return TablePrinter(fmt, ul="")(data)

        if sh == "expt":

            data = [
                {
                    "col1": self.centshow.format("Sampleor"),
                    "col2": self.centshow.format("WaveLength (angstrom)"),
                    "col3": self.centshow.format("Energy (keV)"),
                    "col4": self.centshow.format("Incidence Dir"),
                    "col5": self.centshow.format("Normal Dir"),
                    "col6": self.centshow.format("Reference Dir"),
                },
                {
                    "col1": self.centshow.format(self.sampleor),
                    "col2": self.centshow.format(lb(str(self.lam))),
                    "col3": self.centshow.format(str(lb(self.en / 1000))),
                    "col4": self.centshow.format(
                        str(self.idir[0])
                        + " "
                        + str(self.idir[1])
                        + " "
                        + str(self.idir[2])
                    ),
                    "col5": self.centshow.format(
                        str(self.ndir[0])
                        + " "
                        + str(self.ndir[1])
                        + " "
                        + str(self.ndir[2])
                    ),
                    "col6": self.centshow.format(
                        str(self.nref[0])
                        + " "
                        + str(self.nref[1])
                        + " "
                        + str(self.nref[2])
                    ),
                },
            ]

            return TablePrinter(fmt, ul="")(data)

        if sh == "sample":

            fmt = [
                ("", "ident", ident),
                ("", "col1", space),
                ("", "col2", space),
                ("", "col3", space),
                ("", "col4", space),
                ("", "col5", space),
                ("", "col6", space),
                ("", "col7", space),
            ]

            data = [
                {
                    "col1": self.centshow.format("Sample"),
                    "col2": self.centshow.format("a"),
                    "col3": self.centshow.format("b"),
                    "col4": self.centshow.format("c"),
                    "col5": self.centshow.format("Alpha"),
                    "col6": self.centshow.format("Beta"),
                    "col7": self.centshow.format("Gamma"),
                },
                {
                    "col1": self.centshow.format(self.samp.name),
                    "col2": self.centshow.format(lb(str(self.samp.a))),
                    "col3": self.centshow.format(str(lb(self.samp.b))),
                    "col4": self.centshow.format(str(lb(self.samp.c))),
                    "col5": self.centshow.format(str(lb(self.samp.alpha))),
                    "col6": self.centshow.format(str(lb(self.samp.beta))),
                    "col7": self.centshow.format(str(lb(self.samp.gamma))),
                },
            ]

            return TablePrinter(fmt, ul="")(data)

        if sh == "gui":

            return self.setup, conscols, self.forprint, experiment_list, sample_info

    def set_hkl(self, HKL):

        self.hkl = HKL

    def set_material(self, sample, *args):

        self.predefined_samples = {
            "Si": xu.materials.Si,
            "Al": xu.materials.Al,
            "Co": xu.materials.Co,
            "Cu": xu.materials.Cu,
            "Cr": xu.materials.Cr,
            "Fe": xu.materials.Fe,
            "Ge": xu.materials.Ge,
            "Sn": xu.materials.Sn,
            "LaB6": xu.materials.LaB6,
            "Al2O3": xu.materials.Al2O3,
            "C": xu.materials.C,
            "C_HOPG": xu.materials.C_HOPG,
            "InAs": xu.materials.InAs,
            "InP": xu.materials.InP,
            "InSb": xu.materials.InSb,
            "GaP": xu.materials.GaP,
            "GaAs": xu.materials.GaAs,
            "AlAs": xu.materials.AlAs,
            "GaSb": xu.materials.GaSb,
            "GaAsWZ": xu.materials.GaAsWZ,
            "GaAs4H": xu.materials.GaAs4H,
            "GaPWZ": xu.materials.GaPWZ,
            "InPWZ": xu.materials.InPWZ,
            "InAs4H": xu.materials.InAs4H,
            "InSbWZ": xu.materials.InSbWZ,
            "InSb4H": xu.materials.InSb4H,
            "PbTe": xu.materials.PbTe,
            "PbSe": xu.materials.PbSe,
            "CdTe": xu.materials.CdTe,
            "CdSe": xu.materials.CdSe,
            "CdSe_ZB": xu.materials.CdSe_ZB,
            "HgSe": xu.materials.HgSe,
            "NaCl": xu.materials.NaCl,
            "MgO": xu.materials.MgO,
            "GaN": xu.materials.GaN,
            "BaF2": xu.materials.BaF2,
            "SrF2": xu.materials.SrF2,
            "CaF2": xu.materials.CaF2,
            "MnO": xu.materials.MnO,
            "MnTe": xu.materials.MnTe,
            "GeTe": xu.materials.GeTe,
            "SnTe": xu.materials.SnTe,
            "Au": xu.materials.Au,
            "Ti": xu.materials.Ti,
            "Mo": xu.materials.Mo,
            "Ru": xu.materials.Ru,
            "Rh": xu.materials.Rh,
            "V": xu.materials.V,
            "Ta": xu.materials.Ta,
            "Nb": xu.materials.Nb,
            "Pt": xu.materials.Pt,
            "Ag2Se": xu.materials.Ag2Se,
            "TiO2": xu.materials.TiO2,
            "MnO2": xu.materials.MnO2,
            "VO2_Rutile": xu.materials.VO2_Rutile,
            "VO2_Baddeleyite": xu.materials.VO2_Baddeleyite,
            "SiO2": xu.materials.SiO2,
            "In": xu.materials.In,
            "Sb": xu.materials.Sb,
            "Ag": xu.materials.Ag,
            "SnAlpha": xu.materials.SnAlpha,
            "CaTiO3": xu.materials.CaTiO3,
            "SrTiO3": xu.materials.SrTiO3,
            "BaTiO3": xu.materials.BaTiO3,
            "FeO": xu.materials.FeO,
            "CoO": xu.materials.CoO,
            "Fe3O4": xu.materials.Fe3O4,
            "Co3O4": xu.materials.Co3O4,
            "FeRh": xu.materials.FeRh,
            "Ir20Mn80": xu.materials.Ir20Mn80,
            "CoFe": xu.materials.CoFe,
            "CoGa": xu.materials.CoFe,
            "CuMnAs": xu.materials.CuMnAs,
            "Mn3Ge_cub": xu.materials.Mn3Ge_cub,
            "Mn3Ge": xu.materials.Mn3Ge,
            "Pt3Cr": xu.materials.Pt3Cr,
            "TiN": xu.materials.TiN,
        }

        if sample in self.predefined_samples.keys():
            self.samp = self.predefined_samples[sample]

        else:
            self.samp = xu.materials.Crystal(
                str(sample),
                xu.materials.SGLattice(
                    1, args[0], args[1], args[2], args[3], args[4], args[5]
                ),
            )

    def set_constraints(self, *args, setineq=None, **kwargs):
        """Set constraints values to motor and pseudo angle constraints. They should be passed as Keyword Arguments"""
        self.pseudo_constraints_w_value_list = list()

        if "Mu" in kwargs.keys() and "Mu" in self.fixed_motor_list:
            self.Mu_bound = kwargs["Mu"]

        if "Eta" in kwargs.keys() and "Eta" in self.fixed_motor_list:
            self.Eta_bound = kwargs["Eta"]

        if "Chi" in kwargs.keys() and "Chi" in self.fixed_motor_list:
            self.Chi_bound = kwargs["Chi"]

        if "Phi" in kwargs.keys() and "Phi" in self.fixed_motor_list:
            self.Phi_bound = kwargs["Phi"]

        if "Nu" in kwargs.keys() and "Nu" in self.fixed_motor_list:
            self.Nu_bound = kwargs["Nu"]

        if "Del" in kwargs.keys() and "Del" in self.fixed_motor_list:
            self.Del_bound = kwargs["Del"]

        if "qaz" in kwargs.keys() and "qaz" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("qaz", kwargs["qaz"]))

        if "naz" in kwargs.keys() and "naz" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("naz", kwargs["naz"]))

        if "alpha" in kwargs.keys() and "alpha" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("alpha", kwargs["alpha"]))

        if "beta" in kwargs.keys() and "beta" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("beta", kwargs["beta"]))

        if "psi" in kwargs.keys() and "psi" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("psi", kwargs["psi"]))

        if "omega" in kwargs.keys() and "omega" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("omega", kwargs["omega"]))

        if "aeqb" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("aeqb", "--"))

        if "eta=del/2" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("eta=del/2", "--"))

        if "mu=nu/2" in self.pseudo_angle_constraints:
            self.pseudo_constraints_w_value_list.append(("mu=nu/2", "--"))

        self.motor_bounds_list = (
            self.Mu_bound,
            self.Eta_bound,
            self.Chi_bound,
            self.Phi_bound,
            self.Nu_bound,
            self.Del_bound,
        )

        return self.motor_bounds_list, self.pseudo_constraints_w_value_list

    def set_circle_constrain(self, **kwargs):
        """Deprecated, check and remove"""
        if "Mu" in kwargs.keys() and "Mu" not in self.fixed_motor_list:
            self.Mu_bound = kwargs["Mu"]

        if "Eta" in kwargs.keys() and "Eta" not in self.fixed_motor_list:
            self.Eta_bound = kwargs["Eta"]

        if "Chi" in kwargs.keys() and "Chi" not in self.fixed_motor_list:
            self.Chi_bound = kwargs["Chi"]

        if "Phi" in kwargs.keys() and "Phi" not in self.fixed_motor_list:
            self.Phi_bound = kwargs["Phi"]

        if "Nu" in kwargs.keys() and "Nu" not in self.fixed_motor_list:
            self.Nu_bound = kwargs["Nu"]

        if "Del" in kwargs.keys() and "Del" not in self.fixed_motor_list:
            self.Del_bound = kwargs["Del"]

    def set_exp_conditions(
        self, idir=(0, 0, 1), ndir=(1, 1, 0), rdir=(0, 0, 1), sampleor="x+", en=8000
    ):

        self.idir = idir
        self.ndir = ndir
        self.nref = rdir
        self.sampleor = sampleor

        ENWL = en

        if ENWL > 50:
            self.en = ENWL
            self.lam = xu.en2lam(en)
        else:
            self.lam = ENWL
            self.en = xu.lam2en(self.lam)

    def set_print_options(self, marker="-", column_marker="|", space=12):

        self.marker = marker
        self.column_marker = column_marker

        if space > 10:
            if space % 2 == 0:
                self.space = space
            elif space % 2 == 0:
                self.space = space - 1
        else:
            self.space = 10

        self.center = (
            self.column_marker + "{:^" + str(self.space - 2) + "}" + self.column_marker
        )

        if self.space > 10:
            self.roundfit = int(4 + ((self.space - 10) / 2))
        else:
            self.roundfit = 4

    def __str__(self):

        lb = lambda x: "{:.5f}".format(float(x))

        if self.isscan:
            return repr(self.formscantxt)

        else:
            dprint = {
                "x": "--",
                "Mu": self.Mu_bound,
                "Eta": self.Eta_bound,
                "Chi": self.Chi_bound,
                "Phi": self.Phi_bound,
                "Nu": self.Nu_bound,
                "Del": self.Del_bound,
            }

            self.forprint = self.pseudo_constraints_w_value_list.copy()

            if self.col1 in (1, 2):
                if self.col1 == 1:
                    self.forprint.insert(0, (self.setup[0], self.Del_bound))
                elif self.col1 == 2:
                    self.forprint.insert(0, (self.setup[0], self.Nu_bound))
                for i in self.motor_constraints:
                    if i not in ("Del", "Nu"):
                        self.forprint.append((i, dprint[i]))
                if self.col2 == 0:
                    self.forprint.insert(1, ("XD", "--"))

            else:
                if self.col1 == 0 and self.col2 == 0:

                    self.forprint.insert(0, ("XD", "--"))
                    self.forprint.insert(0, ("XD", "--"))

                    for i in self.motor_constraints:
                        self.forprint.append((i, dprint[i]))

                elif self.col1 == 0:

                    self.forprint.insert(0, ("XD", "--"))

                    for i in self.motor_constraints:
                        self.forprint.append((i, dprint[i]))

                elif self.col2 == 0:
                    self.forprint.insert(1, ("XD", "--"))
                    # self.forprint.pop()

                    for i in self.motor_constraints:
                        self.forprint.append((i, dprint[i]))
                else:
                    for i in self.motor_constraints:
                        self.forprint.append((i, dprint[i]))

            self.forprint = [
                (i[0], lb(i[1])) if i[1] != "--" else (i[0], i[1])
                for i in self.forprint
            ]

            data = [
                {
                    "col1": self.center.format("MODE"),
                    "col2": self.center.format(self.setup[0]),
                    "col3": self.center.format(self.setup[1]),
                    "col4": self.center.format(self.setup[2]),
                    "col5": self.center.format(self.setup[3]),
                    "col6": self.center.format(self.setup[4]),
                    "col7": self.center.format("Error"),
                },
                {
                    "col1": self.center.format(
                        str(self.col1)
                        + str(self.col2)
                        + str(self.col3)
                        + str(self.col4)
                        + str(self.col5)
                    ),
                    "col2": self.center.format(self.forprint[0][1]),
                    "col3": self.center.format(self.forprint[1][1]),
                    "col4": self.center.format(self.forprint[2][1]),
                    "col5": self.center.format(self.forprint[3][1]),
                    "col6": self.center.format(self.forprint[4][1]),
                    "col7": self.center.format("%.3g" % self.qerror),
                },
                {
                    "col1": self.marker * self.space,
                    "col2": self.marker * self.space,
                    "col3": self.marker * self.space,
                    "col4": self.marker * self.space,
                    "col5": self.marker * self.space,
                    "col6": self.marker * self.space,
                    "col7": self.marker * self.space,
                },
                {
                    "col1": self.center.format("H"),
                    "col2": self.center.format("K"),
                    "col3": self.center.format("L"),
                    "col4": self.center.format("Ref vector"),
                    "col5": self.center.format("Energy (keV)"),
                    "col6": self.center.format("WL (angstrom)"),
                    "col7": self.center.format("Sample"),
                },
                {
                    "col1": self.center.format(str(lb(self.hkl_calc[0]))),
                    "col2": self.center.format(str(lb(self.hkl_calc[1]))),
                    "col3": self.center.format(str(lb(self.hkl_calc[2]))),
                    "col4": self.center.format(
                        str(self.nref[0])
                        + " "
                        + str(self.nref[1])
                        + " "
                        + str(self.nref[2])
                    ),
                    "col5": self.center.format(lb(self.en / 1000)),
                    "col6": self.center.format(lb(self.lam)),
                    "col7": self.center.format(self.samp.name),
                },
                {
                    "col1": self.marker * self.space,
                    "col2": self.marker * self.space,
                    "col3": self.marker * self.space,
                    "col4": self.marker * self.space,
                    "col5": self.marker * self.space,
                    "col6": self.marker * self.space,
                    "col7": self.marker * self.space,
                },
                {
                    "col1": self.center.format("Qx"),
                    "col2": self.center.format("Qy"),
                    "col3": self.center.format("Qz"),
                    "col4": self.center.format("|Q|"),
                    "col5": self.center.format("Exp 2theta"),
                    "col6": self.center.format("Dhkl"),
                    "col7": self.center.format("FHKL (Base)"),
                },
                {
                    "col1": self.center.format(str(lb(self.Qshow[0]))),
                    "col2": self.center.format(str(lb(self.Qshow[1]))),
                    "col3": self.center.format(str(lb(self.Qshow[2]))),
                    "col4": self.center.format(lb(self.Qnorm)),
                    "col5": self.center.format(lb(self.ttB1)),
                    "col6": self.center.format(lb(self.dhkl)),
                    "col7": self.center.format(lb(self.FHKL)),
                },
                {
                    "col1": self.marker * self.space,
                    "col2": self.marker * self.space,
                    "col3": self.marker * self.space,
                    "col4": self.marker * self.space,
                    "col5": self.marker * self.space,
                    "col6": self.marker * self.space,
                    "col7": self.marker * self.space,
                },
                {
                    "col1": self.center.format("Alpha"),
                    "col2": self.center.format("Beta"),
                    "col3": self.center.format("Psi"),
                    "col4": self.center.format("Tau"),
                    "col5": self.center.format("Qaz"),
                    "col6": self.center.format("Naz"),
                    "col7": self.center.format("Omega"),
                },
                {
                    "col1": self.center.format(lb(self.alphain)),
                    "col2": self.center.format(lb(self.betaout)),
                    "col3": self.center.format(lb(self.psipseudo)),
                    "col4": self.center.format(lb(self.taupseudo)),
                    "col5": self.center.format(lb(self.qaz)),
                    "col6": self.center.format(lb(self.naz)),
                    "col7": self.center.format(lb(self.omega)),
                },
                {
                    "col1": self.marker * self.space,
                    "col2": self.marker * self.space,
                    "col3": self.marker * self.space,
                    "col4": self.marker * self.space,
                    "col5": self.marker * self.space,
                    "col6": self.marker * self.space,
                    "col7": self.marker * self.space,
                },
                {
                    "col1": self.center.format("Del"),
                    "col2": self.center.format("Eta"),
                    "col3": self.center.format("Chi"),
                    "col4": self.center.format("Phi"),
                    "col5": self.center.format("Nu"),
                    "col6": self.center.format("Mu"),
                    "col7": self.center.format("--"),
                },
                {
                    "col1": self.center.format(lb(self.Del)),
                    "col2": self.center.format(lb(self.Eta)),
                    "col3": self.center.format(lb(self.Chi)),
                    "col4": self.center.format(lb(self.Phi)),
                    "col5": self.center.format(lb(self.Nu)),
                    "col6": self.center.format(lb(self.Mu)),
                    "col7": self.center.format("--"),
                },
                {
                    "col1": self.marker * self.space,
                    "col2": self.marker * self.space,
                    "col3": self.marker * self.space,
                    "col4": self.marker * self.space,
                    "col5": self.marker * self.space,
                    "col6": self.marker * self.space,
                    "col7": self.marker * self.space,
                },
            ]

            fmt = [
                ("", "col1", self.space),
                ("", "col2", self.space),
                ("", "col3", self.space),
                ("", "col4", self.space),
                ("", "col5", self.space),
                ("", "col6", self.space),
                ("", "col7", self.space),
            ]

            return TablePrinter(fmt, ul=self.marker)(data)

    def __call__(self, *args, **kwargs):
        """
        wrapper function for motor_angles(...)
        """
        return self.motor_angles(*args, **kwargs)

    def scan_generator(self, hkli, hklf, points):

        ini = np.array(hkli)
        fin = np.array(hklf)
        scanlist = np.linspace(hkli, hklf, points)
        return scanlist

    def set_U(self, U):

        self.U = U

    def calcUB(self):

        return self.U.dot(self.samp.B)

    def build_xrd_experiment(self):
        """Build the XRD experiment"""
        self.hrxrd = xu.HXRD(
            self.idir, self.ndir, en=self.en, qconv=self.qconv, sampleor=self.sampleor
        )

    def build_bounds(self):
        """Build the bounds to be used in the minimization"""
        self.bounds = (
            self.Mu_bound,
            self.Eta_bound,
            self.Chi_bound,
            self.Phi_bound,
            self.Nu_bound,
            self.Del_bound,
        )

    def calc_from_angs(self, Mu, Eta, Chi, Phi, Nu, Del):

        hkl = self.hrxrd.Ang2HKL(
            Mu, Eta, Chi, Phi, Nu, Del, mat=self.samp, en=self.en, U=self.U
        )
        self.hkl = hkl
        return hkl

    def export_angles(self):

        return [
            self.Mu,
            self.Eta,
            self.Chi,
            self.Phi,
            self.Nu,
            self.Del,
            self.ttB1,
            self.tB1,
            self.alphain,
            self.qaz,
            self.naz,
            self.taupseudo,
            self.psipseudo,
            self.betaout,
            self.omega,
            self.hkl_calc,
            "{0:.2e}".format(self.qerror),
        ]

    def scan(
        self,
        hkli,
        hklf,
        points,
        diflimit=0.1,
        write=False,
        name="testscan.txt",
        sep=",",
        startvalues=[0, 0, 0, 0, 0, 0],
    ):

        scl = self.scan_generator(hkli, hklf, points + 1)
        angslist = list()
        for i in tqdm(scl):
            self.hkl = i
            a, b = self.motor_angles(self, sv=startvalues)
            angslist.append(b)
            teste = np.abs(np.array(a[:6]) - np.array(startvalues))

            if np.max(teste) > diflimit and diflimit != 0:
                raise ("Exceded max limit of angles variation")

            if float(a[-1]) > 1e-5:
                raise ("qerror is too big, process failed")

            startvalues = a[:6]

            pd.DataFrame(
                [b],
                columns=[
                    "Mu",
                    "Eta",
                    "Chi",
                    "Phi",
                    "Nu",
                    "Del",
                    "2theta",
                    "theta",
                    "alpha",
                    "qaz",
                    "naz",
                    "tau",
                    "psi",
                    "beta",
                    "omega",
                    "H",
                    "K",
                    "L",
                    "Error",
                ],
            ).to_csv(".my_scan_counter.csv", mode="a", header=False)

        self.isscan = True

        self.formscantxt = pd.DataFrame(
            angslist,
            columns=[
                "Mu",
                "Eta",
                "Chi",
                "Phi",
                "Nu",
                "Del",
                "2theta",
                "theta",
                "alpha",
                "qaz",
                "naz",
                "tau",
                "psi",
                "beta",
                "omega",
                "H",
                "K",
                "L",
                "Error",
            ],
        )

        self.formscan = self.formscantxt[
            ["Mu", "Eta", "Chi", "Phi", "Nu", "Del", "Error"]
        ]

        scan_points = [i[:6] for i in angslist]  ## Get only mu, eta, chi, phi, nu, del

        if write:
            self.formscantxt.to_csv(name, sep=sep)

        pd.options.display.max_rows = None
        pd.options.display.max_columns = 0

        return self.formscantxt
