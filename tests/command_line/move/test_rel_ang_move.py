import sys

import pytest
import numpy as np
import epics

from daf.command_line.move.rel_ang_move import RelAngleMove  # main


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
        obj = RelAngleMove()
        return obj, request.param


@pytest.mark.fixt_data("daf.ramv", "--mu")
def test_move_mu(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["mu"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["mu"]["value"]) == dict_before["motors"][
        "mu"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["mu"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--eta")
def test_move_eta(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["eta"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["eta"]["value"]) == dict_before["motors"][
        "eta"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["eta"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--chi")
def test_move_chi(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["chi"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["chi"]["value"]) == dict_before["motors"][
        "chi"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["chi"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--phi")
def test_move_phi(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["phi"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["phi"]["value"]) == dict_before["motors"][
        "phi"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["phi"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--nu")
def test_move_nu(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["nu"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["nu"]["value"]) == dict_before["motors"][
        "nu"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["nu"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--del")
def test_move_del(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["del"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["del"]["value"]) == dict_before["motors"][
        "del"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["del"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--sample_z")
def test_move_sample_z(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["sample_z"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["sample_z"]["value"]) == dict_before[
        "motors"
    ]["sample_z"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["sample_z"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--sample_x")
def test_move_sample_x(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["sample_x"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["sample_x"]["value"]) == dict_before[
        "motors"
    ]["sample_x"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["sample_x"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--sample_rx")
def test_move_sample_rx(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["sample_rx"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["sample_rx"]["value"]) == dict_before[
        "motors"
    ]["sample_rx"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["sample_rx"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--sample_y")
def test_move_sample_y(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["sample_y"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["sample_y"]["value"]) == dict_before[
        "motors"
    ]["sample_y"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["sample_y"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--sample_ry")
def test_move_sample_ry(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["sample_ry"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["sample_ry"]["value"]) == dict_before[
        "motors"
    ]["sample_ry"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["sample_ry"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--sample_x_s1")
def test_move_sample_x_s1(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["sample_x_s1"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["sample_x_s1"]["value"]) == dict_before[
        "motors"
    ]["sample_x_s1"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["sample_x_s1"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--sample_y_s1")
def test_move_sample_y_s1(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["sample_y_s1"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["sample_y_s1"]["value"]) == dict_before[
        "motors"
    ]["sample_y_s1"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["sample_y_s1"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--diffractomer_ux")
def test_move_diffractomer_ux(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["diffractomer_ux"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["diffractomer_ux"]["value"]) == dict_before[
        "motors"
    ]["diffractomer_ux"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["diffractomer_ux"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--diffractomer_uy")
def test_move_diffractomer_uy(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["diffractomer_uy"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["diffractomer_uy"]["value"]) == dict_before[
        "motors"
    ]["diffractomer_uy"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["diffractomer_uy"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--diffractomer_rx")
def test_move_diffractomer_rx(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(dict_before["motors"]["diffractomer_rx"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["diffractomer_rx"]["value"]) == dict_before[
        "motors"
    ]["diffractomer_rx"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["diffractomer_rx"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--theta_analyzer_crystal")
def test_move_theta_analyzer_crystal(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(
        dict_before["motors"]["theta_analyzer_crystal"]["pv"]
    )
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(
        dict_now["motors"]["theta_analyzer_crystal"]["value"]
    ) == dict_before["motors"]["theta_analyzer_crystal"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["theta_analyzer_crystal"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--2theta_analyzer_crystal")
def test_move_2theta_analyzer_crystal(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    motor_pos_before = epics.caget(
        dict_before["motors"]["2theta_analyzer_crystal"]["pv"]
    )
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(
        dict_now["motors"]["2theta_analyzer_crystal"]["value"]
    ) == dict_before["motors"]["2theta_analyzer_crystal"]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["2theta_analyzer_crystal"]["pv"])
    ) == motor_pos_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--mu", "--eta", "--chi")
def test_move_mu_eta_chi(run_command_line):
    obj, param = run_command_line
    dict_before = obj.io.read()
    mu_before = epics.caget(dict_before["motors"]["mu"]["pv"])
    eta_before = epics.caget(dict_before["motors"]["eta"]["pv"])
    chi_before = epics.caget(dict_before["motors"]["chi"]["pv"])
    obj.run_cmd()
    dict_now = obj.io.read()
    assert pytest.approx(dict_now["motors"]["mu"]["value"]) == dict_before["motors"][
        "mu"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["mu"]["pv"])
    ) == mu_before + float(param)
    assert pytest.approx(dict_now["motors"]["eta"]["value"]) == dict_before["motors"][
        "eta"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["eta"]["pv"])
    ) == eta_before + float(param)
    assert pytest.approx(dict_now["motors"]["chi"]["value"]) == dict_before["motors"][
        "chi"
    ]["value"] + float(param)
    assert pytest.approx(
        epics.caget(dict_now["motors"]["chi"]["pv"])
    ) == chi_before + float(param)


@pytest.mark.fixt_data("daf.ramv", "--eta", "--del")
def test_if_pseudo_angles_are_written_correctly_eta_del(run_command_line):
    obj, param = run_command_line
    obj.run_cmd()
    pseudo_dict = obj.get_pseudo_angles_from_motor_angles()
    dict_now = obj.read_experiment_file()
    del pseudo_dict["q_vector"]
    del pseudo_dict["q_vector_norm"]
    for key, value in pseudo_dict.items():
        assert dict_now[key] == pytest.approx(pseudo_dict[key])


@pytest.mark.fixt_data("daf.ramv", "--chi", "--phi")
def test_if_pseudo_angles_are_written_correctly_chi_phi(run_command_line):
    obj, param = run_command_line
    obj.run_cmd()
    pseudo_dict = obj.get_pseudo_angles_from_motor_angles()
    dict_now = obj.read_experiment_file()
    del pseudo_dict["q_vector"]
    del pseudo_dict["q_vector_norm"]
    for key, value in pseudo_dict.items():
        assert dict_now[key] == pytest.approx(pseudo_dict[key])
