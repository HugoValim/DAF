import sys
import os

import pytest

from daf.command_line.support.init import Init, main
from daf.utils.daf_paths import DAFPaths as dp
from daf.utils import dafutilities as du

@pytest.fixture
def remove_local_config():
    if os.path.isfile(dp.LOCAL_EXPERIMENT_DEFAULT):
        os.remove(dp.LOCAL_EXPERIMENT_DEFAULT)

@pytest.fixture
def remove_global_config():
    if os.path.isfile(dp.GLOBAL_EXPERIMENT_DEFAULT):
        os.remove(dp.GLOBAL_EXPERIMENT_DEFAULT)

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
def run_command_line(remove_local_config, remove_global_config, monkeypatch, request):
    command_line_arguments = []
    marker = request.node.get_closest_marker("fixt_data")
    inptued_args = list(marker.args)
    command_line_arguments.append(inptued_args.pop(0))
    for args in inptued_args:
        command_line_arguments.append(args)
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", command_line_arguments)
        obj = Init()
        obj.run_cmd()
        return obj

@pytest.mark.fixt_data("daf.init", "-s")
def test_simulated_input(run_command_line):
    obj = run_command_line
    assert obj.parsed_args_dict["simulated"] == True
    print(os.path.isfile(dp.LOCAL_EXPERIMENT_DEFAULT))
    assert os.path.isfile(dp.LOCAL_EXPERIMENT_DEFAULT)

@pytest.mark.fixt_data("daf.init", "-a", "-s")
def test_all_input(run_command_line):
    obj = run_command_line
    assert obj.parsed_args_dict["all"] == True
    assert os.path.isfile(dp.LOCAL_EXPERIMENT_DEFAULT)

@pytest.mark.fixt_data("daf.init", "-g", "-s")
def test_global_input(run_command_line):
    obj = run_command_line
    assert obj.parsed_args_dict["global"] == True
    assert os.path.isfile(dp.GLOBAL_EXPERIMENT_DEFAULT)

@pytest.mark.fixt_data("daf.init", "-k", "test_topic", "-db", "test_db", "-s")
def test_bluesky_configs_input(run_command_line):
    obj = run_command_line
    io = du.DAFIO(read=False)
    file_data = io.only_read()
    assert obj.parsed_args_dict["kafka_topic"] == "test_topic"
    assert obj.parsed_args_dict["scan_db"] == "test_db"
    assert file_data["kafka_topic"] == "test_topic"
    assert file_data["scan_db"] == "test_db"
