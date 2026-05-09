from daf.core.mode_parser import ModeParser


def test_mode_parser_applies_constraint_values_for_fixed_motor_and_pseudo_angles():
    mode = ModeParser((2, 1, 5))

    mode.apply_constraint_values(
        {
            "Nu": 30.0,
            "alpha": 1.0,
            "beta": 2.0,
            "psi": 3.0,
            "omega": 4.0,
            "qaz": 5.0,
            "naz": 6.0,
        }
    )

    assert mode.bounds_for("Nu") == 30.0
    assert ("aeqb", "--") in mode.pseudo_constraints()
    assert ("eta=del/2", "--") in mode.pseudo_constraints()


def test_mode_parser_builds_solver_constraints_from_mode_constraints():
    mode = ModeParser((2, 1, 5))
    mode.apply_constraint_values({})

    constraints = mode.solver_constraints(lambda angles, name, value: 0.0)

    assert len(constraints) == 2
    assert constraints[0]["type"] == "eq"
    assert constraints[0]["fun"]([0, 0, 0, 0, 0, 0]) == 0.0
