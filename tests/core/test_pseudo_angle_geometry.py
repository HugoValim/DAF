import numpy as np

from daf.core.geometry import DiffractometerGeometry
from daf.core.matrix_utils import calculate_pseudo_angle_from_geometry


def test_pseudo_angle_geometry_calculates_named_result():
    import xrayutilities as xu

    geometry = DiffractometerGeometry(
        motor_angles=(0.0, 9.17547, 35.26439, 45.0, 0.0, 18.35093),
        sample=xu.materials.Si,
        hkl=np.array([1.0, 1.0, 1.0]),
        wave_length=xu.en2lam(12000),
        reference_direction=np.array([0, 0, 1]),
        u_matrix=np.identity(3),
    )

    result = calculate_pseudo_angle_from_geometry(geometry)

    assert result.theta > 0
    assert result.q_vector_norm > 0
