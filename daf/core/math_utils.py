import numpy as np
import math


def unit_vector(vector):
    """Returns the unit vector of the vector."""
    return vector / np.linalg.norm(vector)


def vector_angle(v1, v2, deg=False):
    """Returns the angle in radians between vectors 'v1' and 'v2'::

    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    if deg:
        return np.rad2deg(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def vec_norm(v):
    """
    Calculate the norm of a vector.

    Parameters
    ----------
    v :     list or array-like
        input vector(s), either one vector or an array of vectors with shape
        (n, 3)

    Returns
    -------
    float or ndarray
        vector norm, either a single float or shape (n, )
    """
    if isinstance(v, np.ndarray):
        if len(v.shape) >= 2:
            return np.linalg.norm(v, axis=-1)
    if len(v) != 3:
        raise ValueError("Vector must be of length 3, but has length %d!" % len(v))
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
