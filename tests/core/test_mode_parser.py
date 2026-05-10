"""Unit tests for ModeParser collaboration interface (GitHub issue #3)."""

import pytest

from daf.core.mode_parser import ModeParser


class TestModeParserBounds:
    def test_bounds_for_free_motor_returns_default_tuple(self):
        # Mode (0, 1, 5, 0, 0): no fixed motors; alpha=beta pseudo-constraint only
        parser = ModeParser((0, 1, 5, 0, 0))
        assert parser.bounds_for("Mu") == (-180, 180)
        assert parser.bounds_for("Eta") == (-180, 180)
        assert parser.bounds_for("Chi") == (-5, 95)
        assert parser.bounds_for("Phi") == (30, 400)
        assert parser.bounds_for("Nu") == (-180, 180)
        assert parser.bounds_for("Del") == (-180, 180)

    def test_bounds_for_fixed_motor_returns_zero(self):
        parser = ModeParser((2, 0, 1, 4, 0))  # Nu, Eta, Phi fixed
        assert parser.bounds_for("Nu") == 0
        assert parser.bounds_for("Eta") == 0
        assert parser.bounds_for("Phi") == 0
        assert parser.bounds_for("Mu") == (-180, 180)

    def test_bounds_for_invalid_motor_raises_key_error(self):
        parser = ModeParser((2, 0, 5, 2))
        with pytest.raises(KeyError):
            parser.bounds_for("X")

    def test_set_bound_updates_bound(self):
        parser = ModeParser((2, 0, 5, 2))
        parser.set_bound("Mu", 45)
        assert parser.bounds_for("Mu") == 45

    def test_set_bound_updates_motor_bounds_dict(self):
        parser = ModeParser((2, 0, 5, 2))
        parser.set_bound("Mu", 45)
        assert parser.motor_bounds["Mu"] == 45


class TestModeParserFixedMotors:
    def test_fixed_motors_with_no_fixed_motors(self):
        parser = ModeParser((0, 0, 1, 2, 3))
        assert parser.fixed_motors() == ["Eta", "Mu", "Chi"]

    def test_fixed_motors_with_some_fixed(self):
        parser = ModeParser((2, 1, 5))  # Nu fixed
        assert parser.fixed_motors() == ["Nu"]

    def test_is_motor_fixed_returns_true_for_fixed(self):
        parser = ModeParser((2, 0, 1, 4, 0))
        assert parser.is_motor_fixed("Nu") is True
        assert parser.is_motor_fixed("Eta") is True

    def test_is_motor_fixed_returns_false_for_free(self):
        parser = ModeParser((2, 0, 1, 4, 0))
        assert parser.is_motor_fixed("Mu") is False


class TestModeParserConstraints:
    def test_motor_constraints(self):
        parser = ModeParser((2, 0, 1, 4, 0))
        assert parser.motor_constraints == ["Nu", "Eta", "Phi"]

    def test_pseudo_angle_constraints(self):
        parser = ModeParser((2, 1, 5))
        assert parser.pseudo_angle_constraints == ["aeqb", "eta=del/2"]

    def test_pseudo_constraints_initial(self):
        parser = ModeParser((2, 1, 5))
        assert parser.pseudo_constraints() == [
            ("aeqb", "--"),
            ("eta=del/2", "--"),
        ]

    def test_set_pseudo_constraints_updates_list(self):
        parser = ModeParser((2, 1, 5))
        parser.set_pseudo_constraints([("aeqb", "--"), ("eta=del/2", 10)])
        assert parser.pseudo_constraints() == [
            ("aeqb", "--"),
            ("eta=del/2", 10),
        ]

    def test_constraint_columns(self):
        parser = ModeParser((2, 1, 5, 2, 0))
        assert parser.constraint_columns() == (2, 1, 5, 2, 0)


class TestModeParserBoundsTuple:
    def test_bounds_tuple_order(self):
        parser = ModeParser((2, 0, 1, 4, 0))
        assert parser.bounds_tuple == (
            parser.bounds_for("Mu"),
            parser.bounds_for("Eta"),
            parser.bounds_for("Chi"),
            parser.bounds_for("Phi"),
            parser.bounds_for("Nu"),
            parser.bounds_for("Del"),
        )
