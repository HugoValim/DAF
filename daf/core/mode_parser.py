#!/usr/bin/env python3
"""Mode parsing and constraint derivation for DAF operation modes."""

import xrayutilities as xu

from daf.core.utils import MODE_COLUMNS

# Maps setup string → motor name
_ANGLE_MAP = {
    "--": "x",
    "del_fix": "Del",
    "nu_fix": "Nu",
    "mu_fix": "Mu",
    "eta_fix": "Eta",
    "chi_fix": "Chi",
    "phi_fix": "Phi",
}

# Maps setup string → pseudo-angle constraint name
_CONS_MAP = {
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

# Default bounds for each motor
_DEFAULT_BOUNDS = {
    "Mu": (-180, 180),
    "Eta": (-180, 180),
    "Chi": (-5, 95),
    "Phi": (30, 400),
    "Nu": (-180, 180),
    "Del": (-180, 180),
}

# Pseudo-angle constraints that take "--" instead of a numeric value
_PSEUDO_NO_VALUE = {"eta=del/2", "mu=nu/2", "aeqb"}

# All predefined materials from xrayutilities
PREDEFINED_MATERIALS = {
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


class ModeParser:
    """Parse operation mode tuple, derive constraints and motor bounds.

    Example:
        parser = ModeParser((2, 0, 1, 0, 0))
        parser.setup          # ('alpha = beta', 'XD', 'Eta', 'phi_fix', '--')
        parser.col1           # 2
        parser.motor_bounds  # {'Del': 0, 'Phi': (30, 400), ...}
    """

    def __init__(self, mode: tuple):
        self._validate_mode(mode)
        self._parse_columns(mode)
        self._derive_constraints()
        self._compute_motor_bounds()
        self._build_pseudo_constraints()

    def _validate_mode(self, mode: tuple) -> None:
        for i in mode:
            if i not in (0, 1, 2, 3, 4, 5, 6):
                raise ValueError("The values of columns must be between 0 and 6")

        if mode[0] == 0 and mode[1] == 0:
            if len(mode) <= 3:
                raise ValueError(
                    "If the two first columns are set to 0, columns 4 and 5 must be given"
                )
            elif mode[3] == 0 or mode[4] == 0:
                raise ValueError(
                    "If the two first columns are set to 0, columns 4 and 5 must not be 0"
                )

        if mode[0] == 5:
            raise ValueError("Zone mode was not implemented yet")
        if mode[0] == 6:
            raise ValueError("Energy mode was not implemented yet")

    def _parse_columns(self, mode: tuple) -> None:
        self.constraint_col1 = mode[0]
        self.constraint_col2 = mode[1]
        self.constraint_col3 = mode[2]
        self.constraint_col4 = mode[3] if len(mode) >= 4 else 0
        self.constraint_col5 = mode[4] if len(mode) == 5 else 0

        self.setup = (
            MODE_COLUMNS[1][self.constraint_col1],
            MODE_COLUMNS[2][self.constraint_col2],
            MODE_COLUMNS[3][self.constraint_col3],
            MODE_COLUMNS[4][self.constraint_col4],
            MODE_COLUMNS[5][self.constraint_col5],
        )

    def _derive_constraints(self) -> None:
        self.motor_constraints = []
        self.pseudo_angle_constraints = []

        for i, name in enumerate(self.setup):
            if name in _ANGLE_MAP:
                if name == "--" and i in (0, 1):
                    continue
                mapped = _ANGLE_MAP[name]
                if mapped != "x":
                    self.motor_constraints.append(mapped)
            elif name in _CONS_MAP:
                mapped = _CONS_MAP[name]
                if mapped != "x":
                    self.pseudo_angle_constraints.append(mapped)

        self.fixed_motor_list = [m for m in self.motor_constraints if m != "x"]

    def _compute_motor_bounds(self) -> None:
        self.Mu_bound = 0 if "Mu" in self.fixed_motor_list else _DEFAULT_BOUNDS["Mu"]
        self.Eta_bound = 0 if "Eta" in self.fixed_motor_list else _DEFAULT_BOUNDS["Eta"]
        self.Chi_bound = 0 if "Chi" in self.fixed_motor_list else _DEFAULT_BOUNDS["Chi"]
        self.Phi_bound = 0 if "Phi" in self.fixed_motor_list else _DEFAULT_BOUNDS["Phi"]
        self.Nu_bound = 0 if "Nu" in self.fixed_motor_list else _DEFAULT_BOUNDS["Nu"]
        self.Del_bound = 0 if "Del" in self.fixed_motor_list else _DEFAULT_BOUNDS["Del"]

        self.motor_bounds = {
            "Mu": self.Mu_bound,
            "Eta": self.Eta_bound,
            "Chi": self.Chi_bound,
            "Phi": self.Phi_bound,
            "Nu": self.Nu_bound,
            "Del": self.Del_bound,
        }

    def _build_pseudo_constraints(self) -> None:
        self.pseudo_constraints_w_value_list = [
            (name, "--" if name in _PSEUDO_NO_VALUE else 0)
            for name in self.pseudo_angle_constraints
        ]

    def bounds_for(self, motor: str) -> tuple | int:
        """Return the bound for a given motor name."""
        return self.motor_bounds[motor]

    def set_bound(self, motor: str, value: tuple | int | float | list) -> None:
        """Update the bound for a given motor name."""
        self.motor_bounds[motor] = value
        setattr(self, f"{motor}_bound", value)

    def fixed_motors(self) -> list[str]:
        """Return a copy of the fixed motor list."""
        return list(self.fixed_motor_list)

    def is_motor_fixed(self, motor: str) -> bool:
        """Check if a motor is fixed in the current mode."""
        return motor in self.fixed_motor_list

    def constraints(self) -> tuple[list[str], list[str]]:
        """Return motor constraints and pseudo-angle constraints."""
        return list(self.motor_constraints), list(self.pseudo_angle_constraints)

    def pseudo_constraints(self) -> list[tuple[str, tuple | int | str]]:
        """Return a copy of pseudo constraints with their values."""
        return list(self.pseudo_constraints_w_value_list)

    def set_pseudo_constraints(
        self, constraints: list[tuple[str, tuple | int | str]]
    ) -> None:
        """Replace the pseudo constraints value list."""
        self.pseudo_constraints_w_value_list = list(constraints)

    def constraint_columns(self) -> tuple[int, int, int, int, int]:
        """Return the five constraint column values as a tuple."""
        return (
            self.constraint_col1,
            self.constraint_col2,
            self.constraint_col3,
            self.constraint_col4,
            self.constraint_col5,
        )

    @property
    def bounds_tuple(self) -> tuple:
        """Motor bounds as a 6-element tuple, for xrayutilities."""
        return (
            self.Mu_bound,
            self.Eta_bound,
            self.Chi_bound,
            self.Phi_bound,
            self.Nu_bound,
            self.Del_bound,
        )
