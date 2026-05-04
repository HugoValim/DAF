#!/usr/bin/env python3

import xrayutilities as xu
import numpy as np
from numpy import linalg as LA

from daf.core.ub_matrix_calc import UBMatrix
from daf.core.matrix_utils import calculate_pseudo_angle_from_motor_angles
from daf.core.math_utils import vector_angle


# Motor pseudo-angle names that map directly to motor indices
_MOTOR_PSEUDO_MAP = {
    "Mu": 0,
    "Eta": 1,
    "Chi": 2,
    "Phi": 3,
    "Nu": 4,
    "Del": 5,
}

# Tolerance for numerical computations
_ANGLE_OFFSET = 1e-6  # Small offset added to motor angles for numerical stability
_DEFAULT_MAX_ERROR = 1e-5  # Default max error threshold for Q2AngFit
_SCAN_QERROR_THRESHOLD = (
    1e-5  # Threshold for raising qerror in scan (shares _DEFAULT_MAX_ERROR intent)
)
_CHUTE_ANGLES = (45, 45, 45, 45, 45, 45)  # Motor angle offsets for retry sequence
_ENERGY_KEV_THRESHOLD = 100  # Threshold below which beamline PV values are in keV


# Pseudo angles that require full computation via calculate_pseudo_angle_from_motor_angles
_PSEUDO_ANGLE_COMPUTED = frozenset(
    {
        "alpha",
        "beta",
        "qaz",
        "naz",
        "tau",
        "psi",
        "omega",
        "aeqb",
    }
)


def _compute_pseudo_angles(Mu, Eta, Chi, Phi, Nu, Del, samp, hkl, lam, nref, U):
    return calculate_pseudo_angle_from_motor_angles(
        Mu, Eta, Chi, Phi, Nu, Del, samp, hkl, lam, nref, U
    )


class MinimizationProc(UBMatrix):
    def pseudoAngleConst(self, angles, pseudo_angle, fix_angle):

        # Special geometric relations
        if pseudo_angle == "eta=del/2":
            return angles[1] - angles[5] / 2
        elif pseudo_angle == "mu=nu/2":
            return angles[0] - angles[4] / 2

        # Direct motor angle constraints
        if pseudo_angle in _MOTOR_PSEUDO_MAP:
            idx = _MOTOR_PSEUDO_MAP[pseudo_angle]
            return angles[idx] + _ANGLE_OFFSET - fix_angle

        # Pseudo angles that require full computation
        Mu = angles[0] + _ANGLE_OFFSET
        Eta = angles[1] + _ANGLE_OFFSET
        Chi = angles[2] + _ANGLE_OFFSET
        Phi = angles[3] + _ANGLE_OFFSET
        Nu = angles[4] + _ANGLE_OFFSET
        Del = angles[5] + _ANGLE_OFFSET

        computed = _compute_pseudo_angles(
            Mu, Eta, Chi, Phi, Nu, Del, self.sample, self.hkl, self.lam, self.nref, self.U
        )

        if pseudo_angle == "aeqb":
            return computed.beta - computed.alpha
        if hasattr(computed, pseudo_angle):
            return getattr(computed, pseudo_angle) - fix_angle

    def motor_angles(self, *args, qvec=False, max_err=_DEFAULT_MAX_ERROR, **kwargs):

        self.isscan = False

        if qvec is not False:
            self.Q_lab = qvec

        else:
            self.Q_material = self.sample.Q(self.hkl)

            self.Q_lab = self.hrxrd.Transform(self.Q_material)

        self.dhkl = self.sample.planeDistance(self.hkl)
        tilt = vector_angle(self.hkl, self.sample.Q(self.ndir), deg=True)

        if "start_values" in kwargs:
            self.start = kwargs["start_values"]
        else:
            self.start = [0, 0, 0, 0, 0, 0]

        self.fallback_angles = list(_CHUTE_ANGLES)

        # Build constraint list from pseudo_constraints_w_value_list
        if len(self.pseudo_constraints_w_value_list) != 0:
            pseudoconst = self.pseudoAngleConst
            restrict = [
                {
                    "type": "eq",
                    "fun": lambda a, idx=idx: pseudoconst(
                        a,
                        self.pseudo_constraints_w_value_list[idx][0],
                        self.pseudo_constraints_w_value_list[idx][1],
                    ),
                }
                for idx in range(len(self.pseudo_constraints_w_value_list))
            ]
        else:
            restrict = None

        ang, qerror, errcode = xu.Q2AngFit(
            self.Q_lab,
            self.hrxrd,
            self.bounds,
            startvalues=self.start,
            constraints=restrict,
            ormat=self.U,
        )

        if qerror > max_err:
            ang, self.qerror = self._retry_q2angfit_with_start_sequence(
                restrict, max_err
            )
        else:
            self.qerror = qerror
        self.hkl_calc = np.round(
            self.hrxrd.Ang2HKL(*ang, mat=self.sample, en=self.en, U=self.U), 5
        )

        self.Mu, self.Eta, self.Chi, self.Phi = (ang[0], ang[1], ang[2], ang[3])
        self.Nu, self.Del = (ang[4], ang[5])

        pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
            self.Mu,
            self.Eta,
            self.Chi,
            self.Phi,
            self.Nu,
            self.Del,
            self.sample,
            self.hkl,
            self.lam,
            self.nref,
            self.U,
        )

        self.ttB1 = pseudo_angles_dict.twotheta
        self.tB1 = pseudo_angles_dict.theta
        self.alphain = pseudo_angles_dict.alpha
        self.qaz = pseudo_angles_dict.qaz
        self.naz = pseudo_angles_dict.naz
        self.taupseudo = pseudo_angles_dict.tau
        self.psipseudo = pseudo_angles_dict.psi
        self.betaout = pseudo_angles_dict.beta
        self.omega = pseudo_angles_dict.omega
        self.Qshow = pseudo_angles_dict.q_vector
        self.Qnorm = pseudo_angles_dict.q_vector_norm
        self.FHKL = LA.norm(
            self.sample.StructureFactor(pseudo_angles_dict.q_vector, self.en)
        )

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
            "{0:.2e}".format(self.qerror),
        ], [
            self.format_float(self.Mu),
            self.format_float(self.Eta),
            self.format_float(self.Chi),
            self.format_float(self.Phi),
            self.format_float(self.Nu),
            self.format_float(self.Del),
            self.format_float(self.ttB1),
            self.format_float(self.tB1),
            self.format_float(self.alphain),
            self.format_float(self.qaz),
            self.format_float(self.naz),
            self.format_float(self.taupseudo),
            self.format_float(self.psipseudo),
            self.format_float(self.betaout),
            self.format_float(self.omega),
            self.format_float(self.hkl_calc[0]),
            self.format_float(self.hkl_calc[1]),
            self.format_float(self.hkl_calc[2]),
            "{0:.2e}".format(self.qerror),
        ]

    def _retry_q2angfit_with_start_sequence(self, constraints, max_err):
        """Retry Q2AngFit with a sequence of different start values.

        The retry sequence tries progressively wider sweeps of the Phi motor
        (0, 90, 180, 270 degrees) combined with the fallback_angles,
        as well as an initial estimate from Q2Ang.
        """
        start_sequence = [
            (0, 0, 0, 0, 0, self.preangs[3]),
            (
                self.fallback_angles[0],
                self.fallback_angles[1],
                self.fallback_angles[2],
                0,
                self.fallback_angles[4],
                self.fallback_angles[5],
            ),
            (
                self.fallback_angles[0],
                self.fallback_angles[1],
                self.fallback_angles[2],
                90,
                self.fallback_angles[4],
                self.fallback_angles[5],
            ),
            (
                self.fallback_angles[0],
                self.fallback_angles[1],
                self.fallback_angles[2],
                180,
                self.fallback_angles[4],
                self.fallback_angles[5],
            ),
            (
                self.fallback_angles[0],
                self.fallback_angles[1],
                self.fallback_angles[2],
                270,
                self.fallback_angles[4],
                self.fallback_angles[5],
            ),
        ]

        for start in start_sequence:
            self.start = list(start)
            ang, self.qerror, errcode = xu.Q2AngFit(
                self.Q_lab,
                self.hrxrd,
                self.bounds,
                startvalues=self.start,
                constraints=constraints,
                ormat=self.U,
            )
            if self.qerror < max_err:
                return
