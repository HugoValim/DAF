import numpy as np

def calculate_rotation_matrix_from_diffractometer_angles(
        mu, eta, chi, phi, nu, del_
    ) -> dict:
        """Calculate the rotation matrix for all diffractometer motors and return a dict with all calculated rotations"""
        # Matrices from 4S+2D angles, H. You, JAC, 1999, 32, 614-23
        phi_rotation = MAT(
            [
                [np.cos(rad(phi)), np.sin(rad(phi)), 0],
                [-np.sin(rad(phi)), np.cos(rad(phi)), 0],
                [0, 0, 1],
            ]
        )

        chi_rotation = MAT(
            [
                [np.cos(rad(chi)), 0, np.sin(rad(chi))],
                [0, 1, 0],
                [-np.sin(rad(chi)), 0, np.cos(rad(chi))],
            ]
        )

        eta_rotation = MAT(
            [
                [np.cos(rad(eta)), np.sin(rad(eta)), 0],
                [-np.sin(rad(eta)), np.cos(rad(eta)), 0],
                [0, 0, 1],
            ]
        )

        mu_rotation = MAT(
            [
                [1, 0, 0],
                [0, np.cos(rad(mu)), -np.sin(rad(mu))],
                [0, np.sin(rad(mu)), np.cos(rad(mu))],
            ]
        )

        del_rotation = MAT(
            [
                [np.cos(rad(del_)), np.sin(rad(del_)), 0],
                [-np.sin(rad(del_)), np.cos(rad(del_)), 0],
                [0, 0, 1],
            ]
        )

        nu_rotation = MAT(
            [
                [1, 0, 0],
                [0, np.cos(rad(nu)), -np.sin(rad(nu))],
                [0, np.sin(rad(nu)), np.cos(rad(nu))],
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