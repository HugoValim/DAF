"""Phase 4 TDD tests — extract large functions."""
import pandas as pd
import pytest

from daf.core.main import DAF, _SCAN_COLUMNS


def _make_daf_no_constraints():
    return DAF(2, 0, 5, 2)


def _make_daf_with_pseudo_constraint():
    # Mode 2052: nu fixed + alpha=beta + eta fixed + mu fixed => has pseudo constraints
    return DAF(2, 0, 5, 2)


# --- _build_constraints ---


def test_build_constraints_returns_none_when_no_constraints():
    daf = _make_daf_no_constraints()
    # Ensure no pseudo constraints
    daf.pseudo_constraints_w_value_list = []
    result = daf._build_constraints()
    assert result is None


def test_build_constraints_returns_list_when_constraints_present():
    daf = DAF(2, 1, 5)  # mode with pseudo constraints
    daf.pseudo_constraints_w_value_list = [("alpha", 0.0)]
    result = daf._build_constraints()
    assert isinstance(result, list)
    assert len(result) == 1
    assert all("type" in c and "fun" in c for c in result)


# --- _build_scan_dataframe ---


def test_scan_columns_constant_exists():
    assert isinstance(_SCAN_COLUMNS, list)
    assert "Mu" in _SCAN_COLUMNS
    assert "Error" in _SCAN_COLUMNS


def test_build_scan_dataframe_shape():
    daf = _make_daf_no_constraints()
    row = [0.0] * len(_SCAN_COLUMNS)
    df = daf._build_scan_dataframe([row])
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == _SCAN_COLUMNS
    assert len(df) == 1


# --- cli_formatting extractions ---


def test_format_motor_section_returns_string():
    from daf.core.cli_formatting import DAFFormatter

    formatter = DAFFormatter()
    result = formatter._format_motor_section(
        del_val=0.0, eta_val=0.0, chi_val=0.0,
        phi_val=0.0, nu_val=0.0, mu_val=0.0,
    )
    assert isinstance(result, list)
    assert len(result) == 2


def test_format_constraint_section_returns_string():
    from daf.core.cli_formatting import DAFFormatter
    from daf.core.mode_parser import ModeParser

    mode = ModeParser((2, 1, 5, 2, 0))
    formatter = DAFFormatter()
    result = formatter._format_constraint_section(mode, [], 0.0)
    assert isinstance(result, list)
    assert len(result) == 2
