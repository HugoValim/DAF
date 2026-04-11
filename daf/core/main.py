#!/usr/bin/env python3

import xrayutilities as xu
import numpy as np
import pandas as pd
from tqdm import tqdm

from daf.core.mode_parser import ModeParser, PREDEFINED_MATERIALS
from daf.utils.print_utils import TablePrinter
from daf.core.reciprocal_map import ReciprocalMapWindow
from daf.core.minimization import MinimizationProc


class DAF(MinimizationProc, ReciprocalMapWindow):

    predefined_samples = PREDEFINED_MATERIALS

    def __init__(self, *args):
        parser = ModeParser(args)
        self.setup = parser.setup
        self.col1 = parser.col1
        self.col2 = parser.col2
        self.col3 = parser.col3
        self.col4 = parser.col4
        self.col5 = parser.col5
        self.motor_constraints = parser.motor_constraints
        self.pseudo_angle_constraints = parser.pseudo_angle_constraints
        self.fixed_motor_list = parser.fixed_motor_list
        self.Mu_bound = parser.Mu_bound
        self.Eta_bound = parser.Eta_bound
        self.Chi_bound = parser.Chi_bound
        self.Phi_bound = parser.Phi_bound
        self.Nu_bound = parser.Nu_bound
        self.Del_bound = parser.Del_bound
        self.pseudo_constraints_w_value_list = parser.pseudo_constraints_w_value_list
        self.define_standard_experiment()
        self.define_standard_print_parameters()

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
        self.qconv = xu.experiment.QConversion(
            ["x+", "z-", "y+", "z-"], ["x+", "z-"], [0, 1, 0]
        )

    def define_standard_print_parameters(self):
        self.space = 12
        self.marker = "-"
        self.column_marker = "|"
        self.center = (
            self.column_marker + "{:^" + str(self.space - 2) + "}" + self.column_marker
        )
        self.roundfit = 5
        self.centshow = "{:^" + str(16 - 2) + "}"

    def _build_forprint_rows(self, dprint: dict, col1: int, col2: int) -> list:
        """Build constraint rows for display table.

        Shared logic between show() and __str__().
        """
        rows = self.pseudo_constraints_w_value_list.copy()

        if col1 in (1, 2):
            if col1 == 1:
                rows.insert(0, (self.setup[0], self.Del_bound))
            elif col1 == 2:
                rows.insert(0, (self.setup[0], self.Nu_bound))
            for i in self.motor_constraints:
                if i not in ("Del", "Nu"):
                    rows.append((i, dprint[i]))
            if col2 == 0:
                rows.insert(1, ("XD", "--"))

        else:
            if col1 == 0 and col2 == 0:
                rows.insert(0, ("XD", "--"))
                rows.insert(0, ("XD", "--"))
                for i in self.motor_constraints:
                    rows.append((i, dprint[i]))
            elif col1 == 0:
                rows.insert(0, ("XD", "--"))
                for i in self.motor_constraints:
                    rows.append((i, dprint[i]))
            elif col2 == 0:
                rows.insert(1, ("XD", "--"))
                for i in self.motor_constraints:
                    rows.append((i, dprint[i]))
            else:
                for i in self.motor_constraints:
                    rows.append((i, dprint[i]))

        return rows

    def show(self, sh, ident=3, space=20):
        lb = lambda x: "{:.5f}".format(float(x))

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

        self.forprint = self._build_forprint_rows(dprint, self.col1, self.col2)

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
        if sample in PREDEFINED_MATERIALS:
            self.samp = PREDEFINED_MATERIALS[sample]
        else:
            self.samp = xu.materials.Crystal(
                str(sample),
                xu.materials.SGLattice(
                    1, args[0], args[1], args[2], args[3], args[4], args[5]
                ),
            )

    MOTOR_BOUNDS_MAP = {
        "Mu": "Mu_bound",
        "Eta": "Eta_bound",
        "Chi": "Chi_bound",
        "Phi": "Phi_bound",
        "Nu": "Nu_bound",
        "Del": "Del_bound",
    }

    def set_constraints(self, *args, setineq=None, **kwargs):
        """Set constraints values to motor and pseudo angle constraints."""
        self.pseudo_constraints_w_value_list = list()

        for motor, bound_attr in self.MOTOR_BOUNDS_MAP.items():
            if motor in kwargs and motor in self.fixed_motor_list:
                setattr(self, bound_attr, kwargs[motor])

        for name in ("qaz", "naz", "alpha", "beta", "psi", "omega"):
            if name in kwargs and name in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append((name, kwargs[name]))

        for name in ("aeqb", "eta=del/2", "mu=nu/2"):
            if name in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append((name, "--"))

        self.motor_bounds_list = tuple(
            getattr(self, attr) for attr in self.MOTOR_BOUNDS_MAP.values()
        )
        return self.motor_bounds_list, self.pseudo_constraints_w_value_list

    def set_circle_constrain(self, **kwargs):
        """Deprecated, check and remove"""
        for motor, bound_attr in self.MOTOR_BOUNDS_MAP.items():
            if motor in kwargs and motor not in self.fixed_motor_list:
                setattr(self, bound_attr, kwargs[motor])

    def set_exp_conditions(
        self, idir=(0, 0, 1), ndir=(1, 1, 0), rdir=(0, 0, 1), sampleor="x+", en=8000
    ):
        self.idir = idir
        self.ndir = ndir
        self.nref = rdir
        self.sampleor = sampleor

        if en > 50:
            self.en = en
            self.lam = xu.en2lam(en)
        else:
            self.lam = en
            self.en = xu.lam2en(self.lam)

    def set_print_options(self, marker="-", column_marker="|", space=12):
        self.marker = marker
        self.column_marker = column_marker

        if space > 10:
            self.space = space if space % 2 == 0 else space - 1
        else:
            self.space = 10

        self.center = (
            self.column_marker + "{:^" + str(self.space - 2) + "}" + self.column_marker
        )
        self.roundfit = int(4 + ((self.space - 10) / 2)) if self.space > 10 else 4

    def __str__(self):
        lb = lambda x: "{:.5f}".format(float(x))

        if self.isscan:
            return repr(self.formscantxt)

        dprint = {
            "x": "--",
            "Mu": self.Mu_bound,
            "Eta": self.Eta_bound,
            "Chi": self.Chi_bound,
            "Phi": self.Phi_bound,
            "Nu": self.Nu_bound,
            "Del": self.Del_bound,
        }

        self.forprint = self._build_forprint_rows(dprint, self.col1, self.col2)

        self.forprint = [
            (i[0], lb(i[1])) if i[1] != "--" else (i[0], i[1])
            for i in self.forprint
        ]

        data = [
            {"col1": self.center.format("MODE"),
             "col2": self.center.format(self.setup[0]),
             "col3": self.center.format(self.setup[1]),
             "col4": self.center.format(self.setup[2]),
             "col5": self.center.format(self.setup[3]),
             "col6": self.center.format(self.setup[4]),
             "col7": self.center.format("Error")},
            {"col1": self.center.format(
                str(self.col1) + str(self.col2) + str(self.col3) + str(self.col4) + str(self.col5)),
             "col2": self.center.format(self.forprint[0][1]),
             "col3": self.center.format(self.forprint[1][1]),
             "col4": self.center.format(self.forprint[2][1]),
             "col5": self.center.format(self.forprint[3][1]),
             "col6": self.center.format(self.forprint[4][1]),
             "col7": self.center.format("%.3g" % self.qerror)},
            *self._separator_row(),
            {"col1": self.center.format("H"), "col2": self.center.format("K"),
             "col3": self.center.format("L"), "col4": self.center.format("Ref vector"),
             "col5": self.center.format("Energy (keV)"), "col6": self.center.format("WL (angstrom)"),
             "col7": self.center.format("Sample")},
            {"col1": self.center.format(str(lb(self.hkl_calc[0]))),
             "col2": self.center.format(str(lb(self.hkl_calc[1]))),
             "col3": self.center.format(str(lb(self.hkl_calc[2]))),
             "col4": self.center.format(
                 str(self.nref[0]) + " " + str(self.nref[1]) + " " + str(self.nref[2])),
             "col5": self.center.format(lb(self.en / 1000)),
             "col6": self.center.format(lb(self.lam)),
             "col7": self.center.format(self.samp.name)},
            *self._separator_row(),
            {"col1": self.center.format("Qx"), "col2": self.center.format("Qy"),
             "col3": self.center.format("Qz"), "col4": self.center.format("|Q|"),
             "col5": self.center.format("Exp 2theta"), "col6": self.center.format("Dhkl"),
             "col7": self.center.format("FHKL (Base)")},
            {"col1": self.center.format(str(lb(self.Qshow[0]))),
             "col2": self.center.format(str(lb(self.Qshow[1]))),
             "col3": self.center.format(str(lb(self.Qshow[2]))),
             "col4": self.center.format(lb(self.Qnorm)),
             "col5": self.center.format(lb(self.ttB1)),
             "col6": self.center.format(lb(self.dhkl)),
             "col7": self.center.format(lb(self.FHKL))},
            *self._separator_row(),
            {"col1": self.center.format("Alpha"), "col2": self.center.format("Beta"),
             "col3": self.center.format("Psi"), "col4": self.center.format("Tau"),
             "col5": self.center.format("Qaz"), "col6": self.center.format("Naz"),
             "col7": self.center.format("Omega")},
            {"col1": self.center.format(lb(self.alphain)),
             "col2": self.center.format(lb(self.betaout)),
             "col3": self.center.format(lb(self.psipseudo)),
             "col4": self.center.format(lb(self.taupseudo)),
             "col5": self.center.format(lb(self.qaz)),
             "col6": self.center.format(lb(self.naz)),
             "col7": self.center.format(lb(self.omega))},
            *self._separator_row(),
            {"col1": self.center.format("Del"), "col2": self.center.format("Eta"),
             "col3": self.center.format("Chi"), "col4": self.center.format("Phi"),
             "col5": self.center.format("Nu"), "col6": self.center.format("Mu"),
             "col7": self.center.format("--")},
            {"col1": self.center.format(lb(self.Del)),
             "col2": self.center.format(lb(self.Eta)),
             "col3": self.center.format(lb(self.Chi)),
             "col4": self.center.format(lb(self.Phi)),
             "col5": self.center.format(lb(self.Nu)),
             "col6": self.center.format(lb(self.Mu)),
             "col7": self.center.format("--")},
            *self._separator_row(),
        ]

        fmt = [
            ("", "col1", self.space), ("", "col2", self.space), ("", "col3", self.space),
            ("", "col4", self.space), ("", "col5", self.space), ("", "col6", self.space),
            ("", "col7", self.space),
        ]
        return TablePrinter(fmt, ul=self.marker)(data)

    def _separator_row(self) -> list:
        mk = self.marker * self.space
        return [
            {"col1": mk, "col2": mk, "col3": mk, "col4": mk,
             "col5": mk, "col6": mk, "col7": mk}
        ]

    def __call__(self, *args, **kwargs):
        return self.motor_angles(*args, **kwargs)

    def scan_generator(self, hkli, hklf, points):
        return np.linspace(hkli, hklf, points)

    def set_U(self, U):
        self.U = U

    def calcUB(self):
        return self.U.dot(self.samp.B)

    def build_xrd_experiment(self):
        self.hrxrd = xu.HXRD(
            self.idir, self.ndir, en=self.en, qconv=self.qconv, sampleor=self.sampleor
        )

    def build_bounds(self):
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
            self.Mu, self.Eta, self.Chi, self.Phi, self.Nu, self.Del,
            self.ttB1, self.tB1, self.alphain, self.qaz, self.naz,
            self.taupseudo, self.psipseudo, self.betaout, self.omega,
            self.hkl_calc, "{0:.2e}".format(self.qerror),
        ]

    def scan(
        self, hkli, hklf, points, diflimit=0.1, write=False,
        name="testscan.txt", sep=",", startvalues=[0, 0, 0, 0, 0, 0],
    ):
        scl = self.scan_generator(hkli, hklf, points + 1)
        angslist = []
        for i in tqdm(scl):
            self.hkl = i
            a, b = self.motor_angles(self, sv=startvalues)
            angslist.append(b)
            teste = np.abs(np.array(a[:6]) - np.array(startvalues))

            if np.max(teste) > diflimit and diflimit != 0:
                raise ValueError("Exceded max limit of angles variation")
            if float(a[-1]) > 1e-5:
                raise ValueError("qerror is too big, process failed")

            startvalues = a[:6]

            pd.DataFrame(
                [b],
                columns=["Mu", "Eta", "Chi", "Phi", "Nu", "Del", "2theta", "theta",
                         "alpha", "qaz", "naz", "tau", "psi", "beta", "omega",
                         "H", "K", "L", "Error"],
            ).to_csv(".my_scan_counter.csv", mode="a", header=False)

        self.isscan = True
        self.formscantxt = pd.DataFrame(
            angslist,
            columns=["Mu", "Eta", "Chi", "Phi", "Nu", "Del", "2theta", "theta",
                     "alpha", "qaz", "naz", "tau", "psi", "beta", "omega",
                     "H", "K", "L", "Error"],
        )
        self.formscan = self.formscantxt[["Mu", "Eta", "Chi", "Phi", "Nu", "Del", "Error"]]

        if write:
            self.formscantxt.to_csv(name, sep=sep)

        return self.formscantxt
