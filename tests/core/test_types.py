import numpy as np
import pytest

from daf.core.types import MotorAngles, PseudoAngles, RotationMatrices


def test_pseudo_angles_fields():
    pa = PseudoAngles(
        twotheta=0,
        theta=0,
        alpha=0,
        qaz=0,
        naz=0,
        tau=0,
        psi=0,
        beta=0,
        omega=0,
        q_vector=np.zeros(3),
        q_vector_norm=0.0,
    )
    assert pa.twotheta == 0


def test_rotation_matrices_fields():
    rm = RotationMatrices(
        mu=np.eye(3),
        eta=np.eye(3),
        chi=np.eye(3),
        phi=np.eye(3),
        nu=np.eye(3),
        del_=np.eye(3),
    )
    assert rm.mu.shape == (3, 3)
    assert rm.del_.shape == (3, 3)


def test_motor_angles_fields():
    ma = MotorAngles(mu=0.0, eta=0.0, chi=0.0, phi=0.0, nu=0.0, del_=0.0)
    assert ma.nu == 0.0


def test_calculate_rotation_matrix_returns_rotation_matrices_type():
    from daf.core.matrix_utils import (
        calculate_rotation_matrix_from_diffractometer_angles,
    )

    result = calculate_rotation_matrix_from_diffractometer_angles(0, 0, 0, 0, 0, 0)
    assert isinstance(result, RotationMatrices)
    assert hasattr(result, "mu")
    assert hasattr(result, "del_")


def test_rotation_matrices_attribute_access():
    from daf.core.matrix_utils import (
        calculate_rotation_matrix_from_diffractometer_angles,
    )

    result = calculate_rotation_matrix_from_diffractometer_angles(0, 0, 0, 0, 0, 0)
    assert result.mu.shape == (3, 3)
    assert result.eta.shape == (3, 3)
    assert result.chi.shape == (3, 3)
    assert result.phi.shape == (3, 3)
    assert result.nu.shape == (3, 3)
    assert result.del_.shape == (3, 3)
