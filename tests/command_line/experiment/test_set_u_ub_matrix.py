import sys

import pytest
import numpy as np
import epics

from daf.command_line.experiment.set_u_ub_matrix import SetUUB, main


CALCULATED_U =[
        [0.99939, -0.03488, 0.00122],
        [0.03490, 0.99878, -0.03488],
        [-0.00000, 0.03490, 0.99939],
    ]

CALCULATED_UB =[
        [1.15620, -0.04035, 0.00141],
        [0.04037, 1.15549, -0.04035],
        [-0.00000, 0.04038, 1.15620],
    ]

CALCULATED_LATTICE_PARAMETERS = {
    "lparam_a": 5.431013398913497,
    "lparam_b": 5.431013398912699,
    "lparam_c": 5.431013398913498,
    "lparam_alpha": 90.0000000000157,
    "lparam_beta": 90.00003104698489,
    "lparam_gama": 90.0000000182752,
}

FIRST_REFLECTION = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
SECOND_REFLECTION = ["0", "1", "0", "0", "5.28232", "2", "92", "0", "10.5647"]
THIRD_REFLECTION = ["0", "0", "1", "0", "5.28232", "92", "92", "0", "10.5647"]

@pytest.fixture
def motor_dict():
    predefined_dict = {
        "mu": 1.1971657231936314e-22,
        "eta": 11.402686406409414,
        "chi": 35.26439476525327,
        "phi": 44.999999194854674,
        "nu": 0.0,
        "del": 22.805372812818828,
        "tt": 22.805372812818835,
        "theta": 11.402686406409417,
        "alpha": 6.554258723031806,
        "qaz": 90.0,
        "naz": 34.727763787897146,
        "tau": 54.735629207009254,
        "psi": 90.00000458366236,
        "beta": 6.554258723031807,
        "omega": -0.0,
        "hklnow": np.array([1.0, 1.0, 1.0]),
    }
    return predefined_dict


@pytest.fixture
def run_command_line(monkeypatch, request):
    command_line_arguments = []
    marker = request.node.get_closest_marker("fixt_data")
    inptued_args = list(marker.args)
    command_line_arguments.append(inptued_args.pop(0))
    for arg in inptued_args:
        command_line_arguments.append(arg)
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", command_line_arguments)
        obj = SetUUB()
        obj.run_cmd()
        return obj


@pytest.mark.fixt_data("daf.ub", "-r", *FIRST_REFLECTION)
def test_inputed_first_reflection_args(run_command_line):
    obj= run_command_line
    dict_now = obj.io.read()
    print(obj.parsed_args_dict["reflection"])
    print([float(i) for i in FIRST_REFLECTION])
    assert obj.parsed_args_dict["reflection"][:-1] == [float(i) for i in FIRST_REFLECTION]
    assert dict_now["reflections"][0][:-1] == [float(i) for i in FIRST_REFLECTION]


@pytest.mark.fixt_data("daf.ub", "-r", *SECOND_REFLECTION)
def test_inputed_second_reflection_args(run_command_line):
    obj= run_command_line
    dict_now = obj.io.read()
    print(obj.parsed_args_dict["reflection"])
    print([float(i) for i in SECOND_REFLECTION])
    assert obj.parsed_args_dict["reflection"][:-1] == [float(i) for i in SECOND_REFLECTION]
    assert dict_now["reflections"][1][:-1] == [float(i) for i in SECOND_REFLECTION]


@pytest.mark.fixt_data("daf.ub", "-r", *THIRD_REFLECTION)
def test_inputed_third_reflection_args(run_command_line):
    obj= run_command_line
    dict_now = obj.io.read()
    print(obj.parsed_args_dict["reflection"])
    print([float(i) for i in THIRD_REFLECTION])
    assert obj.parsed_args_dict["reflection"][:-1] == [float(i) for i in THIRD_REFLECTION]
    assert dict_now["reflections"][2][:-1] == [float(i) for i in THIRD_REFLECTION]
   
@pytest.mark.fixt_data("daf.ub", "-rn", *["1", "0", "0"])
def test_reflection_now_args(run_command_line):
    obj= run_command_line
    dict_now = obj.io.read()
    print(obj.parsed_args_dict["reflection"])
    print([float(i) for i in THIRD_REFLECTION])
    print(dict_now["reflections"])
    assert obj.parsed_args_dict["reflection_now"]== [float(i) for i in ["1", "0", "0"]]
    assert dict_now["reflections"][3][:3] == [float(i) for i in ["1", "0", "0"]]

@pytest.mark.fixt_data("daf.ub", "-cr", "4")
def test_remove_reflection_args(run_command_line):
    obj= run_command_line
    dict_now = obj.io.read()
    assert len(dict_now["reflections"]) == 3

@pytest.mark.fixt_data("daf.ub", "-u", *["1", "0", "0", "0", "1", "0", "0", "0", "1"])
def test_set_u_args(run_command_line):
    obj= run_command_line
    param = ["1", "0", "0", "0", "1", "0", "0", "0", "1"]
    assert obj.parsed_args_dict["u_matrix"] == [float(i) for i in param]

@pytest.mark.fixt_data("daf.ub", "-ub", *["1", "0", "0", "0", "1", "0", "0", "0", "1"])
def test_set_ub_args(run_command_line):
    obj= run_command_line
    param = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    dict_now = obj.io.read()
    assert dict_now["UB_mat"] == param

@pytest.mark.fixt_data("daf.ub", "-c2", *["1", "2"])
def test_calc_from_2_ref_args(run_command_line):
    obj= run_command_line
    dict_now = obj.io.read()
    for i in range(len(CALCULATED_U)):
        for j in range(len(CALCULATED_U[0])):
            assert dict_now["U_mat"][i][j] ==  pytest.approx(CALCULATED_U[i][j], abs=1e-1)
    for i in range(len(CALCULATED_UB)):
        for j in range(len(CALCULATED_UB[0])):
            assert dict_now["UB_mat"][i][j] ==  pytest.approx(CALCULATED_UB[i][j], abs=1e-1)

@pytest.mark.fixt_data("daf.ub", "-c3", *["1", "2", "3"])
def test_calc_from_3_ref_args(run_command_line):
    obj= run_command_line
    dict_now = obj.io.read()
    for i in range(len(CALCULATED_U)):
        for j in range(len(CALCULATED_U[0])):
            assert dict_now["U_mat"][i][j] ==  pytest.approx(CALCULATED_U[i][j], abs=1e-1)
    for i in range(len(CALCULATED_UB)):
        for j in range(len(CALCULATED_UB[0])):
            assert dict_now["UB_mat"][i][j] ==  pytest.approx(CALCULATED_UB[i][j], abs=1e-1)
    for key, value in CALCULATED_LATTICE_PARAMETERS.items():
        print(dict_now[key])
        assert dict_now[key] == pytest.approx(
             CALCULATED_LATTICE_PARAMETERS[key], abs=1e-3
        )
    
@pytest.mark.fixt_data("daf.ub", "-l")
def test_list_args(run_command_line):
    obj= run_command_line

@pytest.mark.fixt_data("daf.ub", "-s")
def test_show_args(run_command_line):
    obj= run_command_line

@pytest.mark.fixt_data("daf.ub", "-p")
def test_param_args(run_command_line):
    obj= run_command_line

@pytest.mark.fixt_data("daf.ub", "-ca")
def test_clear_all_args(run_command_line):
    obj= run_command_line
