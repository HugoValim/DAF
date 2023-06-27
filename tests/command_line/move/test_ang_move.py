import sys

import pytest
import numpy as np
import epics

from daf.command_line.move.ang_move import AngleMove


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


@pytest.fixture(params=["-5", "5"])
def run_command_line(monkeypatch, request):
    command_line_arguments = []
    marker = request.node.get_closest_marker("fixt_data")
    inptued_args = list(marker.args)
    command_line_arguments.append(inptued_args.pop(0))
    for motor in inptued_args:
        command_line_arguments.append(motor)
        command_line_arguments.append(request.param)
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", command_line_arguments)
        obj = AngleMove()
        obj.run_cmd()
        return obj, request.param


@pytest.mark.fixt_data("daf.amv", "--mu")
def test_move_mu(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["mu"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["mu"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--eta")
def test_move_eta(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["eta"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["eta"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--chi")
def test_move_chi(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["chi"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["chi"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--phi")
def test_move_phi(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["phi"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["phi"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--nu")
def test_move_nu(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["nu"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["nu"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--del")
def test_move_del(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["del"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["del"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--sample_z")
def test_move_sample_z(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["sample_z"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["sample_z"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--sample_x")
def test_move_sample_x(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["sample_x"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["sample_x"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--sample_rx")
def test_move_sample_rx(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["sample_rx"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["sample_rx"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--sample_y")
def test_move_sample_y(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["sample_y"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["sample_y"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--sample_ry")
def test_move_sample_ry(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["sample_ry"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["sample_ry"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--sample_x_s1")
def test_move_sample_x_s1(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["sample_x_s1"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["sample_x_s1"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--sample_y_s1")
def test_move_sample_y_s1(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["sample_y_s1"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["sample_y_s1"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--diffractomer_ux")
def test_move_diffractomer_ux(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["diffractomer_ux"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["diffractomer_ux"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--diffractomer_uy")
def test_move_diffractomer_uy(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["diffractomer_uy"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["diffractomer_uy"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--diffractomer_rx")
def test_move_diffractomer_rx(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["diffractomer_rx"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["diffractomer_rx"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--theta_analyzer_crystal")
def test_move_theta_analyzer_crystal(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["theta_analyzer_crystal"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["theta_analyzer_crystal"]["pv"]) == float(
        param
    )


@pytest.mark.fixt_data("daf.amv", "--2theta_analyzer_crystal")
def test_move_2theta_analyzer_crystal(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["2theta_analyzer_crystal"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["2theta_analyzer_crystal"]["pv"]) == float(
        param
    )


# def test_GIVEN_cli_argument_WHEN_eta_is_moved_to_CEN_THEN_check_if_written(
#     ,
# ):
#     pos_to_move = "CEN"
#     obj = .make_obj(["-e", str(pos_to_move)])
#     obj.run_cmd()
#     dict_now = obj.io.read()
#     .assertAlmostEqual(
#         dict_now["motors"]["eta"]["value"], 20.983173898742514, 2
#     )

# def test_GIVEN_cli_argument_WHEN_eta_is_moved_to_CEN_THEN_check_if_written(
#     ,
# ):
#     pos_to_move = "MAX"
#     obj = .make_obj(["-e", str(pos_to_move)])
#     obj.run_cmd()
#     dict_now = obj.io.read()
#     .assertAlmostEqual(
#         dict_now["motors"]["eta"]["value"], 21.809999465942383, 2
#     )

# def test_GIVEN_cli_argument_WHEN_eta_is_moved_to_CEN_passing_the_counter_THEN_check_if_written(
#     ,
# ):
#     pos_to_move = "CEN"
#     obj = .make_obj(["-e", str(pos_to_move), "-co", "mvs2_diode"])
#     obj.run_cmd()
#     dict_now = obj.io.read()
#     .assertAlmostEqual(
#         dict_now["motors"]["eta"]["value"], 21.922770471720945, 2
#     )

# def test_GIVEN_cli_argument_WHEN_eta_is_moved_to_MAX_passing_the_counter_THEN_check_if_written(
#     ,
# ):
#     pos_to_move = "MAX"
#     obj = .make_obj(["-e", str(pos_to_move), "-co", "mvs2_diode"])
#     obj.run_cmd()
#     dict_now = obj.io.read()
#     .assertAlmostEqual(dict_now["motors"]["eta"]["value"], 10.8543, 2)

# def test_GIVEN_cli_argument_WHEN_eta_is_moved_to_CEN_without_main_counter_THEN_check_if_written(
#     ,
# ):
#     pos_to_move = "CEN"
#     obj = .make_obj(["-e", str(pos_to_move)])
#     obj.run_cmd()
#     dict_now = obj.io.read()
#     dict_now["main_scan_counter"] = ""
#     .assertAlmostEqual(
#         dict_now["motors"]["eta"]["value"], 20.983173898742514, 2
#     )

# def test_GIVEN_cli_argument_WHEN_eta_is_moved_to_MAX_without_main_counter_THEN_check_if_written(
#     ,
# ):
#     pos_to_move = "MAX"
#     obj = .make_obj(["-e", str(pos_to_move)])
#     obj.run_cmd()
#     dict_now = obj.io.read()
#     dict_now["main_scan_counter"] = ""
#     .assertAlmostEqual(import argparse as ap


@pytest.mark.fixt_data("daf.amv", "--mu", "--eta", "--chi")
def test_move_mu_eta_chi(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["mu"]["value"] == float(param)
    assert dict_now["motors"]["eta"]["value"] == float(param)
    assert dict_now["motors"]["chi"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["mu"]["pv"]) == float(param)
    assert epics.caget(dict_now["motors"]["eta"]["pv"]) == float(param)
    assert epics.caget(dict_now["motors"]["chi"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--mu", "--eta", "--chi", "--phi")
def test_move_mu_eta_chi_phi(run_command_line):
    obj, param = run_command_line
    dict_now = obj.io.read()
    assert dict_now["motors"]["mu"]["value"] == float(param)
    assert dict_now["motors"]["eta"]["value"] == float(param)
    assert dict_now["motors"]["chi"]["value"] == float(param)
    assert dict_now["motors"]["phi"]["value"] == float(param)
    assert epics.caget(dict_now["motors"]["mu"]["pv"]) == float(param)
    assert epics.caget(dict_now["motors"]["eta"]["pv"]) == float(param)
    assert epics.caget(dict_now["motors"]["chi"]["pv"]) == float(param)
    assert epics.caget(dict_now["motors"]["phi"]["pv"]) == float(param)


@pytest.mark.fixt_data("daf.amv", "--eta", "--del")
def test_if_pseudo_angles_are_written_correctly_eta_del(run_command_line):
    obj, param = run_command_line
    pseudo_dict = obj.get_pseudo_angles_from_motor_angles()
    dict_now = obj.read_experiment_file()
    del pseudo_dict["q_vector"]
    del pseudo_dict["q_vector_norm"]
    for key, value in pseudo_dict.items():
        assert dict_now[key] == pytest.approx(pseudo_dict[key])


@pytest.mark.fixt_data("daf.amv", "--chi", "--phi")
def test_if_pseudo_angles_are_written_correctly_chi_phi(run_command_line):
    obj, param = run_command_line
    pseudo_dict = obj.get_pseudo_angles_from_motor_angles()
    dict_now = obj.read_experiment_file()
    del pseudo_dict["q_vector"]
    del pseudo_dict["q_vector_norm"]
    for key, value in pseudo_dict.items():
        assert dict_now[key] == pytest.approx(pseudo_dict[key])
