import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.set_u_ub_matrix import SetUUB
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    CALCULATED_U =  np.array([[0.99939, -0.03488, 0.00122],
                             [0.03490, 0.99878, -0.03488],
                             [-0.00000, 0.03490, 0.99939]])
    CALCULATED_UB =  np.array([[1.15620, -0.04035, 0.00141],
                              [0.04037, 1.15549, -0.04035],
                              [-0.00000, 0.04038, 1.15620]])

    def setUp(self):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 10000.0
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
        param = ["1", "0", "0", '0', '5.28232', '0', '2', '0', '10.5647']
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
        arg = "-U"
        full_arg = "Umatrix"
        param = ["1", "0", "0", "0", "1", "0", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [float(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_UBmatrix_THEN_check_parsed_args(
        self,
    ):
        arg = "-UB"
        full_arg = "UBmatrix"
        param = ["1", "0", "0", "0", "1", "0", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [float(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_Calc2_THEN_check_parsed_args(
        self,
    ):
        arg = "-c2"
        full_arg = "Calc2"
        param = ["1", "2"]
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == [int(i) for i in param]

    def test_GIVEN_cli_argument_WHEN_inputing_Calc3_THEN_check_parsed_args(
        self,
    ):
        arg = "-c3"
        full_arg = "Calc3"
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
        full_arg = "Show"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_Params_THEN_check_parsed_args(
        self,
    ):
        arg = "-p"
        full_arg = "Params"
        param = []
        obj = self.make_obj([arg, *param])
        assert obj.parsed_args_dict[full_arg] == True

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", '0', '5.28232', '0', '2', '0', '10.5647']
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        for i in range(len(obj.parsed_args_dict[full_arg])):
            assert dict_now["reflections"][0][i] == obj.parsed_args_dict[full_arg][i]

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", '0', '5.28232', '0', '2', '0', '10.5647']
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        for i in range(len(obj.parsed_args_dict[full_arg])):
            assert dict_now["reflections"][0][i] == obj.parsed_args_dict[full_arg][i]

    def test_GIVEN_cli_argument_WHEN_inputing_reflection_now_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-rn"
        full_arg = "reflection_now"
        param = ["0", "1", "0"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        for i in range(len(obj.parsed_args_dict[full_arg])):
            assert dict_now["reflections"][0][i] == obj.parsed_args_dict[full_arg][i]

    def test_GIVEN_cli_argument_WHEN_inputing_Umatrix_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-U"
        full_arg = "Umatrix"
        param = ["1", "0", "0", "0", "1", "0", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        input_mat = np.array(obj.parsed_args_dict[full_arg]).reshape(3, 3)
        for i in range(len(input_mat)):
            for j in range(len(input_mat[i])):
                assert dict_now["U_mat"][i][j] == input_mat[i][j]

    def test_GIVEN_cli_argument_WHEN_inputing_UBmatrix_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-UB"
        full_arg = "UBmatrix"
        param = ["1", "0", "0", "1", "1", "1", "0", "0", "1"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        input_mat = np.array(obj.parsed_args_dict[full_arg]).reshape(3, 3)
        for i in range(len(input_mat)):
            for j in range(len(input_mat[i])):
                assert dict_now["UB_mat"][i][j] == input_mat[i][j]

    def test_GIVEN_cli_argument_WHEN_inputing_Calc2_THEN_check_if_it_was_written_correctly(
        self,
    ):
        arg = "-r"
        full_arg = "reflection"
        param = ["1", "0", "0", '0', '5.28232', '0', '2', '0', '10.5647']
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        arg = "-r"
        full_arg = "reflection"
        param = ["0", "1", "0", '0', '5.28232', '2', '92', '0', '10.5647']
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        arg = "-c2"
        full_arg = "Calc2"
        param = ["1", "2"]
        obj = self.make_obj([arg, *param])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        for i in range(len(self.CALCULATED_U)):
            for j in range(len(self.CALCULATED_U[i])):
                self.assertAlmostEqual(
                dict_now["U_mat"][i][j], self.CALCULATED_U[i][j], 5
            )



    # def test_GIVEN_cli_argument_WHEN_defining_new_sample_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     sample = "my_si"
    #     obj = self.make_obj(["-m", sample, "-p", "5.4", "5.5", "5.6", "90", "91", "92"])
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert sample == dict_now["Material"]
    #     assert 5.4 == dict_now["lparam_a"]
    #     assert 5.5 == dict_now["lparam_b"]
    #     assert 5.6 == dict_now["lparam_c"]
    #     assert 90.0 == dict_now["lparam_alpha"]
    #     assert 91.0 == dict_now["lparam_beta"]
    #     assert 92.0 == dict_now["lparam_gama"]
    #     assert sample in dict_now["user_samples"].keys()
    #     assert 5.4 == dict_now["user_samples"][sample][0]
    #     assert 5.5 == dict_now["user_samples"][sample][1]
    #     assert 5.6 == dict_now["user_samples"][sample][2]
    #     assert 90.0 == dict_now["user_samples"][sample][3]
    #     assert 91.0 == dict_now["user_samples"][sample][4]
    #     assert 92.0 == dict_now["user_samples"][sample][5]

    # def test_GIVEN_cli_argument_WHEN_defining_new_energy_in_ev_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     energy = 15000
    #     obj = self.make_obj(["-e", str(energy)])
    #     offset = obj.set_energy(energy)
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert offset == dict_now["energy_offset"]

    # def test_GIVEN_cli_argument_WHEN_defining_new_energy_in_wl_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     energy = 1
    #     obj = self.make_obj(["-e", str(energy)])
    #     offset = obj.set_energy(energy)
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert offset == dict_now["energy_offset"]

    # def test_GIVEN_cli_argument_WHEN_defining_idir_and_ndir_THEN_check_if_U_and_UB_was_written_correctly(
    #     self,
    # ):

    #     obj = self.make_obj(
    #         [
    #             "-i",
    #             "1",
    #             "1",
    #             "0",
    #             "-n",
    #             "0",
    #             "0",
    #             "1",
    #         ]
    #     )

    #     U, UB = obj.set_u_and_ub_based_in_idir_ndir([1, 1, 0], [0, 0, 1])
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()

    #     for i in range(len(U)):
    #         for j in range(len(U[i])):
    #             assert U[i][j] == dict_now["U_mat"][i][j]

    #     for i in range(len(UB)):
    #         for j in range(len(UB[i])):
    #             assert UB[i][j] == dict_now["UB_mat"][i][j]

    # def test_GIVEN_cli_argument_WHEN_defining_new_rdir_THEN_check_if_it_was_written_correctly(
    #     self,
    # ):
    #     obj = self.make_obj(["-r", "0", "1", "0"])
    #     obj.run_cmd(obj.parsed_args_dict)
    #     dict_now = du.read()
    #     assert [0, 1, 0] == dict_now["RDir"]
