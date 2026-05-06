#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

import xrayutilities as xu
import numpy as np
import pandas as pd
from tqdm import tqdm

from daf.core.mode_parser import ModeParser, PREDEFINED_MATERIALS

_SCAN_COLUMNS = [
    "Mu", "Eta", "Chi", "Phi", "Nu", "Del",
    "2theta", "theta", "alpha", "qaz", "naz",
    "tau", "psi", "beta", "omega",
    "H", "K", "L", "Error",
]
from daf.core.reciprocal_map import ReciprocalMapGeometry
from daf.core.minimization import MinimizationProc, _SCAN_QERROR_THRESHOLD
from daf.core.cli_formatting import DAFFormatter, build_forprint_rows, build_dprint


class DAF(MinimizationProc, ReciprocalMapGeometry):

    predefined_samples = PREDEFINED_MATERIALS

    def __init__(self, *args: int) -> None:
        self.mode = ModeParser(args)
        self.define_standard_experiment()
        self._formatter = DAFFormatter()

    def define_standard_experiment(self) -> None:
        self.nref = (0, 0, 1)
        self.idir = (0, 0, 1)
        self.ndir = (1, 1, 0)
        self.sampleor = "x+"
        self.en = 8000
        self.lam = xu.en2lam(self.en)
        self.posrestrict = ()
        self.negrestrict = ()
        self.format_float = "{0:.4f}".format
        self.U = np.identity(3)
        self.qconv = xu.experiment.QConversion(
            ["x+", "z-", "y+", "z-"], ["x+", "z-"], [0, 1, 0]
        )

    def _get_dprint(self):
        """Build dprint dict for constraint display."""
        return build_dprint(self.mode)

    def _build_forprint_rows(self, dprint):
        """Build constraint rows for display table."""
        return build_forprint_rows(self.mode, dprint)

    def show(self, sh: str, ident: int = 3, space: int = 20) -> str | tuple:
        """Show experiment info in different formats."""
        self._formatter.set_print_options(space=space)

        dprint = self._get_dprint()
        self.forprint = self._build_forprint_rows(dprint)

        if sh == "mode":
            return self._formatter.format_mode(self.mode, self.forprint)

        if sh == "expt":
            return self._formatter.format_experiment(
                self.sampleor, self.lam, self.en, self.idir, self.ndir, self.nref
            )

        if sh == "sample":
            return self._formatter.format_sample(self.sample)

        if sh == "gui":
            conscols = list(self.mode.constraint_columns())
            experiment_list = [
                self.sampleor,
                self._formatter._fmt(self.lam),
                self._formatter._fmt(self.en / 1000),
                self.idir,
                self.ndir,
                self.nref,
            ]
            sample_info = [
                self.sample.name,
                self.sample.a,
                self.sample.b,
                self.sample.c,
                self.sample.alpha,
                self.sample.beta,
                self.sample.gamma,
            ]
            return self.setup, conscols, self.forprint, experiment_list, sample_info

    def set_hkl(self, HKL):
        self.hkl = HKL

    def set_material(self, sample: str, *args: float) -> None:
        if sample in PREDEFINED_MATERIALS:
            self.sample = PREDEFINED_MATERIALS[sample]
        else:
            self.sample = xu.materials.Crystal(
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

    # Backward-compatible properties delegating to self.mode
    @property
    def setup(self):
        return self.mode.setup

    @property
    def constraint_col1(self):
        return self.mode.constraint_col1

    @property
    def constraint_col2(self):
        return self.mode.constraint_col2

    @property
    def constraint_col3(self):
        return self.mode.constraint_col3

    @property
    def constraint_col4(self):
        return self.mode.constraint_col4

    @property
    def constraint_col5(self):
        return self.mode.constraint_col5

    @property
    def motor_constraints(self):
        return self.mode.motor_constraints

    @property
    def pseudo_angle_constraints(self):
        return self.mode.pseudo_angle_constraints

    @property
    def fixed_motor_list(self):
        return self.mode.fixed_motor_list

    @property
    def pseudo_constraints_w_value_list(self):
        return self.mode.pseudo_constraints_w_value_list

    @pseudo_constraints_w_value_list.setter
    def pseudo_constraints_w_value_list(self, value):
        self.mode.pseudo_constraints_w_value_list = list(value)

    @property
    def Mu_bound(self):
        return self.mode.bounds_for("Mu")

    @Mu_bound.setter
    def Mu_bound(self, value):
        self.mode.set_bound("Mu", value)

    @property
    def Eta_bound(self):
        return self.mode.bounds_for("Eta")

    @Eta_bound.setter
    def Eta_bound(self, value):
        self.mode.set_bound("Eta", value)

    @property
    def Chi_bound(self):
        return self.mode.bounds_for("Chi")

    @Chi_bound.setter
    def Chi_bound(self, value):
        self.mode.set_bound("Chi", value)

    @property
    def Phi_bound(self):
        return self.mode.bounds_for("Phi")

    @Phi_bound.setter
    def Phi_bound(self, value):
        self.mode.set_bound("Phi", value)

    @property
    def Nu_bound(self):
        return self.mode.bounds_for("Nu")

    @Nu_bound.setter
    def Nu_bound(self, value):
        self.mode.set_bound("Nu", value)

    @property
    def Del_bound(self):
        return self.mode.bounds_for("Del")

    @Del_bound.setter
    def Del_bound(self, value):
        self.mode.set_bound("Del", value)

    @property
    def motor_bounds(self):
        return self.mode.motor_bounds

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
        """Set print formatting options."""
        self._formatter.set_print_options(
            marker=marker, column_marker=column_marker, space=space
        )

    def __str__(self):
        """String representation of current DAF state."""
        if self.isscan:
            return repr(self.formscantxt)

        dprint = self._get_dprint()
        self.forprint = self._build_forprint_rows(dprint)

        self.forprint = [
            (i[0], self._formatter._fmt(i[1])) if i[1] != "--" else (i[0], i[1])
            for i in self.forprint
        ]

        return self._formatter.format_full_status(
            self.mode,
            self.forprint,
            self.qerror,
            self.hkl_calc,
            self.nref,
            self.en,
            self.lam,
            self.sample,
            self.alphain,
            self.betaout,
            self.psipseudo,
            self.taupseudo,
            self.qaz,
            self.naz,
            self.omega,
            self.Del,
            self.Eta,
            self.Chi,
            self.Phi,
            self.Nu,
            self.Mu,
            self.Qshow,
            self.Qnorm,
            self.ttB1,
            self.dhkl,
            self.FHKL,
        )

    def __call__(self, *args, **kwargs):
        return self.motor_angles(*args, **kwargs)

    def scan_generator(self, hkli, hklf, points):
        return np.linspace(hkli, hklf, points)

    def set_U(self, U):
        self.U = U

    def calcUB(self):
        return self.U.dot(self.sample.B)

    def build_xrd_experiment(self):
        self.hrxrd = xu.HXRD(
            self.idir, self.ndir, en=self.en, qconv=self.qconv, sampleor=self.sampleor
        )

    def build_bounds(self):
        self.bounds = self.mode.bounds_tuple

    def calc_from_angs(self, Mu, Eta, Chi, Phi, Nu, Del):
        hkl = self.hrxrd.Ang2HKL(
            Mu, Eta, Chi, Phi, Nu, Del, mat=self.sample, en=self.en, U=self.U
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

    def _build_scan_dataframe(self, angles_list: list) -> pd.DataFrame:
        return pd.DataFrame(angles_list, columns=_SCAN_COLUMNS)

    def scan(
        self,
        hkli,
        hklf,
        points,
        diflimit=0.1,
        write=False,
        name="testscan.txt",
        sep=",",
        startvalues=None,
    ):
        if startvalues is None:
            startvalues = [0, 0, 0, 0, 0, 0]
        scl = self.scan_generator(hkli, hklf, points + 1)
        angslist = []
        for i in tqdm(scl):
            self.hkl = i
            a, b = self.motor_angles(self, start_values=startvalues)
            angslist.append(b)
            teste = np.abs(np.array(a[:6]) - np.array(startvalues))

            if np.max(teste) > diflimit and diflimit != 0:
                raise ValueError("Exceded max limit of angles variation")
            if float(a[-1]) > _SCAN_QERROR_THRESHOLD:
                raise ValueError("qerror is too big, process failed")

            startvalues = a[:6]

            self._build_scan_dataframe([b]).to_csv(
                ".my_scan_counter.csv", mode="a", header=False
            )

        self.isscan = True
        self.formscantxt = self._build_scan_dataframe(angslist)
        self.formscan = self.formscantxt[
            ["Mu", "Eta", "Chi", "Phi", "Nu", "Del", "Error"]
        ]

        if write:
            self.formscantxt.to_csv(name, sep=sep)

        return self.formscantxt
