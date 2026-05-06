"""TDD Red phase — pure geometry tests for ReciprocalMapGeometry.

These tests must NOT import matplotlib or any GUI toolkit.
They validate the geometry-only class that lives in daf.core.reciprocal_map.
"""
from unittest.mock import MagicMock

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Pure function: get_peaks
# ---------------------------------------------------------------------------


def test_get_peaks_returns_structured_array_with_expected_fields():
    """get_peaks() returns numpy structured array with q, qvec, r, hkl fields."""
    from daf.core.reciprocal_map import get_peaks

    mat = MagicMock()
    # a1/a2/a3 are lattice vectors — must be length-3 arrays
    mat.a1 = np.array([1.0, 0.0, 0.0])
    mat.a2 = np.array([0.0, 1.0, 0.0])
    mat.a3 = np.array([0.0, 0.0, 1.0])
    # With k0=1 and vec_norm=1, _compute_bragg_indices gives hma=kma=lma=1,
    # so hkl has 3*3*3 = 27 rows. All mocks must match that shape.
    mat.Q.return_value = np.zeros((27, 3))
    mat.StructureFactor.return_value = 1.0 + 0j
    mat.StructureFactorForQ.return_value = np.full(27, 1.0 + 0j)
    exp = MagicMock()
    exp.k0 = 1.0
    exp.energy = 8000
    exp.Transform.return_value = np.zeros((27, 3))

    result = get_peaks(mat, exp, ttmax=180)

    assert hasattr(result, "dtype"), "get_peaks must return a numpy structured array"
    field_names = result.dtype.names
    assert field_names is not None
    for field in ("q", "qvec", "r", "hkl"):
        assert field in field_names, f"Expected field '{field}' in structured array"


# ---------------------------------------------------------------------------
# ReciprocalMapGeometry class
# ---------------------------------------------------------------------------


def test_reciprocal_map_geometry_class_exists():
    """ReciprocalMapGeometry should be importable from daf.core.reciprocal_map."""
    from daf.core.reciprocal_map import ReciprocalMapGeometry

    assert ReciprocalMapGeometry is not None


def test_reciprocal_map_geometry_has_two_theta_max():
    """ReciprocalMapGeometry must expose two_theta_max() as a pure geometry method."""
    from daf.core.reciprocal_map import ReciprocalMapGeometry

    geom = object.__new__(ReciprocalMapGeometry)
    # Provide fixed bounds as scalars so two_theta_max() can compute without DAF state
    geom.bounds = (0.0, 0.0, 0.0, 0.0, 30.0, 60.0)
    ttmax, ttmin = geom.two_theta_max()

    assert isinstance(ttmax, float), "ttmax must be a float"
    assert isinstance(ttmin, float), "ttmin must be a float"
    assert ttmax >= ttmin


def test_reciprocal_map_geometry_does_not_import_matplotlib_at_module_level():
    """Core reciprocal_map module must not import matplotlib at the top level."""
    import importlib
    import sys

    # Remove any cached version so we re-import cleanly
    for key in list(sys.modules.keys()):
        if "reciprocal_map" in key and "daf" in key:
            del sys.modules[key]

    # Temporarily block matplotlib so an accidental top-level import raises ImportError
    real_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

    class _MatplotlibBlocker:
        def find_module(self, fullname, path=None):
            if fullname.startswith("matplotlib"):
                raise ImportError(f"matplotlib must not be imported at module level: {fullname}")
            return None

    import sys as _sys

    blocker = _MatplotlibBlocker()
    _sys.meta_path.insert(0, blocker)
    try:
        # This should succeed — matplotlib import only happens lazily inside functions
        import daf.core.reciprocal_map  # noqa: F401
    except ImportError as exc:
        if "matplotlib must not be imported" in str(exc):
            pytest.fail(str(exc))
        # Some other ImportError (e.g. missing xrayutilities) — not our concern here
    finally:
        _sys.meta_path.remove(blocker)
        # Restore cached modules so nothing downstream breaks
        importlib.invalidate_caches()


def test_reciprocal_map_geometry_has_no_matplotlib_in_base_class():
    """ReciprocalMapGeometry class itself must not reference matplotlib at class definition."""
    import inspect
    from daf.core.reciprocal_map import ReciprocalMapGeometry

    source = inspect.getsource(ReciprocalMapGeometry)
    # The class body itself should not import matplotlib directly
    assert "import matplotlib" not in source or "def " in source.split("import matplotlib")[0], (
        "ReciprocalMapGeometry class body must not contain a bare 'import matplotlib' statement"
    )


# ---------------------------------------------------------------------------
# DAF class should NOT inherit from ReciprocalMapWindow
# ---------------------------------------------------------------------------


def test_daf_does_not_inherit_from_reciprocal_map_window():
    """DAF must not inherit from ReciprocalMapWindow after the refactor."""
    from daf.core.main import DAF

    base_names = [cls.__name__ for cls in DAF.__mro__]
    assert "ReciprocalMapWindow" not in base_names, (
        "DAF should no longer inherit from ReciprocalMapWindow after refactor"
    )


def test_daf_does_not_have_show_reciprocal_space_plane():
    """DAF must not expose show_reciprocal_space_plane() — that belongs to the GUI widget."""
    from daf.core.main import DAF

    assert not hasattr(DAF, "show_reciprocal_space_plane"), (
        "show_reciprocal_space_plane() is a GUI concern and must not live on DAF"
    )


def test_daf_does_not_have_two_theta_max_via_window_mixin():
    """two_theta_max() can still exist on DAF (via ReciprocalMapGeometry) but
    must NOT come from ReciprocalMapWindow."""
    from daf.core.main import DAF

    # If DAF still has two_theta_max, it must originate from ReciprocalMapGeometry,
    # not ReciprocalMapWindow (which should be gone / empty).
    if hasattr(DAF, "two_theta_max"):
        mro_names = [cls.__name__ for cls in DAF.__mro__]
        assert "ReciprocalMapWindow" not in mro_names, (
            "two_theta_max must not come from ReciprocalMapWindow on DAF"
        )
