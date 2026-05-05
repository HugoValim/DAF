"""Phase 6 TDD tests — CLI deduplication."""
import argparse


def test_add_hkl_display_args_adds_expected_arguments():
    from daf.command_line.move.move_utils import _add_hkl_display_args

    parser = argparse.ArgumentParser()
    _add_hkl_display_args(parser)
    args = parser.parse_args([])

    assert hasattr(args, "quiet")
    assert hasattr(args, "marker")
    assert hasattr(args, "column_marker")
    assert hasattr(args, "size")


def test_add_hkl_display_args_defaults():
    from daf.command_line.move.move_utils import _add_hkl_display_args

    parser = argparse.ArgumentParser()
    _add_hkl_display_args(parser)
    args = parser.parse_args([])

    assert args.quiet is False
    assert args.marker == ""
    assert args.column_marker == ""
    assert args.size == 14


def test_iter_motors_yields_motor_names():
    from daf.utils.dafutilities import iter_motors

    fake_dict = {"motors": {"mu": {"value": 0}, "eta": {"value": 0}}}
    names = list(iter_motors(fake_dict))
    assert "mu" in names
    assert "eta" in names


def test_iter_motors_yields_all_keys():
    from daf.utils.dafutilities import iter_motors

    motors = {"mu": {}, "eta": {}, "chi": {}, "phi": {}, "nu": {}, "del": {}}
    fake_dict = {"motors": motors}
    assert set(iter_motors(fake_dict)) == set(motors.keys())
