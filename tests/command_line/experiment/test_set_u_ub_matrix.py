import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.set_u_ub_matrix import SetUUB, main
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    CALCULATED_U = np.array(
        [
            [0.99939, -0.03488, 0.00122],
            [0.03490, 0.99878, -0.03488],
            [-0.00000, 0.03490, 0.99939],
        ]
    )
    CALCULATED_UB = np.array(
        [
            [1.15620, -0.04035, 0.00141],
            [0.04037, 1.15549, -0.04035],
            [-0.00000, 0.04038, 1.15620],
        ]
    )
    CALCULATED_LATTICE_PARAMETERS = {
        "lparam_a": 5.431013398913497,
        "lparam_b": 5.431013398912699,
        "lparam_c": 5.431013398913498,
        "lparam_alpha": 90.0000000000157,
        "lparam_beta": 90.00003104698489,
        "lparam_gama": 90.0000000182752,
    }

    def setUp(self):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 1
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> SetUUB:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.ub"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = SetUUB()
        return obj

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_THEN_check_parsed_args(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [float(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_now_THEN_check_parsed_args(
        self,
    ):
        arg = "-rn"
        full_arg = "reflection_now"
        param = ["1", "0", "0"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [float(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_Umatrix_THEN_check_parsed_args(
        self,
    ):
        arg = "-u"
        full_arg = "u_matrix"
        param = ["1", "0", "0", "0", "1", "0", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [float(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_UBmatrix_THEN_check_parsed_args(
        self,
    ):
        arg = "-ub"
        full_arg = "ub_matrix"
        param = ["1", "0", "0", "0", "1", "0", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [float(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_Calc2_THEN_check_parsed_args(
        self,
    ):
        arg = "-c2"
        full_arg = "calc_from_2_reflections"
        param = ["1", "2"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [int(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_Calc3_THEN_check_parsed_args(
        self,
    ):
        arg = "-c3"
        full_arg = "calc_from_3_reflections"
        param = ["1", "2", "3"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [int(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_clear_reflections_THEN_check_parsed_args(
        self,
    ):
        arg = "-cr"
        full_arg = "clear_reflections"
        param = ["1", "2", "3"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [int(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_clear_all_THEN_check_parsed_args(
        self,
    ):
        arg = "-ca"
        full_arg = "clear_all"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_check_parsed_args(
        self,
    ):
        arg = "-l"
        full_arg = "list"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_Show_THEN_check_parsed_args(
        self,
    ):
        arg = "-s"
        full_arg = "show"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_Params_THEN_check_parsed_args(
        self,
    ):
        arg = "-p"
        full_arg = "params"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        dict_now = obj.io.read()
        for i in range(len(obj.parsed_args_dict[full_arg])):
            assert dict_now["reflections"][0][i] == obj.parsed_args_dict[full_arg][i]

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        dict_now = obj.io.read()
        for i in range(len(obj.parsed_args_dict[full_arg])):
            assert dict_now["reflections"][0][i] == obj.parsed_args_dict[full_arg][i]

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_now_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-rn"
        full_arg = "reflection_now"
        param = ["0", "1", "0"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        dict_now = obj.io.read()
        for i in range(len(obj.parsed_args_dict[full_arg])):
            assert dict_now["reflections"][0][i] == obj.parsed_args_dict[full_arg][i]

    def test_GIVEN_cli_argument_WHEN_inputing_Umatrix_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-u"
        full_arg = "u_matrix"
        param = ["1", "0", "0", "0", "1", "0", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        dict_now = obj.io.read()
        input_mat = np.array(obj.parsed_args_dict[full_arg]).reshape(3, 3)
        for i in range(len(input_mat)):
            for j in range(len(input_mat[i])):
                assert dict_now["U_mat"][i][j] == input_mat[i][j]

    def test_GIVEN_cli_argument_WHEN_inputing_UBmatrix_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-ub"
        full_arg = "ub_matrix"
        param = ["1", "0", "0", "1", "1", "1", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        dict_now = obj.io.read()
        input_mat = np.array(obj.parsed_args_dict[full_arg]).reshape(3, 3)
        for i in range(len(input_mat)):
            for j in range(len(input_mat[i])):
                assert dict_now["UB_mat"][i][j] == input_mat[i][j]

    def test_GIVEN_cli_argument_WHEN_inputing_Calc2_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "1", "0", "0", "5.28232", "2", "92", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        arg = "-c2"
        full_arg = "calc_from_2_reflections"
        param = ["1", "2"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        dict_now = obj.io.read()
        for i in range(len(self.CALCULATED_U)):
            for j in range(len(self.CALCULATED_U[i])):
                self.assertAlmostEqual(
                    dict_now["U_mat"][i][j], self.CALCULATED_U[i][j], 5
                )
        for i in range(len(self.CALCULATED_UB)):
            for j in range(len(self.CALCULATED_UB[i])):
                self.assertAlmostEqual(
                    dict_now["UB_mat"][i][j], self.CALCULATED_UB[i][j], 5
                )

    def test_GIVEN_cli_argument_WHEN_inputing_Calc3_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "1", "0", "0", "5.28232", "2", "92", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "0", "1", "0", "5.28232", "92", "92", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-c3"
        full_arg = "calc_from_3_reflections"
        param = ["1", "2", "3"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()
        dict_now = obj.io.read()

        for i in range(len(self.CALCULATED_U)):
            for j in range(len(self.CALCULATED_U[i])):
                self.assertAlmostEqual(
                    dict_now["U_mat"][i][j], self.CALCULATED_U[i][j], 5
                )
        for i in range(len(self.CALCULATED_UB)):
            for j in range(len(self.CALCULATED_UB[i])):
                self.assertAlmostEqual(
                    dict_now["UB_mat"][i][j], self.CALCULATED_UB[i][j], 4
                )
        for key, value in self.CALCULATED_LATTICE_PARAMETERS.items():
            self.assertAlmostEqual(
                dict_now[key], self.CALCULATED_LATTICE_PARAMETERS[key], 5
            )

    def test_GIVEN_cli_argument_WHEN_inputing_clear_reflections_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "1", "0", "0", "5.28232", "2", "92", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "0", "1", "0", "5.28232", "92", "92", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-cr"
        full_arg = "clear_reflections"
        param = ["1", "2"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd()

        dict_now = obj.io.read()
        assert len(dict_now["reflections"]) == 1

    def test_GIVEN_cli_argument_WHEN_inputing_clear_all_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "1", "0", "0", "5.28232", "2", "92", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "0", "1", "0", "5.28232", "92", "92", "0", "10.5647"]
        obj = self.make_obj([arg, *param])
        obj.en = 1  #  Set to the right energy
        obj.run_cmd()
        arg = "-ca"
        full_arg = "clear_all"
        param = []
        obj = self.make_obj([arg, *param])
        obj.run_cmd()

        dict_now = obj.io.read()
        assert len(dict_now["reflections"]) == 0

    def test_GIVEN_cli_argument_WHEN_inputing_list_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-l"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_Params_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-p",
        ]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_Show_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-s",
        ]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_clear_reflections_THEN_test_for_problems(
        self,
    ):
        testargs = [
            "/home/hugo/work/SOL/tmp/daf/command_line/daf.init",
            "-cr",
        ]
        with patch.object(sys, "argv", testargs):
            main()


    def test_GIVEN_cli_argument_WHEN_inputing_reflection_1_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_2_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "0", "1", "0", "0", "5.28232", "2", "92", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_3_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "0", "0", "1", "0", "5.28232", "92", "92", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_c2_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "0", "0", "1", "0", "5.28232", "92", "92", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-c2", "1", "2"]
        with patch.object(sys, "argv", testargs):
            main()

    def test_GIVEN_cli_argument_WHEN_inputing_c3_THEN_test_for_problems(
        self,
    ):
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "1", "0", "0", "0", "5.28232", "0", "2", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "0", "1", "0", "0", "5.28232", "2", "92", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "0", "0", "1", "0", "5.28232", "92", "92", "0", "10.5647"]
        with patch.object(sys, "argv", testargs):
            main()
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-c3", "1", "2", "3"]
        with patch.object(sys, "argv", testargs):
            main()

