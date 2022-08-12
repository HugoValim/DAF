import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.experiment_configuration import ExperimentConfiguration, main
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):

    def setUp(self):
        data_sim = gdd.default
        data_sim["simulated"] = True
        data_sim["PV_energy"] = 10000.0
        gdd.generate_file(data=data_sim, file_name=".Experiment")

    def tearDown(self):
        os.system("rm .Experiment")

    @staticmethod
    def make_obj(command_line_args: list) -> ExperimentConfiguration:
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init"]
        for arg in command_line_args:
            testargs.append(arg)
        with patch.object(sys, "argv", testargs):
            obj = ExperimentConfiguration()
        return obj

    def test_GIVEN_full_cli_argument_WHEN_inputing_sample_Ag_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--sample", "Ag"])
        assert obj.parsed_args_dict["sample"] == "Ag"

    def test_GIVEN_cli_argument_WHEN_inputing_sample_Ag_THEN_check_parsed_args(self):
        obj = self.make_obj(["-s", "Ag"])
        assert obj.parsed_args_dict["sample"] == "Ag"

    def test_GIVEN_full_cli_argument_WHEN_inputing_lattice_parameters_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(
            ["--lattice_parameters", "5.4", "5.5", "5.6", "90", "91", "92"]
        )
        assert obj.parsed_args_dict["lattice_parameters"][0] == 5.4
        assert obj.parsed_args_dict["lattice_parameters"][1] == 5.5
        assert obj.parsed_args_dict["lattice_parameters"][2] == 5.6
        assert obj.parsed_args_dict["lattice_parameters"][3] == 90.0
        assert obj.parsed_args_dict["lattice_parameters"][4] == 91.0
        assert obj.parsed_args_dict["lattice_parameters"][5] == 92.0

    def test_GIVEN_cli_argument_WHEN_inputing_lattice_parameters_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-p", "5.4", "5.5", "5.6", "90", "91", "92"])
        assert obj.parsed_args_dict["lattice_parameters"][0] == 5.4
        assert obj.parsed_args_dict["lattice_parameters"][1] == 5.5
        assert obj.parsed_args_dict["lattice_parameters"][2] == 5.6
        assert obj.parsed_args_dict["lattice_parameters"][3] == 90.0
        assert obj.parsed_args_dict["lattice_parameters"][4] == 91.0
        assert obj.parsed_args_dict["lattice_parameters"][5] == 92.0

    def test_GIVEN_full_cli_argument_WHEN_inputing_idir_110_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--idir_print", "1", "1", "0"])
        assert obj.parsed_args_dict["idir_print"][0] == 1.0
        assert obj.parsed_args_dict["idir_print"][1] == 1.0
        assert obj.parsed_args_dict["idir_print"][2] == 0.0

    def test_GIVEN_cli_argument_WHEN_inputing_idir_110_THEN_check_parsed_args(self):
        obj = self.make_obj(["-i", "1", "1", "0"])
        assert obj.parsed_args_dict["idir_print"][0] == 1.0
        assert obj.parsed_args_dict["idir_print"][1] == 1.0
        assert obj.parsed_args_dict["idir_print"][2] == 0.0

    def test_GIVEN_full_cli_argument_WHEN_inputing_ndir_110_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--ndir_print", "1", "1", "0"])
        assert obj.parsed_args_dict["ndir_print"][0] == 1.0
        assert obj.parsed_args_dict["ndir_print"][1] == 1.0
        assert obj.parsed_args_dict["ndir_print"][2] == 0.0

    def test_GIVEN_cli_argument_WHEN_inputing_ndir_110_THEN_check_parsed_args(self):
        obj = self.make_obj(["-n", "1", "1", "0"])
        assert obj.parsed_args_dict["ndir_print"][0] == 1.0
        assert obj.parsed_args_dict["ndir_print"][1] == 1.0
        assert obj.parsed_args_dict["ndir_print"][2] == 0.0

    def test_GIVEN_full_cli_argument_WHEN_inputing_rdir_110_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--rdir", "1", "1", "0"])
        assert obj.parsed_args_dict["rdir"][0] == 1.0
        assert obj.parsed_args_dict["rdir"][1] == 1.0
        assert obj.parsed_args_dict["rdir"][2] == 0.0

    def test_GIVEN_cli_argument_WHEN_inputing_rdir_110_THEN_check_parsed_args(self):
        obj = self.make_obj(["-r", "1", "1", "0"])
        assert obj.parsed_args_dict["rdir"][0] == 1.0
        assert obj.parsed_args_dict["rdir"][1] == 1.0
        assert obj.parsed_args_dict["rdir"][2] == 0.0

    def test_GIVEN_full_cli_argument_WHEN_inputing_energy_10kev_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--energy", "10000"])
        assert obj.parsed_args_dict["energy"] == 10000.0

    def test_GIVEN_cli_argument_WHEN_inputing_energy_10kev_THEN_check_parsed_args(self):
        obj = self.make_obj(["-e", "10000"])
        assert obj.parsed_args_dict["energy"] == 10000.0

    def test_GIVEN_cli_argument_WHEN_inputing_several_args_THEN_check_parsed_args(self):
        obj = self.make_obj(
            [
                "-s",
                "Ag",
                "-p",
                "5.4",
                "5.5",
                "5.6",
                "90",
                "91",
                "92",
                "-i",
                "1",
                "1",
                "0",
                "-n",
                "0",
                "0",
                "1",
            ]
        )
        assert obj.parsed_args_dict["sample"] == "Ag"
        assert obj.parsed_args_dict["lattice_parameters"][0] == 5.4
        assert obj.parsed_args_dict["lattice_parameters"][1] == 5.5
        assert obj.parsed_args_dict["lattice_parameters"][2] == 5.6
        assert obj.parsed_args_dict["lattice_parameters"][3] == 90.0
        assert obj.parsed_args_dict["lattice_parameters"][4] == 91.0
        assert obj.parsed_args_dict["lattice_parameters"][5] == 92.0
        assert obj.parsed_args_dict["idir_print"][0] == 1.0
        assert obj.parsed_args_dict["idir_print"][1] == 1.0
        assert obj.parsed_args_dict["idir_print"][2] == 0.0
        assert obj.parsed_args_dict["ndir_print"][0] == 0.0
        assert obj.parsed_args_dict["ndir_print"][1] == 0.0
        assert obj.parsed_args_dict["ndir_print"][2] == 1.0

    def test_GIVEN_cli_argument_WHEN_defining_predefined_sample_THEN_check_if_it_was_written_correctly(
        self,
    ):
        sample = "Cu"
        obj = self.make_obj(["-s", sample])
        obj.run_cmd()
        dict_now = obj.io.read()
        assert sample == dict_now["Material"]

    def test_GIVEN_cli_argument_WHEN_defining_new_sample_THEN_check_if_it_was_written_correctly(
        self,
    ):
        sample = "my_si"
        obj = self.make_obj(["-s", sample, "-p", "5.4", "5.5", "5.6", "90", "91", "92"])
        obj.run_cmd()
        dict_now = obj.io.read()
        assert sample == dict_now["Material"]
        assert 5.4 == dict_now["lparam_a"]
        assert 5.5 == dict_now["lparam_b"]
        assert 5.6 == dict_now["lparam_c"]
        assert 90.0 == dict_now["lparam_alpha"]
        assert 91.0 == dict_now["lparam_beta"]
        assert 92.0 == dict_now["lparam_gama"]
        assert sample in dict_now["user_samples"].keys()
        assert 5.4 == dict_now["user_samples"][sample][0]
        assert 5.5 == dict_now["user_samples"][sample][1]
        assert 5.6 == dict_now["user_samples"][sample][2]
        assert 90.0 == dict_now["user_samples"][sample][3]
        assert 91.0 == dict_now["user_samples"][sample][4]
        assert 92.0 == dict_now["user_samples"][sample][5]

    def test_GIVEN_cli_argument_WHEN_defining_new_energy_in_ev_THEN_check_if_it_was_written_correctly(
        self,
    ):
        energy = 15000
        obj = self.make_obj(["-e", str(energy)])
        offset = obj.set_energy(energy)
        obj.run_cmd()
        dict_now = obj.io.read()
        assert offset == dict_now["energy_offset"]

    def test_GIVEN_cli_argument_WHEN_defining_new_energy_in_wl_THEN_check_if_it_was_written_correctly(
        self,
    ):
        energy = 1
        obj = self.make_obj(["-e", str(energy)])
        offset = obj.set_energy(energy)
        obj.run_cmd()
        dict_now = obj.io.read()
        assert offset == dict_now["energy_offset"]

    def test_GIVEN_cli_argument_WHEN_defining_idir_and_ndir_THEN_check_if_U_and_UB_was_written_correctly(
        self,
    ):

        obj = self.make_obj(
            [
                "-i",
                "1",
                "1",
                "0",
                "-n",
                "0",
                "0",
                "1",
            ]
        )

        U, UB = obj.set_u_and_ub_based_in_idir_ndir([1, 1, 0], [0, 0, 1])
        obj.run_cmd()
        dict_now = obj.io.read()

        for i in range(len(U)):
            for j in range(len(U[i])):
                assert U[i][j] == dict_now["U_mat"][i][j]

        for i in range(len(UB)):
            for j in range(len(UB[i])):
                assert UB[i][j] == dict_now["UB_mat"][i][j]

    def test_GIVEN_cli_argument_WHEN_defining_new_rdir_THEN_check_if_it_was_written_correctly(
        self,
    ):
        obj = self.make_obj(["-r", "0", "1", "0"])
        obj.run_cmd()
        dict_now = obj.io.read()
        assert [0, 1, 0] == dict_now["RDir"]

    def test_GIVEN_cli_argument_WHEN_inputing_sample_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-s", "Cu"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert "Cu" == dict_now["Material"]

    def test_GIVEN_cli_argument_WHEN_inputing_sample_and_parameters_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-s", "meu_si", "-p", "2", "3", "4", "90", "90", "120"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert "meu_si" == dict_now["Material"]
        assert 2 == dict_now["user_samples"]["meu_si"][0]
        assert 3 == dict_now["user_samples"]["meu_si"][1]
        assert 4 == dict_now["user_samples"]["meu_si"][2]
        assert 90 == dict_now["user_samples"]["meu_si"][3]
        assert 90 == dict_now["user_samples"]["meu_si"][4]
        assert 120 == dict_now["user_samples"]["meu_si"][5]

    def test_GIVEN_cli_argument_WHEN_inputing_idir_and_ndir_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-i", "1", "1", "0", "-n", "0", "0", "1"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert 1 == dict_now["IDir_print"][0]
        assert 1 == dict_now["IDir_print"][1]
        assert 0 == dict_now["IDir_print"][2]
        assert 0 == dict_now["NDir_print"][0]
        assert 0 == dict_now["NDir_print"][1]
        assert 1 == dict_now["NDir_print"][2]

    def test_GIVEN_cli_argument_WHEN_inputing_rdir_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-r", "0", "1", "0"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert 0 == dict_now["RDir"][0]
        assert 1 == dict_now["RDir"][1]
        assert 0 == dict_now["RDir"][2]

    def test_GIVEN_cli_argument_WHEN_inputing_sample_or_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-so", "x+"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert "x+" == dict_now["Sampleor"]

    def test_GIVEN_cli_argument_WHEN_inputing_simulated_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-sim"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["simulated"] == True

    def test_GIVEN_cli_argument_WHEN_inputing_real_THEN_test_for_problems(
        self,
    ):
        obj = self.make_obj([])
        testargs = ["/home/hugo/work/SOL/tmp/daf/command_line/daf.init", "-rl"]
        with patch.object(sys, "argv", testargs):
            main()
        dict_now = obj.io.read()
        assert dict_now["simulated"] == False
        