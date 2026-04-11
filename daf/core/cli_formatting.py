#!/usr/bin/env python3
"""CLI formatting utilities for DAF experiment output."""

from daf.utils.print_utils import TablePrinter


# Default print formatting constants
_DEFAULT_SPACE = 12
_DEFAULT_MARKER = "-"
_DEFAULT_COLUMN_MARKER = "|"


def format_vec(vec):
    """Format a 3-element vector as '[x, y, z]'."""
    return "[" + ", ".join(str(v) for v in vec) + "]"


def build_forprint_rows(pseudo_constraints, motor_constraints, dprint, col1, col2, setup):
    """Build constraint rows for display table.

    Shared logic between show() and __str__().
    """
    rows = list(pseudo_constraints)

    if col1 in (1, 2):
        if col1 == 1:
            rows.insert(0, (setup[0], dprint.get("Del", "--")))
        elif col1 == 2:
            rows.insert(0, (setup[0], dprint.get("Nu", "--")))
        for i in motor_constraints:
            if i not in ("Del", "Nu"):
                rows.append((i, dprint.get(i, "--")))
        if col2 == 0:
            rows.insert(1, ("XD", "--"))

    else:
        if col1 == 0 and col2 == 0:
            rows.insert(0, ("XD", "--"))
            rows.insert(0, ("XD", "--"))
            for i in motor_constraints:
                rows.append((i, dprint.get(i, "--")))
        elif col1 == 0:
            rows.insert(0, ("XD", "--"))
            for i in motor_constraints:
                rows.append((i, dprint.get(i, "--")))
        elif col2 == 0:
            rows.insert(1, ("XD", "--"))
            for i in motor_constraints:
                rows.append((i, dprint.get(i, "--")))
        else:
            for i in motor_constraints:
                rows.append((i, dprint.get(i, "--")))

    return rows


def build_dprint(mu_bound, eta_bound, chi_bound, phi_bound, nu_bound, del_bound):
    """Build the dprint dict mapping motor names to bounds."""
    return {
        "x": "--",
        "Mu": mu_bound,
        "Eta": eta_bound,
        "Chi": chi_bound,
        "Phi": phi_bound,
        "Nu": nu_bound,
        "Del": del_bound,
    }


class DAFFormatter:
    """Formatter for DAF experiment CLI output.

    Handles all text/table formatting so the core DAF class doesn't need to.
    """

    def __init__(self, space=None, marker=None, column_marker=None):
        self.space = space if space is not None else _DEFAULT_SPACE
        self.marker = marker if marker is not None else _DEFAULT_MARKER
        self.column_marker = column_marker if column_marker is not None else _DEFAULT_COLUMN_MARKER
        self._update_format_strings()

    def _update_format_strings(self):
        """Update format strings based on current space/marker/column_marker."""
        self.center = (
            self.column_marker
            + "{:^" + str(self.space - 2) + "}"
            + self.column_marker
        )
        self.roundfit = int(4 + ((self.space - 10) / 2)) if self.space > 10 else 4
        self.centshow = "{:^" + str(16 - 2) + "}"

    def set_print_options(self, marker=None, column_marker=None, space=None):
        """Update print formatting options."""
        if marker is not None:
            self.marker = marker
        if column_marker is not None:
            self.column_marker = column_marker
        if space is not None:
            self.space = space if space > 10 else 10
        self._update_format_strings()

    def _fmt(self, val):
        """Format a float value to 5 decimal places."""
        return "{:.5f}".format(float(val))

    def _separator_row(self):
        """Generate a separator row."""
        mk = self.marker * self.space
        return [
            {"col1": mk, "col2": mk, "col3": mk, "col4": mk,
             "col5": mk, "col6": mk, "col7": mk}
        ]

    def _base_fmt(self):
        """Base format spec for 7-column tables."""
        return [
            ("", "col1", self.space), ("", "col2", self.space),
            ("", "col3", self.space), ("", "col4", self.space),
            ("", "col5", self.space), ("", "col6", self.space),
            ("", "col7", self.space),
        ]

    def _6col_fmt(self, ident=3, space=20):
        """Format spec for 6-column tables."""
        return [
            ("", "ident", ident),
            ("", "col1", space), ("", "col2", space),
            ("", "col3", space), ("", "col4", space),
            ("", "col5", space), ("", "col6", space),
        ]

    def _7col_fmt(self, ident=3, space=20):
        """Format spec for 7-column tables."""
        return [
            ("", "ident", ident),
            ("", "col1", space), ("", "col2", space),
            ("", "col3", space), ("", "col4", space),
            ("", "col5", space), ("", "col6", space),
            ("", "col7", space),
        ]

    def format_mode(self, setup, col1, col2, col3, col4, col5, forprint):
        """Format the mode display."""
        mode_num = str(col1) + str(col2) + str(col3) + str(col4) + str(col5)
        data = [
            {
                "ident": "",
                "col1": self.centshow.format("MODE"),
                "col2": self.centshow.format(setup[0]),
                "col3": self.centshow.format(setup[1]),
                "col4": self.centshow.format(setup[2]),
                "col5": self.centshow.format(setup[3]),
                "col6": self.centshow.format(setup[4]),
            },
            {
                "ident": "",
                "col1": self.centshow.format(mode_num),
                "col2": self.centshow.format(forprint[0][1]),
                "col3": self.centshow.format(forprint[1][1]),
                "col4": self.centshow.format(forprint[2][1]),
                "col5": self.centshow.format(forprint[3][1]),
                "col6": self.centshow.format(forprint[4][1]),
            },
        ]
        return TablePrinter(self._6col_fmt(), ul="")(data)

    def format_experiment(self, sampleor, lam, en, idir, ndir, nref):
        """Format the experiment display."""
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
                "col1": self.centshow.format(sampleor),
                "col2": self.centshow.format(self._fmt(lam)),
                "col3": self.centshow.format(str(self._fmt(en / 1000))),
                "col4": self.centshow.format(format_vec(idir)),
                "col5": self.centshow.format(format_vec(ndir)),
                "col6": self.centshow.format(format_vec(nref)),
            },
        ]
        return TablePrinter(self._6col_fmt(), ul="")(data)

    def format_sample(self, samp):
        """Format the sample info display."""
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
                "col1": self.centshow.format(samp.name),
                "col2": self.centshow.format(self._fmt(samp.a)),
                "col3": self.centshow.format(str(self._fmt(samp.b))),
                "col4": self.centshow.format(str(self._fmt(samp.c))),
                "col5": self.centshow.format(str(self._fmt(samp.alpha))),
                "col6": self.centshow.format(str(self._fmt(samp.beta))),
                "col7": self.centshow.format(str(self._fmt(samp.gamma))),
            },
        ]
        return TablePrinter(self._7col_fmt(), ul="")(data)

    def format_full_status(
        self, setup, col1, col2, col3, col4, col5,
        forprint, qerror,
        hkl_calc, nref, en, lam, samp,
        alphain, betaout, psipseudo, taupseudo, qaz, naz, omega,
        del_val, eta_val, chi_val, phi_val, nu_val, mu_val,
        Qshow, Qnorm, ttB1, dhkl, FHKL
    ):
        """Format the full __str__ output for DAF."""
        def c(val):
            return self.center.format(val)

        def f(val):
            return self.center.format(self._fmt(val))

        def sep(val):
            return self.center.format(val)

        mode_num = str(col1) + str(col2) + str(col3) + str(col4) + str(col5)

        data = [
            {"col1": c("MODE"), "col2": c(setup[0]), "col3": c(setup[1]),
             "col4": c(setup[2]), "col5": c(setup[3]), "col6": c(setup[4]),
             "col7": c("Error")},
            {"col1": c(mode_num), "col2": c(forprint[0][1]), "col3": c(forprint[1][1]),
             "col4": c(forprint[2][1]), "col5": c(forprint[3][1]), "col6": c(forprint[4][1]),
             "col7": c("%.3g" % qerror)},
            *self._separator_row(),
            {"col1": c("H"), "col2": c("K"), "col3": c("L"),
             "col4": c("Ref vector"), "col5": c("Energy (keV)"), "col6": c("WL (angstrom)"),
             "col7": c("Sample")},
            {"col1": f(hkl_calc[0]), "col2": f(hkl_calc[1]), "col3": f(hkl_calc[2]),
             "col4": c(format_vec(nref)), "col5": f(en / 1000), "col6": f(lam),
             "col7": c(samp.name)},
            *self._separator_row(),
            {"col1": c("Qx"), "col2": c("Qy"), "col3": c("Qz"),
             "col4": c("|Q|"), "col5": c("Exp 2theta"), "col6": c("Dhkl"),
             "col7": c("FHKL (Base)")},
            {"col1": f(Qshow[0]), "col2": f(Qshow[1]), "col3": f(Qshow[2]),
             "col4": f(Qnorm), "col5": f(ttB1), "col6": f(dhkl),
             "col7": f(FHKL)},
            *self._separator_row(),
            {"col1": c("Alpha"), "col2": c("Beta"), "col3": c("Psi"),
             "col4": c("Tau"), "col5": c("Qaz"), "col6": c("Naz"),
             "col7": c("Omega")},
            {"col1": f(alphain), "col2": f(betaout), "col3": f(psipseudo),
             "col4": f(taupseudo), "col5": f(qaz), "col6": f(naz),
             "col7": f(omega)},
            *self._separator_row(),
            {"col1": c("Del"), "col2": c("Eta"), "col3": c("Chi"),
             "col4": c("Phi"), "col5": c("Nu"), "col6": c("Mu"),
             "col7": c("--")},
            {"col1": f(del_val), "col2": f(eta_val), "col3": f(chi_val),
             "col4": f(phi_val), "col5": f(nu_val), "col6": f(mu_val),
             "col7": c("--")},
            *self._separator_row(),
        ]

        return TablePrinter(self._base_fmt(), ul=self.marker)(data)
