import sys
import os

import pytest

from daf.command_line.support.reset import Reset
from daf.command_line.experiment.operation_mode import OperationMode
from daf.utils.daf_paths import DAFPaths as dp
from daf.utils import dafutilities as du

@pytest.fixture
def remove_local_config():
    if os.path.isfile(dp.LOCAL_EXPERIMENT_DEFAULT):
        os.remove(dp.LOCAL_EXPERIMENT_DEFAULT)


@pytest.fixture()
def set_mode(monkeypatch):
    command_line_arguments = []
    inptued_args = ["daf.mode", "215"]
    command_line_arguments.append(inptued_args.pop(0))
    for args in inptued_args:
        command_line_arguments.append(args)
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", command_line_arguments)
        obj = OperationMode()
        obj.run_cmd()
        return obj

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
        obj = Reset()
        return obj

@pytest.mark.skip
@pytest.mark.fixt_data("daf.reset")
def test_no_input(set_mode, run_command_line):
    obj = run_command_line
    io = du.DAFIO(read=False)
    file_data = io.only_read()
    print(os.system("pwd"))
    assert file_data["Mode"] == "215"
    obj.run_cmd()
    file_data_2 = io.only_read()
    assert file_data_2["Mode"] == "2052"

@pytest.mark.fixt_data("daf.reset", "-g")
def test_remove_global_input(remove_local_config, set_mode, run_command_line):
    obj = run_command_line
    io = du.DAFIO(read=False)
    file_data = io.only_read()
    assert file_data["Mode"] == "215"
    obj.run_cmd()
    file_data_2 = io.only_read()
    assert file_data_2["Mode"] == "2052"

@pytest.mark.fixt_data("daf.reset", "--hard")
def test_reset_hard_input(remove_local_config, set_mode, run_command_line):
    obj = run_command_line
    obj.run_cmd()
    assert not os.path.isdir(dp.DAF_CONFIGS)










# import os
# import sys

# import pytest
# import unittest
# from unittest.mock import patch

# import daf.utils.dafutilities as du
# from daf.command_line.support.reset import Reset, main
# import daf.utils.generate_daf_default as gdd
# from daf.command_line.support.init import Init


# class TestDAF(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):import os
# import sys

# import pytest
# import unittest
# from unittest.mock import patch

# import daf.utils.dafutilities as du
# from daf.command_line.support.reset import Reset, main
# import daf.utils.generate_daf_default as gdd
# from daf.command_line.support.init import Init


# class TestDAF(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         data_sim = Init.build_current_file(Init, True)
#         data_sim["simulated"] = True
#         data_sim["PV_energy"] = 1
#         gdd.generate_file(data=data_sim, file_name=".Experiment")

#     @classmethod
#     def tearDownClass(cls):
#         os.remove(".Experiment")
#         os.remove("Log")

#     @staticmethod
#     def make_obj(command_line_args: list) -> Reset:
#         testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
#         for arg in command_line_args:
#             testargs.append(arg)
#         with patch.object(sys, "argv", testargs):
#             obj = Reset()
#         return obj

#     def test_GIVEN_cli_argument_WHEN_inputing_hard_option_THEN_check_parsed_args(self):
#         obj = self.make_obj(["--hard"])
#         assert obj.parsed_args_dict["hard"] == True

#     def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_check_if_it_was_written_correctly(
#         self,
#     ):
#         obj = self.make_obj([])
#         obj.experiment_file_dict["Mode"] = "2023"
#         obj.write_to_experiment_file({})
#         dict_now = obj.io.read()
#         assert obj.experiment_file_dict["Mode"] == "2023"
#         obj = self.make_obj([])
#         obj.run_cmd()
#         dict_now = obj.io.read()
#         assert dict_now["Mode"] == "2052"

#     def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_test_for_problems(
#         self,
#     ):
#         obj = self.make_obj([])
#         obj.experiment_file_dict["Mode"] = "2023"
#         obj.write_to_experiment_file({})
#         dict_now = obj.io.read()
#         assert dict_now["Mode"] == "2023"
#         testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
#         with patch.object(sys, "argv", testargs):
#             main()
#         dict_now = obj.io.read()
#         assert dict_now["Mode"] == "2052"

#         os.remove(".Experiment")
#         os.remove("Log")

#     @staticmethod
#     def make_obj(command_line_args: list) -> Reset:
#         testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
#         for arg in command_line_args:
#             testargs.append(arg)
#         with patch.object(sys, "argv", testargs):
#             obj = Reset()
#         return obj

#     def test_GIVEN_cli_argument_WHEN_inputing_hard_option_THEN_check_parsed_args(self):
#         obj = self.make_obj(["--hard"])
#         assert obj.parsed_args_dict["hard"] == True

#     def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_check_if_it_was_written_correctly(
#         self,
#     ):
#         obj = self.make_obj([])
#         obj.experiment_file_dict["Mode"] = "2023"
#         obj.write_to_experiment_file({})
#         dict_now = obj.io.read()
#         assert obj.experiment_file_dict["Mode"] == "2023"
#         obj = self.make_obj([])
#         obj.run_cmd()
#         dict_now = obj.io.read()
#         assert dict_now["Mode"] == "2052"

#     def test_GIVEN_cli_argument_WHEN_inputing_all_THEN_test_for_problems(
#         self,
#     ):
#         obj = self.make_obj([])
#         obj.experiment_file_dict["Mode"] = "2023"
#         obj.write_to_experiment_file({})
#         dict_now = obj.io.read()
#         assert dict_now["Mode"] == "2023"
#         testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
#         with patch.object(sys, "argv", testargs):
#             main()
#         dict_now = obj.io.read()
#         assert dict_now["Mode"] == "2052"
