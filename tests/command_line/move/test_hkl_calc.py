import sys

import pytest
import numpy as np

from daf.command_line.move.hkl_calc import HKLCalc, main
from daf.core.main import DAF


@pytest.fixture
def motor_dict():
    predefined_motor_dict = {
        "mu": 1.1971657231936314e-22,
        "eta": 11.402686406409414,
        "chi": 35.26439476525327,
        "phi": 44.999999194854674,
        "nu": 0.0,
        "del": 22.805372812818828,
        "hklnow": np.array([1.0, 1.0, 1.0]),
    }
    return predefined_motor_dict


predefined_pseudo_dict = {
    "twotheta": 22.805372812818835,
    "theta": 11.402686406409417,
    "alpha": 6.554258723031806,
    "qaz": 90.0,
    "naz": 34.727763787897146,
    "tau": 54.735629207009254,
    "psi": 90.00000458366236,
    "beta": 6.554258723031807,
    "omega": -0.0,
}


@pytest.fixture()
def run_main(monkeypatch, request):
    command_line_arguments = []
    marker = request.node.get_closest_marker("fixt_data")
    inptued_args = list(marker.args)
    command_line_arguments.append(inptued_args.pop(0))
    for args in inptued_args:
        command_line_arguments.append(args)
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", command_line_arguments)
        main()


@pytest.fixture()
def run_command_line(monkeypatch, request):
    command_line_arguments = []
    marker = request.node.get_closest_marker("fixt_data")
    inptued_args = list(marker.args)
    command_line_arguments.append(inptued_args.pop(0))
    for args in inptued_args:
        command_line_arguments.append(args)
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", command_line_arguments)
        obj = HKLCalc()
        return obj


@pytest.mark.fixt_data("daf.ca", "1", "1", "1")
def test_hkl_input(run_command_line):
    obj = run_command_line
    assert obj.parsed_args_dict["hkl-position"] == [1.0, 1.0, 1.0]


@pytest.mark.fixt_data("daf.ca", "1", "1", "1", "--quiet")
def test_quiet_input(
    run_command_line,
):
    obj = run_command_line
    assert obj.parsed_args_dict["quiet"]


@pytest.mark.fixt_data("daf.ca", "1", "1", "1", "-m", "-")
def test_marker_input(
    run_command_line,
):
    obj = run_command_line
    assert obj.parsed_args_dict["marker"] == "-"


@pytest.mark.fixt_data("daf.ca", "1", "1", "1", "-cm", "%")
def test_column_marker_input(
    run_command_line,
):
    obj = run_command_line
    assert obj.parsed_args_dict["column_marker"] == "%"


@pytest.mark.fixt_data("daf.ca", "1", "1", "1", "-s", "16")
def test_size_input(
    run_command_line,
):
    obj = run_command_line
    assert obj.parsed_args_dict["size"] == 16


@pytest.mark.fixt_data(
    "daf.ca", "1", "1", "1", "--quiet", "-m", "-", "-cm", "%", "-s", "16"
)
def test_several_inputs(
    run_command_line,
):
    obj = run_command_line
    assert obj.parsed_args_dict["hkl-position"] == [1.0, 1.0, 1.0]
    assert obj.parsed_args_dict["quiet"]
    assert obj.parsed_args_dict["marker"] == "-"
    assert obj.parsed_args_dict["column_marker"] == "%"
    assert obj.parsed_args_dict["size"] == 16


@pytest.mark.fixt_data("daf.ca", "1", "1", "1")
def test_if_experiment_was_created(run_command_line):
    obj = run_command_line
    assert isinstance(obj.exp, DAF)


@pytest.mark.fixt_data("daf.ca", "1", "1", "1")
def test_if_hkl_was_calculated_right(
    run_command_line,
):
    obj = run_command_line
    error = obj.calculate_hkl(obj.parsed_args_dict["hkl-position"])
    assert error < 1e-4


@pytest.mark.fixt_data("daf.ca", "1", "1", "1")
def test_calculated_angles(run_command_line, motor_dict):
    obj = run_command_line
    obj.run_cmd()
    exp_dict = obj.get_angles_from_calculated_exp()
    # Do not need to compare the hkl value, only angles
    iter_list = list(motor_dict.keys())[:-1]
    for key in iter_list:
        assert pytest.approx(motor_dict[key]) == exp_dict[key]


@pytest.mark.fixt_data("daf.ca", "1", "1", "1")
def test_main_1(
    run_main,
):
    pass


@pytest.mark.fixt_data("daf.ca", "2", "0", "0", "-q")
def test_main_2(
    run_main,
):
    pass
