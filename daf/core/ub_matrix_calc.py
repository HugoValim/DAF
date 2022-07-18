#!/usr/bin/env python3

import xrayutilities as xu
import numpy as np
from numpy import linalg as LA
from math import sqrt, sin, cos, atan2, acos

from daf.core.matrix_utils import calculate_rotation_matrix_from_diffractometer_angles


class UBMatrix:
    def uphi(self, Mu, Eta, Chi, Phi, Nu, Del):

        calculated_matrixes = calculate_rotation_matrix_from_diffractometer_angles(
            Mu, Eta, Chi, Phi, Nu, Del
        )

        MU = calculated_matrixes["mu"]
        ETA = calculated_matrixes["eta"]
        CHI = calculated_matrixes["chi"]
        PHI = calculated_matrixes["phi"]
        NU = calculated_matrixes["nu"]
        DEL = calculated_matrixes["del"]

        ttB1 = np.rad2deg(np.arccos(np.cos(np.deg2rad(Nu)) * np.cos(np.deg2rad(Del))))
        theta = ttB1 / 2

        invphi = LA.inv(PHI)
        invchi = LA.inv(CHI)
        inveta = LA.inv(ETA)
        invmu = LA.inv(MU)

        Ql1 = np.array(
            [
                np.sin(np.deg2rad(Del)),
                np.cos(np.deg2rad(Del)) * np.cos(np.deg2rad(Nu)) - 1,
                np.cos(np.deg2rad(Del)) * np.sin(np.deg2rad(Nu)),
            ]
        )

        Ql = Ql1 * (1 / (2 * np.sin(np.deg2rad(theta))))

        # uphi = invphi.dot(invchi).dot(inveta).dot(invmu).dot(Ql)
        uphi = PHI.T.dot(CHI.T).dot(ETA.T).dot(MU.T).dot(Ql)
        return uphi, theta

    def calc_U_2HKL(self, h1, angh1, h2, angh2):

        u1p, th1 = self.uphi(*angh1)
        u2p, th2 = self.uphi(*angh2)

        h1c = self.samp.B.dot(h1)
        h2c = self.samp.B.dot(h2)

        # Create modified unit vectors t1, t2 and t3 in crystal and phi systems

        t1c = h1c
        t3c = np.cross(h1c, h2c)
        t2c = np.cross(t3c, t1c)

        t1p = u1p  # FIXED from h1c 9July08
        t3p = np.cross(u1p, u2p)
        t2p = np.cross(t3p, t1p)
        # print(t2p)
        # ...and nornmalise and check that the reflections used are appropriate
        SMALL = 1e-4  # Taken from Vlieg's code

        def normalise(m):
            d = LA.norm(m)
            if d < SMALL:

                raise DiffcalcException(
                    "Invalid UB reference data. Please check that the specified "
                    "reference reflections/orientations are not parallel."
                )
            return m / d

        t1c = normalise(t1c)
        t2c = normalise(t2c)
        t3c = normalise(t3c)

        t1p = normalise(t1p)
        t2p = normalise(t2p)
        t3p = normalise(t3p)

        Tc = np.array([t1c, t2c, t3c])
        Tp = np.array([t1p, t2p, t3p])
        TcI = LA.inv(Tc.T)

        U = Tp.T.dot(TcI)
        self.U = U
        self.UB = U.dot(self.samp.B)

        return U, self.UB

    def calc_U_3HKL(self, h1, angh1, h2, angh2, h3, angh3):
        u1p, th1 = self.uphi(*angh1)
        u2p, th2 = self.uphi(*angh2)
        u3p, th3 = self.uphi(*angh3)

        h1p = (2 * np.sin(np.deg2rad(th1)) / self.lam) * u1p
        h2p = (2 * np.sin(np.deg2rad(th2)) / self.lam) * u2p
        h3p = (2 * np.sin(np.deg2rad(th3)) / self.lam) * u3p

        H = np.array([h1, h2, h3]).T
        Hp = np.array([h1p, h2p, h3p]).T
        HI = LA.inv(H)
        UB = Hp.dot(HI)
        UB2p = UB * 2 * np.pi

        GI = UB.T.dot(UB)
        G = LA.inv(GI)
        a1 = G[0, 0] ** 0.5
        a2 = G[1, 1] ** 0.5
        a3 = G[2, 2] ** 0.5
        alpha1 = np.rad2deg(np.arccos(G[1, 2] / (a2 * a3)))
        alpha2 = np.rad2deg(np.arccos(G[0, 2] / (a1 * a3)))
        alpha3 = np.rad2deg(np.arccos(G[0, 1] / (a1 * a2)))

        samp = xu.materials.Crystal(
            "generic", xu.materials.SGLattice(1, a1, a2, a3, alpha1, alpha2, alpha3)
        )

        U = UB2p.dot(LA.inv(samp.B))

        rparam = [a1, a2, a3, alpha1, alpha2, alpha3]

        self.U = U
        self.UB = UB2p

        self.calclp = rparam

        return U, UB2p, rparam

    def dot3(self, x, y):
        """z = dot3(x ,y) -- where x, y are 3*1 Jama matrices"""
        return x[0, 0] * y[0, 0] + x[1, 0] * y[1, 0] + x[2, 0] * y[2, 0]

    def bound(self, x):
        """
        moves x between -1 and 1. Used to correct for rounding errors which may
        have moved the sin or cosine of a value outside this range.
        """
        SMALL = 1e-10
        if abs(x) > (1 + SMALL):
            raise AssertionError(
                "The value (%f) was unexpectedly too far outside -1 or 1 to "
                "safely bound. Please report this." % x
            )
        if x > 1:
            return 1
        if x < -1:
            return -1
        return x

    def _get_quat_from_u123(self, u1, u2, u3):
        q0, q1 = sqrt(1.0 - u1) * sin(2.0 * np.pi * u2), sqrt(1.0 - u1) * cos(
            2.0 * np.pi * u2
        )
        q2, q3 = sqrt(u1) * sin(2.0 * np.pi * u3), sqrt(u1) * cos(2.0 * np.pi * u3)
        return q0, q1, q2, q3

    def _get_rot_matrix(self, q0, q1, q2, q3):
        rot = np.array(
            [
                [
                    q0**2 + q1**2 - q2**2 - q3**2,
                    2.0 * (q1 * q2 - q0 * q3),
                    2.0 * (q1 * q3 + q0 * q2),
                ],
                [
                    2.0 * (q1 * q2 + q0 * q3),
                    q0**2 - q1**2 + q2**2 - q3**2,
                    2.0 * (q2 * q3 - q0 * q1),
                ],
                [
                    2.0 * (q1 * q3 - q0 * q2),
                    2.0 * (q2 * q3 + q0 * q1),
                    q0**2 - q1**2 - q2**2 + q3**2,
                ],
            ]
        )
        return rot

    def angle_between_vectors(self, a, b):
        costheta = self.dot3(a * (1 / LA.norm(a)), b * (1 / LA.norm(b)))
        return np.arccos(self.bound(costheta))

    def _func_orient(self, vals, crystal, ref_data):
        quat = self._get_quat_from_u123(*vals)
        trial_u = self._get_rot_matrix(*quat)
        tmp_ub = trial_u * crystal.B

        res = 0
        I = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        for ref in ref_data:
            en = ref[9]
            wl = xu.en2lam(en)
            hkl_vals = np.array(ref[:3]).T
            Mu = ref[3]
            Eta = ref[4]
            Chi = ref[5]
            Phi = ref[6]
            Nu = ref[7]
            Del = ref[8]

        calculated_matrixes = calculate_rotation_matrix_from_diffractometer_angles(
            Mu, Eta, Chi, Phi, Nu, Del
        )

        MU = calculated_matrixes["mu"]
        ETA = calculated_matrixes["eta"]
        CHI = calculated_matrixes["chi"]
        PHI = calculated_matrixes["phi"]
        NU = calculated_matrixes["nu"]
        DEL = calculated_matrixes["del"]

        q_del = (NU * DEL - I) * np.array([[0], [2 * np.pi / wl], [0]])
        q_vals = LA.inv(PHI) * LA.inv(CHI) * LA.inv(ETA) * LA.inv(MU) * q_del

        q_hkl = tmp_ub * hkl_vals
        res += self.angle_between_vectors(q_hkl, q_vals)
        return res

    def _get_init_u123(self, um):
        def sign(x):
            if x < 0:
                return -1
            else:
                return 1

        tr = um[0, 0] + um[1, 1] + um[2, 2]
        sgn_q1 = sign(um[2, 1] - um[1, 2])
        sgn_q2 = sign(um[0, 2] - um[2, 0])
        sgn_q3 = sign(um[1, 0] - um[0, 1])
        q0 = sqrt(1.0 + tr) / 2.0
        q1 = sgn_q1 * sqrt(1.0 + um[0, 0] - um[1, 1] - um[2, 2]) / 2.0
        q2 = sgn_q2 * sqrt(1.0 - um[0, 0] + um[1, 1] - um[2, 2]) / 2.0
        q3 = sgn_q3 * sqrt(1.0 - um[0, 0] - um[1, 1] + um[2, 2]) / 2.0
        u1 = (1.0 - um[0, 0]) / 2.0
        u2 = atan2(q0, q1) / (2.0 * np.pi)
        u3 = atan2(q2, q3) / (2.0 * np.pi)
        if u2 < 0:
            u2 += 1.0
        if u3 < 0:
            u3 += 1.0
        return u1, u2, u3

    def fit_u_matrix(self, init_u, refl_list):
        uc = self.samp
        try:
            start = list(self._get_init_u123(init_u))
            lower = [0, 0, 0]
            upper = [1, 1, 1]
            sigma = [1e-2, 1e-2, 1e-2]
        except AttributeError:
            raise DiffcalcException(
                "UB matrix not initialised. Cannot run UB matrix fitting procedure."
            )

        from scipy.optimize import minimize

        ref_data = refl_list
        bounds = zip(lower, upper)
        res = minimize(
            self._func_orient,
            start,
            args=(uc, ref_data),
            method="SLSQP",
            tol=1e-10,
            options={"disp": False, "maxiter": 10000, "eps": 1e-6, "ftol": 1e-10},
        )
        # bounds=bounds)
        vals = res.x
        q0, q1, q2, q3 = self._get_quat_from_u123(*vals)
        res_u = self._get_rot_matrix(q0, q1, q2, q3)
        angle = 2.0 * acos(q0)
        xr = q1 / sqrt(1.0 - q0 * q0)
        yr = q2 / sqrt(1.0 - q0 * q0)
        zr = q3 / sqrt(1.0 - q0 * q0)
        TODEG = 180 / (2 * np.pi)
        print(angle * TODEG, (xr, yr, zr), res)
        return res_u
