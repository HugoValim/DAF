#!/usr/bin/env python3

import xrayutilities as xu
import numpy as np
from numpy import linalg as LA

from daf.core.ub_matrix_calc import UBMatrix
from daf.core.matrix_utils import (
    calculate_rotation_matrix_from_diffractometer_angles,
    calculate_pseudo_angle_from_motor_angles,
)


class MinimizationProc(UBMatrix):
    def pseudoAngleConst(self, angles, pseudo_angle, fix_angle):

        if pseudo_angle == "eta=del/2":
            return angles[1] - angles[5] / 2
        elif pseudo_angle == "mu=nu/2":
            return angles[0] - angles[4] / 2

        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg

        Mu = angles[0] + 1e-6
        if pseudo_angle == "Mu":
            return Mu - fix_angle

        Eta = angles[1] + 1e-6
        if pseudo_angle == "Eta":
            return Eta - fix_angle

        Chi = angles[2] + 1e-6
        if pseudo_angle == "Chi":
            return Chi - fix_angle

        Phi = angles[3] + 1e-6
        if pseudo_angle == "Phi":
            return Phi - fix_angle

        Nu = angles[4] + 1e-6
        if pseudo_angle == "Nu":
            return Nu - fix_angle

        Del = angles[5] + 1e-6
        if pseudo_angle == "Del":
            return Del - fix_angle

        pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
            Mu, Eta, Chi, Phi, Nu, Del, self.samp, self.hkl, self.lam, self.nref, self.U
        )

        alphain = pseudo_angles_dict["alpha"]
        betaout = pseudo_angles_dict["beta"]
        qaz = pseudo_angles_dict["qaz"]
        naz = pseudo_angles_dict["naz"]
        taupseudo = pseudo_angles_dict["tau"]
        psipseudo = pseudo_angles_dict["psi"]
        omega = pseudo_angles_dict["omega"]

        if pseudo_angle == "alpha":
            return alphain - fix_angle

        elif pseudo_angle == "beta":
            return betaout - fix_angle

        elif pseudo_angle == "qaz":
            return qaz - fix_angle

        elif pseudo_angle == "naz":
            return naz - fix_angle

        elif pseudo_angle == "tau":
            return taupseudo - fix_angle

        elif pseudo_angle == "psi":
            return psipseudo - fix_angle

        elif pseudo_angle == "omega":
            return omega - fix_angle

        elif pseudo_angle == "aeqb":
            return betaout - alphain

    def motor_angles(self, *args, qvec=False, max_err=1e-5, **kwargs):

        self.isscan = False

        if qvec is not False:
            self.Q_lab = qvec

        else:
            self.Q_material = self.samp.Q(self.hkl)

            self.Q_lab = self.hrxrd.Transform(self.Q_material)

        self.dhkl = self.samp.planeDistance(self.hkl)
        tilt = xu.math.vector.VecAngle(self.hkl, self.samp.Q(self.ndir), deg=True)

        if "sv" in kwargs.keys():
            self.start = kwargs["sv"]
        else:
            self.start = [0, 0, 0, 0, 0, 0]

        media = lambda x, y: (x + y) / 2
        # self.chute1 = [media(i[0], i[1]) if type(i) != float else i for i in self.bounds]
        self.chute1 = [45, 45, 45, 45, 45, 45]

        if len(self.pseudo_constraints_w_value_list) != 0:
            pseudoconst = self.pseudoAngleConst

            if len(self.pseudo_constraints_w_value_list) == 1:

                restrict = [
                    {
                        "type": "eq",
                        "fun": lambda a: pseudoconst(
                            a,
                            self.pseudo_constraints_w_value_list[0][0],
                            self.pseudo_constraints_w_value_list[0][1],
                        ),
                    }
                ]

            elif len(self.pseudo_constraints_w_value_list) == 2:

                restrict = [
                    {
                        "type": "eq",
                        "fun": lambda a: pseudoconst(
                            a,
                            self.pseudo_constraints_w_value_list[0][0],
                            self.pseudo_constraints_w_value_list[0][1],
                        ),
                    },
                    {
                        "type": "eq",
                        "fun": lambda a: pseudoconst(
                            a,
                            self.pseudo_constraints_w_value_list[1][0],
                            self.pseudo_constraints_w_value_list[1][1],
                        ),
                    },
                ]

            elif len(self.pseudo_constraints_w_value_list) == 3:

                restrict = [
                    {
                        "type": "eq",
                        "fun": lambda a: pseudoconst(
                            a,
                            self.pseudo_constraints_w_value_list[0][0],
                            self.pseudo_constraints_w_value_list[0][1],
                        ),
                    },
                    {
                        "type": "eq",
                        "fun": lambda a: pseudoconst(
                            a,
                            self.pseudo_constraints_w_value_list[1][0],
                            self.pseudo_constraints_w_value_list[1][1],
                        ),
                    },
                    {
                        "type": "eq",
                        "fun": lambda a: pseudoconst(
                            a,
                            self.pseudo_constraints_w_value_list[2][0],
                            self.pseudo_constraints_w_value_list[2][1],
                        ),
                    },
                ]

            ang, qerror, errcode = xu.Q2AngFit(
                self.Q_lab,
                self.hrxrd,
                self.bounds,
                startvalues=self.start,
                constraints=restrict,
                ormat=self.U,
            )

            if qerror > max_err:
                while True:
                    self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                    self.start = (0, 0, 0, 0, 0, self.preangs[3])
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        constraints=restrict,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        0,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        constraints=restrict,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    # self.start = [0, self.chute1[1], self.chute1[2], 90, self.chute1[4], self.preangs[3]]
                    # ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                    # if qerror < 1e-5:
                    #     break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        90,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        constraints=restrict,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        180,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        constraints=restrict,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        270,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        constraints=restrict,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    break

        else:

            ang, qerror, errcode = xu.Q2AngFit(
                self.Q_lab,
                self.hrxrd,
                self.bounds,
                startvalues=self.start,
                ormat=self.U,
            )
            if qerror > max_err:
                while True:
                    self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                    self.start = (0, 0, 0, 0, 0, self.preangs[3])
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        0,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        90,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    # self.start = [0, self.chute1[1], self.chute1[2], 90, self.chute1[4], self.chute1[5]]
                    # ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                    # if qerror < 1e-5:
                    #     break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        180,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    self.start = [
                        self.chute1[0],
                        self.chute1[1],
                        self.chute1[2],
                        270,
                        self.chute1[4],
                        self.chute1[5],
                    ]
                    ang, qerror, errcode = xu.Q2AngFit(
                        self.Q_lab,
                        self.hrxrd,
                        self.bounds,
                        startvalues=self.start,
                        ormat=self.U,
                    )
                    if qerror < max_err:
                        break
                    break

        self.qerror = qerror
        self.hkl_calc = np.round(
            self.hrxrd.Ang2HKL(*ang, mat=self.samp, en=self.en, U=self.U), 5
        )

        self.Mu, self.Eta, self.Chi, self.Phi = (ang[0], ang[1], ang[2], ang[3])
        self.Nu, self.Del = (ang[4], ang[5])

        calculated_matrixes = calculate_rotation_matrix_from_diffractometer_angles(
            self.Mu, self.Eta, self.Chi, self.Phi, self.Nu, self.Del
        )

        pseudo_angles_dict = calculate_pseudo_angle_from_motor_angles(
            self.Mu,
            self.Eta,
            self.Chi,
            self.Phi,
            self.Nu,
            self.Del,
            self.samp,
            self.hkl,
            self.lam,
            self.nref,
            self.U,
        )

        self.ttB1 = pseudo_angles_dict["twotheta"]
        self.tB1 = pseudo_angles_dict["theta"]
        self.alphain = pseudo_angles_dict["alpha"]
        self.qaz = pseudo_angles_dict["qaz"]
        self.naz = pseudo_angles_dict["naz"]
        self.taupseudo = pseudo_angles_dict["tau"]
        self.psipseudo = pseudo_angles_dict["psi"]
        self.betaout = pseudo_angles_dict["beta"]
        self.omega = pseudo_angles_dict["omega"]
        self.Qshow = pseudo_angles_dict["q_vector"]
        self.Qnorm = pseudo_angles_dict["q_vector_norm"]
        self.FHKL = LA.norm(
            self.samp.StructureFactor(pseudo_angles_dict["q_vector"], self.en)
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
            self.fcsv(self.Mu),
            self.fcsv(self.Eta),
            self.fcsv(self.Chi),
            self.fcsv(self.Phi),
            self.fcsv(self.Nu),
            self.fcsv(self.Del),
            self.fcsv(self.ttB1),
            self.fcsv(self.tB1),
            self.fcsv(self.alphain),
            self.fcsv(self.qaz),
            self.fcsv(self.naz),
            self.fcsv(self.taupseudo),
            self.fcsv(self.psipseudo),
            self.fcsv(self.betaout),
            self.fcsv(self.omega),
            self.fcsv(self.hkl_calc[0]),
            self.fcsv(self.hkl_calc[1]),
            self.fcsv(self.hkl_calc[2]),
            "{0:.2e}".format(self.qerror),
        ]
