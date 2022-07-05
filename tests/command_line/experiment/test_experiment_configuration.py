import os
import sys

import pytest
import unittest
from unittest.mock import patch
import numpy as np

import daf.utils.dafutilities as du
from daf.command_line.experiment.experiment_configuration import ExperimentConfiguration
import daf.utils.generate_daf_default as gdd
from daf.core.main import DAF


class TestDAF(unittest.TestCase):
    predefined_dict = {
        "Mu": 1.1971657231936314e-22,
        "Eta": 11.402686406409414,
        "Chi": 35.26439476525327,
        "Phi": 44.999999194854674,
        "Nu": 0.0,
        "Del": 22.805372812818828,
        "twotheta": 22.805372812818835,
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
        obj = self.make_obj(["--Material", "Ag"])
        assert obj.parsed_args_dict["Material"] == "Ag"

    def test_GIVEN_cli_argument_WHEN_inputing_sample_Ag_THEN_check_parsed_args(self):
        obj = self.make_obj(["-m", "Ag"])
        assert obj.parsed_args_dict["Material"] == "Ag"

    def test_GIVEN_full_cli_argument_WHEN_inputing_lattice_parameters_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(
            ["--Lattice_parameters", "5.4", "5.5", "5.6", "90", "91", "92"]
        )
        assert obj.parsed_args_dict["Lattice_parameters"][0] == 5.4
        assert obj.parsed_args_dict["Lattice_parameters"][1] == 5.5
        assert obj.parsed_args_dict["Lattice_parameters"][2] == 5.6
        assert obj.parsed_args_dict["Lattice_parameters"][3] == 90.0
        assert obj.parsed_args_dict["Lattice_parameters"][4] == 91.0
        assert obj.parsed_args_dict["Lattice_parameters"][5] == 92.0

    def test_GIVEN_cli_argument_WHEN_inputing_lattice_parameters_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["-p", "5.4", "5.5", "5.6", "90", "91", "92"])
        assert obj.parsed_args_dict["Lattice_parameters"][0] == 5.4
        assert obj.parsed_args_dict["Lattice_parameters"][1] == 5.5
        assert obj.parsed_args_dict["Lattice_parameters"][2] == 5.6
        assert obj.parsed_args_dict["Lattice_parameters"][3] == 90.0
        assert obj.parsed_args_dict["Lattice_parameters"][4] == 91.0
        assert obj.parsed_args_dict["Lattice_parameters"][5] == 92.0

    def test_GIVEN_full_cli_argument_WHEN_inputing_idir_110_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--IDir_print", "1", "1", "0"])
        assert obj.parsed_args_dict["IDir_print"][0] == 1.0
        assert obj.parsed_args_dict["IDir_print"][1] == 1.0
        assert obj.parsed_args_dict["IDir_print"][2] == 0.0

    def test_GIVEN_cli_argument_WHEN_inputing_idir_110_THEN_check_parsed_args(self):
        obj = self.make_obj(["-i", "1", "1", "0"])
        assert obj.parsed_args_dict["IDir_print"][0] == 1.0
        assert obj.parsed_args_dict["IDir_print"][1] == 1.0
        assert obj.parsed_args_dict["IDir_print"][2] == 0.0

    def test_GIVEN_full_cli_argument_WHEN_inputing_ndir_110_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--NDir_print", "1", "1", "0"])
        assert obj.parsed_args_dict["NDir_print"][0] == 1.0
        assert obj.parsed_args_dict["NDir_print"][1] == 1.0
        assert obj.parsed_args_dict["NDir_print"][2] == 0.0

    def test_GIVEN_cli_argument_WHEN_inputing_ndir_110_THEN_check_parsed_args(self):
        obj = self.make_obj(["-n", "1", "1", "0"])
        assert obj.parsed_args_dict["NDir_print"][0] == 1.0
        assert obj.parsed_args_dict["NDir_print"][1] == 1.0
        assert obj.parsed_args_dict["NDir_print"][2] == 0.0

    def test_GIVEN_full_cli_argument_WHEN_inputing_rdir_110_THEN_check_parsed_args(
        self,
    ):
        obj = self.make_obj(["--RDir", "1", "1", "0"])
        assert obj.parsed_args_dict["RDir"][0] == 1.0
        assert obj.parsed_args_dict["RDir"][1] == 1.0
        assert obj.parsed_args_dict["RDir"][2] == 0.0

    def test_GIVEN_cli_argument_WHEN_inputing_rdir_110_THEN_check_parsed_args(self):
        obj = self.make_obj(["-r", "1", "1", "0"])
        assert obj.parsed_args_dict["RDir"][0] == 1.0
        assert obj.parsed_args_dict["RDir"][1] == 1.0
        assert obj.parsed_args_dict["RDir"][2] == 0.0

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
                "-m",
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
        assert obj.parsed_args_dict["Material"] == "Ag"
        assert obj.parsed_args_dict["Lattice_parameters"][0] == 5.4
        assert obj.parsed_args_dict["Lattice_parameters"][1] == 5.5
        assert obj.parsed_args_dict["Lattice_parameters"][2] == 5.6
        assert obj.parsed_args_dict["Lattice_parameters"][3] == 90.0
        assert obj.parsed_args_dict["Lattice_parameters"][4] == 91.0
        assert obj.parsed_args_dict["Lattice_parameters"][5] == 92.0
        assert obj.parsed_args_dict["IDir_print"][0] == 1.0
        assert obj.parsed_args_dict["IDir_print"][1] == 1.0
        assert obj.parsed_args_dict["IDir_print"][2] == 0.0
        assert obj.parsed_args_dict["NDir_print"][0] == 0.0
        assert obj.parsed_args_dict["NDir_print"][1] == 0.0
        assert obj.parsed_args_dict["NDir_print"][2] == 1.0

    def test_GIVEN_cli_argument_WHEN_defining_predefined_sample_THEN_check_if_it_was_written_correctly(
        self,
    ):
        sample = "Cu"
        obj = self.make_obj(["-m", sample])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert sample == dict_now["Material"]

    def test_GIVEN_cli_argument_WHEN_defining_new_sample_THEN_check_if_it_was_written_correctly(
        self,
    ):
        sample = "my_si"
        obj = self.make_obj(["-m", sample, "-p", "5.4", "5.5", "5.6", "90", "91", "92"])
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
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
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert offset == dict_now["energy_offset"]

    def test_GIVEN_cli_argument_WHEN_defining_new_energy_in_wl_THEN_check_if_it_was_written_correctly(
        self,
    ):
        energy = 1
        obj = self.make_obj(["-e", str(energy)])
        offset = obj.set_energy(energy)
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
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
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()

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
        obj.run_cmd(obj.parsed_args_dict)
        dict_now = du.read()
        assert [0, 1, 0] == dict_now["RDir"]
