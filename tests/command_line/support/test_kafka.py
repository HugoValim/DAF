import sys
import os

import pytest

from daf.command_line.support.kafka import Kafka, main
from daf.utils.daf_paths import DAFPaths as dp
from daf.utils import dafutilities as du


@pytest.fixture
def remove_local_config():
    if os.path.isfile(dp.LOCAL_EXPERIMENT_DEFAULT):
        os.remove(dp.LOCAL_EXPERIMENT_DEFAULT)


@pytest.fixture()
def init_experiment_file(remove_local_config):
    """Create a default experiment file before running kafka tests"""
    from daf.command_line.support.init import Init
    import daf.utils.generate_daf_default as gdd

    data_sim = Init.build_current_file(Init, True)
    data_sim["simulated"] = True
    gdd.generate_file(data=data_sim, file_name=".Experiment")
    yield
    if os.path.isfile(".Experiment"):
        os.remove(".Experiment")


@pytest.fixture()
def run_command_line(init_experiment_file, monkeypatch, request):
    command_line_arguments = []
    marker = request.node.get_closest_marker("fixt_data")
    inptued_args = list(marker.args)
    command_line_arguments.append(inptued_args.pop(0))
    for args in inptued_args:
        command_line_arguments.append(args)
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", command_line_arguments)
        obj = Kafka()
        return obj


@pytest.mark.fixt_data("daf.kafka", "-l")
def test_list_kafka_config(run_command_line):
    obj = run_command_line
    assert obj.parsed_args_dict["list"]
    obj.list_kafka_config()
    io = du.DAFIO(read=False)
    file_data = io.only_read()
    kafka_server = file_data.get("kafka_server", "not configured")
    assert kafka_server == "not configured"


@pytest.mark.fixt_data("daf.kafka", "-b", "localhost:9092")
def test_set_kafka_server(run_command_line):
    obj = run_command_line
    assert obj.parsed_args_dict["server"] == "localhost:9092"
    obj.set_kafka_server()
    io = du.DAFIO(read=False)
    file_data = io.only_read()
    assert file_data["kafka_server"] == "localhost:9092"


@pytest.mark.fixt_data("daf.kafka", "--server", "kafka.example.com:9092")
def test_set_kafka_server_long_form(run_command_line):
    obj = run_command_line
    assert obj.parsed_args_dict["server"] == "kafka.example.com:9092"
    obj.set_kafka_server()
    io = du.DAFIO(read=False)
    file_data = io.only_read()
    assert file_data["kafka_server"] == "kafka.example.com:9092"
