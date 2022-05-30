#!/usr/bin/env python3

import sys
import subprocess
import xrayutilities as xu
import numpy as np
import pandas as pd
from tqdm import tqdm
from numpy import linalg as LA
from math import pi, sqrt, sin, cos, atan2, acos
import os

import dafutilities as du

PI = np.pi
MAT = np.array
rad = np.deg2rad
deg = np.rad2deg


class DAFCalculations:

    @staticmethod
    def calculate_rotation_matrix_from_diffractometer_angles(mu, eta, chi, phi, nu, del_) -> dict:
        """Calculate the rotation matrix for all diffractometer motors and return a dict with all calculated rotations"""
        
        phi_rotation = MAT([[np.cos(rad(phi)),    np.sin(rad(phi)),   0],
                          [-np.sin(rad(phi)),  np.cos(rad(phi)),     0],
                          [0,                         0,             1]])

        chi_rotation = MAT([[np.cos(rad(chi)),    0,           np.sin(rad(chi))],
                          [0,                       1,                   0],
                          [-np.sin(rad(chi)),    0,           np.cos(rad(chi))]])

        eta_rotation = MAT([[np.cos(rad(eta)),    np.sin(rad(eta)),   0],
                            [-np.sin(rad(eta)),   np.cos(rad(eta)),   0],
                            [0,                         0,           1]])

        mu_rotation = MAT([[1,                       0,                      0],
                          [0,            np.cos(rad(mu)),    -np.sin(rad(mu))],
                          [0,            np.sin(rad(mu)),    np.cos(rad(mu))]])

        del_rotation = MAT([[np.cos(rad(del_)),    np.sin(rad(del_)),   0],
                        [-np.sin(rad(del_)),   np.cos(rad(del_)),   0],
                        [0,                       0,              1]])

        nu_rotation = MAT([[1,                    0,                         0],
                          [0,            np.cos(rad(nu)),    -np.sin(rad(nu))],
                          [0,            np.sin(rad(nu)),    np.cos(rad(nu))]])

        result_dict = {'mu': mu_rotation, 'eta': eta_rotation, 'chi': chi_rotation,
                        'phi': phi_rotation, 'nu': nu_rotation, 'del': del_rotation}
        return result_dict

    def uphi(self, Mu, Eta, Chi, Phi, Nu, Del):



        calculated_matrixes = self.calculate_rotation_matrix_from_diffractometer_angles(
            Mu, Eta, Chi, Phi, Nu, Del
        )

        MU = calculated_matrixes["mu"]
        ETA = calculated_matrixes["eta"]
        CHI = calculated_matrixes["chi"]
        PHI = calculated_matrixes["phi"]
        NU = calculated_matrixes["nu"]
        DEL = calculated_matrixes["del"]

        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        theta = ttB1/2

        invphi = LA.inv(PHI)
        invchi = LA.inv(CHI)
        inveta = LA.inv(ETA)
        invmu = LA.inv(MU)

        Ql1 = MAT([np.sin(rad(Del)),
                   np.cos(rad(Del))*np.cos(rad(Nu)) - 1,
                   np.cos(rad(Del))*np.sin(rad(Nu))])

        Ql = Ql1* (1/(2*np.sin(rad(theta))))

        # uphi = invphi.dot(invchi).dot(inveta).dot(invmu).dot(Ql)
        uphi = PHI.T.dot(CHI.T).dot(ETA.T).dot(MU.T).dot(Ql)
        return uphi, theta

    def calc_U_2HKL(self, h1, angh1, h2, angh2):

        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg

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

                raise DiffcalcException("Invalid UB reference data. Please check that the specified "
                                          "reference reflections/orientations are not parallel.")
            return m / d

        t1c = normalise(t1c)
        t2c = normalise(t2c)
        t3c = normalise(t3c)

        t1p = normalise(t1p)
        t2p = normalise(t2p)
        t3p = normalise(t3p)

        Tc = MAT([t1c, t2c, t3c])
        Tp = MAT([t1p, t2p, t3p])
        TcI = LA.inv(Tc.T)


        U = Tp.T.dot(TcI)
        self.U = U
        self.UB = U.dot(self.samp.B)

        return U , self.UB

    def calc_U_3HKL(self, h1, angh1, h2, angh2, h3, angh3):

        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg

        u1p, th1 = self.uphi(*angh1)
        u2p, th2 = self.uphi(*angh2)
        u3p, th3 = self.uphi(*angh3)

        h1p = (2*np.sin(rad(th1))/self.lam)*u1p
        h2p = (2*np.sin(rad(th2))/self.lam)*u2p
        h3p = (2*np.sin(rad(th3))/self.lam)*u3p


        H = MAT([h1, h2, h3]).T
        Hp = MAT([h1p, h2p, h3p]).T
        HI = LA.inv(H)
        UB = Hp.dot(HI)
        UB2p = UB*2*PI

        GI = UB.T.dot(UB)
        G = LA.inv(GI)
        a1 = G[0,0]**0.5
        a2 = G[1,1]**0.5
        a3 = G[2,2]**0.5
        alpha1 = deg(np.arccos(G[1,2]/(a2*a3)))
        alpha2 = deg(np.arccos(G[0,2]/(a1*a3)))
        alpha3 = deg(np.arccos(G[0,1]/(a1*a2)))

        samp = xu.materials.Crystal('generic',xu.materials.SGLattice(1, a1, a2, a3, alpha1, alpha2, alpha3))

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
                "safely bound. Please report this." % x)
        if x > 1:
            return 1
        if x < -1:
            return -1
        return x


    def _get_quat_from_u123(self, u1, u2, u3):
        q0, q1 = sqrt(1.-u1)*sin(2.*pi*u2), sqrt(1.-u1)*cos(2.*pi*u2)
        q2, q3 =    sqrt(u1)*sin(2.*pi*u3),    sqrt(u1)*cos(2.*pi*u3)
        return q0, q1, q2, q3

    def _get_rot_matrix(self, q0, q1, q2, q3):
        rot = MAT([[q0**2 + q1**2 - q2**2 - q3**2,            2.*(q1*q2 - q0*q3),            2.*(q1*q3 + q0*q2),],
                  [           2.*(q1*q2 + q0*q3), q0**2 - q1**2 + q2**2 - q3**2,            2.*(q2*q3 - q0*q1),],
                  [           2.*(q1*q3 - q0*q2),            2.*(q2*q3 + q0*q1), q0**2 - q1**2 - q2**2 + q3**2,]])
        return rot

    def angle_between_vectors(self, a, b):
        costheta = self.dot3(a * (1 / LA.norm(a)), b * (1 / LA.norm(b)))
        return np.arccos(self.bound(costheta))
    
    def _func_orient(self, vals, crystal, ref_data):
        quat = self._get_quat_from_u123(*vals)
        trial_u = self._get_rot_matrix(*quat)
        tmp_ub = trial_u * crystal.B

        res = 0
        I = MAT([[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]])

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

        calculated_matrixes = self.calculate_rotation_matrix_from_diffractometer_angles(
            Mu, Eta, Chi, Phi, Nu, Del
        )

        MU = calculated_matrixes["mu"]
        ETA = calculated_matrixes["eta"]
        CHI = calculated_matrixes["chi"]
        PHI = calculated_matrixes["phi"]
        NU = calculated_matrixes["nu"]
        DEL = calculated_matrixes["del"]

        q_del = (NU * DEL - I) * MAT([[0], [2 * np.pi / wl], [0]])
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

        tr = um[0,0] + um[1,1] + um[2,2]
        sgn_q1 = sign(um[2,1] - um[1,2])
        sgn_q2 = sign(um[0,2] - um[2,0])
        sgn_q3 = sign(um[1,0] - um[0,1])
        q0 = sqrt(1. + tr) / 2.
        q1 = sgn_q1 * sqrt(1. + um[0,0] - um[1,1] - um[2,2]) / 2.0
        q2 = sgn_q2 * sqrt(1. - um[0,0] + um[1,1] - um[2,2]) / 2.0
        q3 = sgn_q3 * sqrt(1. - um[0,0] - um[1,1] + um[2,2]) / 2.0
        u1 = (1. - um[0,0]) / 2.
        u2 = atan2(q0, q1) / (2. * pi)
        u3 = atan2(q2, q3) / (2. * pi)
        if u2 < 0: u2 += 1.
        if u3 < 0: u3 += 1.
        return u1, u2, u3

    def fit_u_matrix(self, init_u, refl_list):
        uc = self.samp
        try:
            start = list(self._get_init_u123(init_u))
            lower = [ 0, 0, 0]
            upper = [ 1, 1, 1]
            sigma = [ 1e-2, 1e-2, 1e-2]
        except AttributeError:
            raise DiffcalcException("UB matrix not initialised. Cannot run UB matrix fitting procedure.")
       
        from scipy.optimize import minimize

        ref_data = refl_list
        bounds = zip(lower, upper)
        res = minimize(self._func_orient,
                       start,
                       args=(uc, ref_data),
                       method='SLSQP',
                       tol=1e-10,
                       options={'disp' : False,
                                'maxiter': 10000,
                                'eps': 1e-6,
                                'ftol': 1e-10})
                       # bounds=bounds)
        vals = res.x
        q0, q1, q2, q3 = self._get_quat_from_u123(*vals)
        res_u = self._get_rot_matrix(q0, q1, q2, q3)
        angle = 2. * acos(q0)
        xr = q1 / sqrt(1. - q0 * q0)
        yr = q2 / sqrt(1. - q0 * q0)
        zr = q3 / sqrt(1. - q0 * q0)
        TODEG = 180/(2*np.pi)
        print (angle * TODEG, (xr, yr, zr), res)
        return res_u

    def calc_pseudo(self, Mu, Eta, Chi, Phi, Nu, Del):


        calculated_matrixes = self.calculate_rotation_matrix_from_diffractometer_angles(
            Mu, Eta, Chi, Phi, Nu, Del
        )

        MU = calculated_matrixes["mu"]
        ETA = calculated_matrixes["eta"]
        CHI = calculated_matrixes["chi"]
        PHI = calculated_matrixes["phi"]
        NU = calculated_matrixes["nu"]
        DEL = calculated_matrixes["del"]


        Z = MU.dot(ETA).dot(CHI).dot(PHI)
        n = self.nref
        nc = self.samp.B.dot(n)
        nchat = nc/LA.norm(nc)
        nphi = self.U.dot(nc)
        nphihat = nphi/LA.norm(nphi)
        nz = Z.dot(nphihat)

        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        tB1 = ttB1/2


        A1 = (self.samp.a1)
        A2 = (self.samp.a2)
        A3 = (self.samp.a3)

        vcell = A1.dot(np.cross(A2,A3))

        B1 = np.cross(self.samp.a2,self.samp.a3)/vcell
        B2 = np.cross(self.samp.a3,self.samp.a1)/vcell
        B3 = np.cross(self.samp.a1,self.samp.a2)/vcell

        q = self.samp.Q(self.hkl) # eq (1)
        self.Qshow = q
        normQ = LA.norm(q)
        self.Qnorm = normQ
        Qhat = np.round(q/normQ,5)


        k = (2*np.pi)/(self.lam)
        Ki = k*np.array([0,1,0])
        Kf0 = Ki ##### eq (6)
        Kfnu = k*MAT([ np.sin(rad(Del)), np.cos(rad(Nu))*np.cos(rad(Del)), np.sin(rad(Nu))*np.cos(rad(Del))])
        Kfnunorm = LA.norm(Kfnu)
        Kfnuhat = Kfnu/Kfnunorm


        taupseudo = deg(np.arccos(np.round(Qhat.dot(nchat),5)))


        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))

        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))


        qaz = deg(np.arctan2(np.tan(rad(Del)),np.sin(rad(Nu))))


        # QLhat = MAT([ np.cos(rad(tB1))*np.sin(rad(qaz)),
        #             -np.sin(rad(tB1)),
        #             np.cos(rad(tB1))*np.cos(rad(qaz))])

        # taupseudo = deg(np.arccos(QLhat.dot(nz)))


        # naz = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))

        naz = deg(np.arctan2((nz.dot([1,0,0])),(nz.dot([0,0,1]))))


        if taupseudo == 0 or taupseudo == 180:

            Qphi = Qhat.dot(self.samp.B)
            Qphinorm = LA.norm(Qphi)
            Qphihat = Qphi/Qphinorm

            newref = MAT([np.sqrt(Qphihat[1]**2 + Qphihat[2]**2),
                                  -(Qphihat[0]*Qphihat[1])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2)),
                                  -(Qphihat[0]*Qphihat[2])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2))])

            ntmp = newref
            nctmp = self.samp.B.dot(ntmp)
            nchattmp = nc/LA.norm(nctmp)
            nphitmp = self.U.dot(nctmp)
            nphihattmp = nphitmp/LA.norm(nphitmp)

            nztmp = Z.dot(nphihattmp)
            alphatmp = deg(np.arcsin(-xu.math.vector.VecDot(nztmp,[0,1,0])))
            tautemp = deg(np.arccos(Qhat.dot(newref)))

            arg2 = np.round((np.cos(rad(tautemp))*np.sin(rad(tB1))-np.sin(rad(alphatmp)))/(np.sin(rad(tautemp))*np.cos(rad(tB1))),8)


            # print('')
            # print(' The reference vector is parallel to the Q vector, in order to calculate psi the reference\n vector {} will be used.'.format(np.round(newref,5)))

        else:

            arg2 = np.round((np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1))),8)

        psipseudo = deg(np.arccos(arg2))

        # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        # # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))

        # if arg3 >1:
        #     arg3 = 0.99999999999999999999
        # elif arg3 < -1:
        #     arg3 = -0.9999999999999999999

        # betaout = deg(np.arcsin(arg3))

        betaout = deg(np.arcsin((np.dot(Kfnuhat, nz))))


        arg4 = np.round((np.sin(rad(Eta))*np.sin(rad(qaz))+np.sin(rad(Mu))*np.cos(rad(Eta))*np.cos(rad(qaz)))*np.cos(rad(tB1))-np.cos(rad(Mu))*np.cos(rad(Eta))*np.sin(rad(tB1)),5)
        # if arg4 >1:
        #   arg4 = 0.999999999999999999999
        # elif  arg4 < -1:
        #     arg4 = -0.999999999999999999
        omega = deg(np.arcsin(arg4))

        return (alphain, qaz, naz, taupseudo, psipseudo, betaout, omega)

    def pseudoAngleConst(self, angles, pseudo_angle, fix_angle):

        if pseudo_angle == 'eta=del/2':
            return angles[1] - angles[5]/2
        elif pseudo_angle == 'mu=nu/2':
            return angles[0] - angles[4]/2

        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg

        Mu = angles[0] + 1e-6
        if pseudo_angle == 'Mu':
            return Mu - fix_angle

        Eta = angles[1] + 1e-6
        if pseudo_angle == 'Eta':
            return Eta - fix_angle

        Chi = angles[2] + 1e-6
        if pseudo_angle == 'Chi':
            return Chi - fix_angle

        Phi= angles[3] + 1e-6
        if pseudo_angle == 'Phi':
            return Phi - fix_angle

        Nu = angles[4] + 1e-6
        if pseudo_angle == 'Nu':
            return Nu - fix_angle

        Del = angles[5] + 1e-6
        if pseudo_angle == 'Del':
            return Del - fix_angle

        calculated_matrixes = self.calculate_rotation_matrix_from_diffractometer_angles(
            Mu, Eta, Chi, Phi, Nu, Del
        )

        MU = calculated_matrixes["mu"]
        ETA = calculated_matrixes["eta"]
        CHI = calculated_matrixes["chi"]
        PHI = calculated_matrixes["phi"]
        NU = calculated_matrixes["nu"]
        DEL = calculated_matrixes["del"]

        Z = MU.dot(ETA).dot(CHI).dot(PHI)
        n = self.nref
        nc = self.samp.B.dot(n)
        nchat = nc/LA.norm(nc)
        nphi = self.U.dot(nc)
        nphihat = nphi/LA.norm(nphi)

        nz = Z.dot(nphihat)

        A1 = (self.samp.a1)
        A2 = (self.samp.a2)
        A3 = (self.samp.a3)

        vcell = A1.dot(np.cross(A2,A3))

        B1 = np.cross(self.samp.a2,self.samp.a3)/vcell
        B2 = np.cross(self.samp.a3,self.samp.a1)/vcell
        B3 = np.cross(self.samp.a1,self.samp.a2)/vcell

        q = self.samp.Q(self.hkl) # eq (1)
        normQ = LA.norm(q)
        Qhat = np.round(q/normQ,5)

        k = (2*np.pi)/(self.lam)
        Ki = k*np.array([0,1,0])
        Kf0 = Ki ##### eq (6)
        Kfnu = k*MAT([ np.sin(rad(Del)), np.cos(rad(Nu))*np.cos(rad(Del)), np.sin(rad(Nu))*np.cos(rad(Del))])
        Kfnunorm = LA.norm(Kfnu)
        Kfnuhat = Kfnu/Kfnunorm


        # taupseudo = deg(np.arccos(Qhat.dot(nhat)))
        taupseudo = deg(np.arccos(np.round(Qhat.dot(nchat),5)))


        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        tB1 = ttB1/2


        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))

        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))


        qaz = deg(np.arctan2(np.tan(rad(Del)),np.sin(rad(Nu))))

        # QLhat = MAT([ np.cos(rad(tB1))*np.sin(rad(qaz)),
        #             -np.sin(rad(tB1)),
        #             np.cos(rad(tB1))*np.cos(rad(qaz))])

        # taupseudo = deg(np.arccos(QLhat.dot(nz)))
        # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))

        naz = deg(np.arctan2((nz.dot([1,0,0])),(nz.dot([0,0,1]))))


        if taupseudo == 0 or taupseudo == 180:

            Qphi = Qhat.dot(self.samp.B)
            Qphinorm = LA.norm(Qphi)
            Qphihat = Qphi/Qphinorm

            newref = MAT([np.sqrt(Qphihat[1]**2 + Qphihat[2]**2),
                                  -(Qphihat[0]*Qphihat[1])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2)),
                                  -(Qphihat[0]*Qphihat[2])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2))])

            ntmp = newref
            nctmp = self.samp.B.dot(ntmp)
            nchattmp = nc/LA.norm(nctmp)
            nphitmp = self.U.dot(nctmp)
            nphihattmp = nphitmp/LA.norm(nphitmp)

            nztmp = Z.dot(nphihattmp)
            alphatmp = deg(np.arcsin(-xu.math.vector.VecDot(nztmp,[0,1,0])))
            tautemp = deg(np.arccos(Qhat.dot(newref)))

            arg2 = np.round((np.cos(rad(tautemp))*np.sin(rad(tB1))-np.sin(rad(alphatmp)))/(np.sin(rad(tautemp))*np.cos(rad(tB1))),8)

        else:

            arg2 = np.round((np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1))),8)


        psipseudo = deg(np.arccos(arg2))


        # psipseudo = deg(np.arccos(arg2))


        # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))

        # if arg3 >1:
        #     arg3 = 0.99999999999999999999
        # elif arg3 < -1:
        #     arg3 = -0.9999999999999999999
        # betaout = deg(np.arcsin(arg3))

        betaout = deg(np.arcsin((np.dot(Kfnuhat, nz))))

        arg4 = np.round((np.sin(rad(Eta))*np.sin(rad(qaz))+np.sin(rad(Mu))*np.cos(rad(Eta))*np.cos(rad(qaz)))*np.cos(rad(tB1))-np.cos(rad(Mu))*np.cos(rad(Eta))*np.sin(rad(tB1)))
        # if arg4 >1:
        #   arg4 = 0.999999999999999999999
        # elif  arg4 < -1:
        #     arg4 = -0.999999999999999999
        omega = deg(np.arcsin(arg4))


        if pseudo_angle == 'alpha':
            return alphain - fix_angle

        elif pseudo_angle == 'beta':
            return betaout - fix_angle

        elif pseudo_angle == 'qaz':
            return qaz - fix_angle

        elif pseudo_angle == 'naz':
            return naz - fix_angle

        elif pseudo_angle == 'tau':
            return taupseudo - fix_angle

        elif pseudo_angle == 'psi':
            return psipseudo - fix_angle

        elif pseudo_angle == 'omega':
            return omega - fix_angle

        elif pseudo_angle == 'aeqb':
            return betaout - alphain


    def motor_angles(self, *args, qvec = False, calc = True, max_err = 1e-5, **kwargs):

        self.isscan = False

        self.sampleID = self.samp.name


        self.hrxrd = xu.HXRD(self.idir, self.ndir, en = self.en, qconv= self.qconv, sampleor = self.sampleor)


        self.bounds = (self.Mu_bound, self.Eta_bound, self.Chi_bound,
                        self.Phi_bound, self.Nu_bound, self.Del_bound)
        if calc:
            if qvec is not False:
                self.Q_lab = qvec


            else:
                self.Q_material = self.samp.Q(self.hkl)

                self.Q_lab = self.hrxrd.Transform(self.Q_material)


            self.dhkl = self.samp.planeDistance(self.hkl)
            tilt = xu.math.vector.VecAngle(self.hkl, self.samp.Q(self.ndir), deg=True)


            if 'sv' in kwargs.keys():
                self.start = kwargs['sv']
            else:
                self.start = [0,0,0,0,0,0]

            media = lambda x,y: (x+y)/2
            # self.chute1 = [media(i[0], i[1]) if type(i) != float else i for i in self.bounds]
            self.chute1 = [45,45,45,45,45,45]


            if len(self.pseudo_constraints_w_value_list) != 0:
                    pseudoconst = self.pseudoAngleConst


                    if len(self.pseudo_constraints_w_value_list) == 1:


                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.pseudo_constraints_w_value_list[0][0], self.pseudo_constraints_w_value_list[0][1])}]


                    elif len(self.pseudo_constraints_w_value_list) == 2:


                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.pseudo_constraints_w_value_list[0][0], self.pseudo_constraints_w_value_list[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(a, self.pseudo_constraints_w_value_list[1][0], self.pseudo_constraints_w_value_list[1][1])}]


                    elif len(self.pseudo_constraints_w_value_list) == 3:


                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.pseudo_constraints_w_value_list[0][0], self.pseudo_constraints_w_value_list[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(a, self.pseudo_constraints_w_value_list[1][0], self.pseudo_constraints_w_value_list[1][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(a, self.pseudo_constraints_w_value_list[2][0], self.pseudo_constraints_w_value_list[2][1])}]


                    ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat = self.U)

                    if qerror > max_err:
                            while True:
                                self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                                self.start = (0,0,0,0,0,self.preangs[3])
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 0, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                # self.start = [0, self.chute1[1], self.chute1[2], 90, self.chute1[4], self.preangs[3]]
                                # ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                # if qerror < 1e-5:
                                #     break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 90, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 180, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 270, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                break


            else:

                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat = self.U)
                if qerror > max_err:
                    while True:
                        self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                        self.start = (0,0,0,0,0,self.preangs[3])
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 0, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 90, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        # self.start = [0, self.chute1[1], self.chute1[2], 90, self.chute1[4], self.chute1[5]]
                        # ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        # if qerror < 1e-5:
                        #     break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 180, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 270, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        break


            self.qerror = qerror
            self.hkl_calc = np.round(self.hrxrd.Ang2HKL(*ang,mat=self.samp, en = self.en, U=self.U),5)


            self.Mu, self.Eta, self.Chi, self.Phi = (ang[0], ang[1], ang[2], ang[3])
            self.Nu, self.Del = (ang[4], ang[5])


            ## Matrices from 4S+2D angles, H. You, JAC, 1999, 32, 614-23
            #
            calculated_matrixes = self.calculate_rotation_matrix_from_diffractometer_angles(
                self.Mu, self.Eta, self.Chi, self.Phi, self.Nu, self.Del
            )

            MU = calculated_matrixes["mu"]
            ETA = calculated_matrixes["eta"]
            CHI = calculated_matrixes["chi"]
            PHI = calculated_matrixes["phi"]
            NU = calculated_matrixes["nu"]
            DEL = calculated_matrixes["del"]
            
            Z = MU.dot(ETA).dot(CHI).dot(PHI)

            n = self.nref
            nc = self.samp.B.dot(n)
            nchat = nc/LA.norm(nc)
            nphi = self.U.dot(nc)
            nphihat = nphi/LA.norm(nphi)

            nz = Z.dot(nphihat)

            A1 = (self.samp.a1)
            A2 = (self.samp.a2)
            A3 = (self.samp.a3)

            vcell = A1.dot(np.cross(A2,A3))

            B1 = np.cross(self.samp.a2,self.samp.a3)/vcell
            B2 = np.cross(self.samp.a3,self.samp.a1)/vcell
            B3 = np.cross(self.samp.a1,self.samp.a2)/vcell

            q = self.samp.Q(self.hkl) # eq (1)
            self.Qshow = q
            normQ = LA.norm(q)
            self.Qnorm = normQ
            Qhat = np.round(q/normQ,5)
            self.FHKL = LA.norm(self.samp.StructureFactor(q, self.en))


            k = (2*np.pi)/(self.lam)
            Ki = k*np.array([0,1,0])
            Kf0 = Ki ##### eq (6)
            Kfnu = k*MAT([ np.sin(rad(self.Del)), np.cos(rad(self.Nu))*np.cos(rad(self.Del)), np.sin(rad(self.Nu))*np.cos(rad(self.Del))])
            Kfnunorm = LA.norm(Kfnu)
            Kfnuhat = Kfnu/Kfnunorm


            taupseudo = deg(np.arccos(np.round(Qhat.dot(nchat),5)))


            ttB1 = deg(np.arccos(np.cos(rad(self.Nu)) * np.cos(rad(self.Del))))
            tB1 = ttB1/2

            alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))

            # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
            qaz = deg(np.arctan2(np.tan(rad(self.Del)),np.sin(rad(self.Nu))))

            # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))

            # QLhat = MAT([ np.cos(rad(tB1))*np.sin(rad(qaz)),
            #         -np.sin(rad(tB1)),
            #         np.cos(rad(tB1))*np.cos(rad(qaz))])

            # taupseudo = deg(np.arccos(QLhat.dot(nz)))

            naz = deg(np.arctan2((nz.dot([1,0,0])),(nz.dot([0,0,1]))))


            if taupseudo == 0 or taupseudo == 180:

                Qphi = Qhat.dot(self.samp.B)
                Qphinorm = LA.norm(Qphi)
                Qphihat = Qphi/Qphinorm

                newref = MAT([np.sqrt(Qphihat[1]**2 + Qphihat[2]**2),
                                      -(Qphihat[0]*Qphihat[1])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2)),
                                      -(Qphihat[0]*Qphihat[2])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2))])
                ntmp = newref
                nctmp = self.samp.B.dot(ntmp)
                nchattmp = nc/LA.norm(nctmp)
                nphitmp = self.U.dot(nctmp)
                nphihattmp = nphitmp/LA.norm(nphitmp)

                nztmp = Z.dot(nphihattmp)
                alphatmp = deg(np.arcsin(-xu.math.vector.VecDot(nztmp,[0,1,0])))
                tautemp = deg(np.arccos(Qhat.dot(newref)))

                arg2 = np.round((np.cos(rad(tautemp))*np.sin(rad(tB1))-np.sin(rad(alphatmp)))/(np.sin(rad(tautemp))*np.cos(rad(tB1))),8)
                if 'flagmap' not in kwargs.keys():

                    print('')
                    print('Q parallel to reference vector, so using {} as reference for Psi'.format(np.round(newref,5)))


            else:
                arg2 = (np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1)))

                arg2 = np.round((np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1))),8)


            psipseudo = deg(np.arccos(arg2))
            # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
            # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))
            # # print(arg3)
            # if arg3 >1:
            #     arg3 = 0.999999999999999999999
            # elif arg3 < -1:
            #     arg3 = -0.99999999999999999999
            # betaout = deg(np.arcsin(arg3))

            betaout = deg(np.arcsin((np.dot(Kfnuhat, nz))))


            arg4 = np.round((np.sin(rad(self.Eta))*np.sin(rad(qaz))+np.sin(rad(self.Mu))*np.cos(rad(self.Eta))*np.cos(rad(qaz)))*np.cos(rad(tB1))-np.cos(rad(self.Mu))*np.cos(rad(self.Eta))*np.sin(rad(tB1)),5)
            # if arg4 >1:
            #   arg4 = 0.999999999999999999999
            # elif arg4 < -1:
            #     arg4 = -0.999999999999999999999
            omega = deg(np.arcsin(arg4))


            self.ttB1 = ttB1
            self.tB1 = ttB1/2
            self.alphain = alphain
            self.qaz = qaz
            self.naz = naz
            self.taupseudo = taupseudo
            self.psipseudo = psipseudo
            self.betaout = betaout
            self.omega = omega


            return [self.Mu, self.Eta, self.Chi, self.Phi, self.Nu, self.Del, self.ttB1, self.tB1, self.alphain, self.qaz, self.naz, self.taupseudo, self.psipseudo, self.betaout, self.omega, "{0:.2e}".format(self.qerror)], [self.fcsv(self.Mu), self.fcsv(self.Eta), self.fcsv(self.Chi), self.fcsv(self.Phi), self.fcsv(self.Nu), self.fcsv(self.Del), self.fcsv(self.ttB1), self.fcsv(self.tB1), self.fcsv(self.alphain), self.fcsv(self.qaz), self.fcsv(self.naz), self.fcsv(self.taupseudo), self.fcsv(self.psipseudo), self.fcsv(self.betaout), self.fcsv(self.omega), self.fcsv(self.hkl_calc[0]), self.fcsv(self.hkl_calc[1]), self.fcsv(self.hkl_calc[2]), "{0:.2e}".format(self.qerror)]
