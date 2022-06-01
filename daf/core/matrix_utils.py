import numpy as np
from numpy import linalg as la
import xrayutilities as xu


def calculate_rotation_matrix_from_diffractometer_angles(
    mu, eta, chi, phi, nu, del_
) -> dict:
    """Calculate the rotation matrix for all diffractometer motors and return a dict with all calculated rotations"""
    # Matrices from 4S+2D angles, H. You, JAC, 1999, 32, 614-23
    phi_rotation = np.array(
        [
            [np.cos(np.deg2rad(phi)), np.sin(np.deg2rad(phi)), 0],
            [-np.sin(np.deg2rad(phi)), np.cos(np.deg2rad(phi)), 0],
            [0, 0, 1],
        ]
    )

    chi_rotation = np.array(
        [
            [np.cos(np.deg2rad(chi)), 0, np.sin(np.deg2rad(chi))],
            [0, 1, 0],
            [-np.sin(np.deg2rad(chi)), 0, np.cos(np.deg2rad(chi))],
        ]
    )

    eta_rotation = np.array(
        [
            [np.cos(np.deg2rad(eta)), np.sin(np.deg2rad(eta)), 0],
            [-np.sin(np.deg2rad(eta)), np.cos(np.deg2rad(eta)), 0],
            [0, 0, 1],
        ]
    )

    mu_rotation = np.array(
        [
            [1, 0, 0],
            [0, np.cos(np.deg2rad(mu)), -np.sin(np.deg2rad(mu))],
            [0, np.sin(np.deg2rad(mu)), np.cos(np.deg2rad(mu))],
        ]
    )

    del_rotation = np.array(
        [
            [np.cos(np.deg2rad(del_)), np.sin(np.deg2rad(del_)), 0],
            [-np.sin(np.deg2rad(del_)), np.cos(np.deg2rad(del_)), 0],
            [0, 0, 1],
        ]
    )

    nu_rotation = np.array(
        [
            [1, 0, 0],
            [0, np.cos(np.deg2rad(nu)), -np.sin(np.deg2rad(nu))],
            [0, np.sin(np.deg2rad(nu)), np.cos(np.deg2rad(nu))],
        ]
    )

    result_dict = {
        "mu": mu_rotation,
        "eta": eta_rotation,
        "chi": chi_rotation,
        "phi": phi_rotation,
        "nu": nu_rotation,
        "del": del_rotation,
    }
    return result_dict


def calculate_pseudo_angle_from_motor_angles(
    Mu: float,
    Eta: float,
    Chi: float,
    Phi: float,
    Nu: float,
    Del: float,
    sample: xu.materials.material.Crystal,
    hkl: "vector",
    wave_length: float,
    rdir: "vector",
    U: "3x3 array",
) -> dict:
    """Calculate all pseudo angles from motor angles and return a dict with the calculated values"""

    calculated_matrixes = calculate_rotation_matrix_from_diffractometer_angles(
        Mu, Eta, Chi, Phi, Nu, Del
    )

    MU = calculated_matrixes["mu"]
    ETA = calculated_matrixes["eta"]
    CHI = calculated_matrixes["chi"]
    PHI = calculated_matrixes["phi"]
    NU = calculated_matrixes["nu"]
    DEL = calculated_matrixes["del"]

    Z = MU.dot(ETA).dot(CHI).dot(PHI)
    n = rdir
    nc = sample.B.dot(n)
    nchat = nc / la.norm(nc)
    nphi = U.dot(nc)
    nphihat = nphi / la.norm(nphi)
    nz = Z.dot(nphihat)

    ttB1 = np.rad2deg(np.arccos(np.cos(np.deg2rad(Nu)) * np.cos(np.deg2rad(Del))))
    tB1 = ttB1 / 2

    A1 = sample.a1
    A2 = sample.a2
    A3 = sample.a3

    vcell = A1.dot(np.cross(A2, A3))

    B1 = np.cross(sample.a2, sample.a3) / vcell
    B2 = np.cross(sample.a3, sample.a1) / vcell
    B3 = np.cross(sample.a1, sample.a2) / vcell

    q = sample.Q(hkl)  # eq (1)
    normQ = la.norm(q)
    Qhat = np.round(q / normQ, 5)

    k = (2 * np.pi) / (wave_length)
    Ki = k * np.array([0, 1, 0])
    Kf0 = Ki  ##### eq (6)
    Kfnu = k * np.array(
        [
            np.sin(np.deg2rad(Del)),
            np.cos(np.deg2rad(Nu)) * np.cos(np.deg2rad(Del)),
            np.sin(np.deg2rad(Nu)) * np.cos(np.deg2rad(Del)),
        ]
    )
    Kfnunorm = la.norm(Kfnu)
    Kfnuhat = Kfnu / Kfnunorm

    taupseudo = np.rad2deg(np.arccos(np.round(Qhat.dot(nchat), 5)))

    alphain = np.rad2deg(np.arcsin(-xu.math.vector.VecDot(nz, [0, 1, 0])))

    qaz = np.rad2deg(np.arctan2(np.tan(np.deg2rad(Del)), np.sin(np.deg2rad(Nu))))

    naz = np.rad2deg(np.arctan2((nz.dot([1, 0, 0])), (nz.dot([0, 0, 1]))))

    if taupseudo == 0 or taupseudo == 180:

        Qphi = Qhat.dot(sample.B)
        Qphinorm = la.norm(Qphi)
        Qphihat = Qphi / Qphinorm

        newref = np.array(
            [
                np.sqrt(Qphihat[1] ** 2 + Qphihat[2] ** 2),
                -(Qphihat[0] * Qphihat[1])
                / (np.sqrt(Qphihat[1] ** 2 + Qphihat[2] ** 2)),
                -(Qphihat[0] * Qphihat[2])
                / (np.sqrt(Qphihat[1] ** 2 + Qphihat[2] ** 2)),
            ]
        )

        ntmp = newref
        nctmp = sample.B.dot(ntmp)
        nchattmp = nc / la.norm(nctmp)
        nphitmp = U.dot(nctmp)
        nphihattmp = nphitmp / la.norm(nphitmp)

        nztmp = Z.dot(nphihattmp)
        alphatmp = np.rad2deg(np.arcsin(-xu.math.vector.VecDot(nztmp, [0, 1, 0])))
        tautemp = np.rad2deg(np.arccos(Qhat.dot(newref)))

        arg2 = np.round(
            (
                np.cos(np.deg2rad(tautemp)) * np.sin(np.deg2rad(tB1))
                - np.sin(np.deg2rad(alphatmp))
            )
            / (np.sin(np.deg2rad(tautemp)) * np.cos(np.deg2rad(tB1))),
            8,
        )

    else:

        arg2 = np.round(
            (
                np.cos(np.deg2rad(taupseudo)) * np.sin(np.deg2rad(tB1))
                - np.sin(np.deg2rad(alphain))
            )
            / (np.sin(np.deg2rad(taupseudo)) * np.cos(np.deg2rad(tB1))),
            8,
        )

    psipseudo = np.rad2deg(np.arccos(arg2))

    betaout = np.rad2deg(np.arcsin((np.dot(Kfnuhat, nz))))

    arg4 = np.round(
        (
            np.sin(np.deg2rad(Eta)) * np.sin(np.deg2rad(qaz))
            + np.sin(np.deg2rad(Mu)) * np.cos(np.deg2rad(Eta)) * np.cos(np.deg2rad(qaz))
        )
        * np.cos(np.deg2rad(tB1))
        - np.cos(np.deg2rad(Mu)) * np.cos(np.deg2rad(Eta)) * np.sin(np.deg2rad(tB1)),
        5,
    )
    omega = np.rad2deg(np.arcsin(arg4))

    result_dict = {
        "alpha": alphain,
        "qaz": qaz,
        "naz": naz,
        "tau": taupseudo,
        "psi": psipseudo,
        "beta": betaout,
        "omega": omega,
        "twotheta": ttB1,
        "theta": tB1,
        "q_vector": q,
        "q_vector_norm": normQ,
    }

    return result_dict
