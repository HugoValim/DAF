#!/usr/bin/env python3

import os
from os import path

import argparse as ap
import numpy as np
import yaml

from daf.utils.log import daf_log
from daf.utils import dafutilities as du
from daf.utils import daf_paths as dp
from daf.command_line.experiment.experiment_utils import ExperimentBase


class ManageCounters(ExperimentBase):
    DESC = """Manage counter configuration files"""
    EPI = """
    Eg:
       daf.mc -s default
       daf.mc -n new_config
       daf.mc -lc new_config
       daf.mc -r my_setup1 my_setup2 my_setup3
       daf.mc -rc new_config counter1 
        """
    YAML_PREFIX = "config."
    YAML_SUFIX = ".yml"

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.write_flag = False

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-s",
            "--set_default",
            metavar="config name",
            type=str,
            help="Set default counter file to be used in scans",
        )
        self.parser.add_argument(
            "-n", "--new", metavar="config name", type=str, help="Create a new setup"
        )
        self.parser.add_argument(
            "-r", "--remove", metavar="file", nargs="*", help="Remove a setup"
        )
        self.parser.add_argument(
            "-a",
            "--add_counter",
            metavar="counter",
            nargs="*",
            help="Add a counter to a config file",
        )
        self.parser.add_argument(
            "-rc",
            "--remove_counter",
            metavar="file",
            nargs="*",
            help="Remove counters from a config file",
        )
        self.parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List all setups, showing in which one you are",
        )
        self.parser.add_argument(
            "-lc",
            "--list_counters",
            metavar="file",
            nargs="*",
            help="List counters in a specific file, more than one file can be passed",
        )
        self.parser.add_argument(
            "-lac",
            "--list_all_counters",
            action="store_true",
            help="List all counters available",
        )
        self.parser.add_argument(
            "-m",
            "--main-counter",
            metavar="counter",
            type=str,
            help="Set the main counter during a scan",
        )
        args = self.parser.parse_args()
        return args

    @staticmethod
    def read_yaml(file_path: str) -> list:
        with open(file_path) as file:
            data = yaml.safe_load(file)
            return data

    @staticmethod
    def write_yaml(list_: list, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(list_, file)

    def get_full_file_path(self, file_name: str) -> str:
        """Get full file path of a config file and return it"""
        yaml_file_name = self.YAML_PREFIX + file_name + self.YAML_SUFIX
        user_configs = os.listdir(dp.SCAN_UTILS_USER_PATH)
        sys_configs = os.listdir(dp.SCAN_UTILS_SYS_PATH)
        if yaml_file_name in sys_configs:
            path_to_use = dp.SCAN_UTILS_SYS_PATH
        else:
            path_to_use = dp.SCAN_UTILS_USER_PATH
        full_file_path = path.join(path_to_use, yaml_file_name)
        return full_file_path

    @staticmethod
    def list_configuration_files() -> None:
        """List all configuration files, both user and system configuration."""
        user_configs = os.listdir(dp.SCAN_UTILS_USER_PATH)
        sys_configs = os.listdir(dp.SCAN_UTILS_SYS_PATH)
        all_configs = user_configs + sys_configs
        configs = [
            i for i in all_configs if len(i.split(".")) == 3 and i.endswith(".yml")
        ]
        configs.sort()
        for i in configs:
            print(i.split(".")[1])

    @staticmethod
    def list_all_counters() -> None:
        """List all available counters for the current beamline"""
        with open(dp.DEFAULT_SCAN_UTILS_CONFIG) as conf:
            config_data = yaml.safe_load(conf)
        counters = config_data["counters"].keys()
        for i in counters:
            print(i)

    def set_default_counters(self, default_counter: str) -> None:
        """Set the file that should be used in the further scans"""
        self.experiment_file_dict["default_counters"] = (
            self.YAML_PREFIX + default_counter + self.YAML_SUFIX
        )
        self.write_flag = True

    def create_new_configuration_file(self, file_name: str) -> None:
        """Create a new empty configuration counter file, counters should be added in advance."""
        yaml_file_name = self.YAML_PREFIX + file_name + self.YAML_SUFIX
        full_file_path = path.join(dp.SCAN_UTILS_USER_PATH, yaml_file_name)
        self.write_yaml([], full_file_path)

    def list_counter_in_a_configuration_file(self, file_name: str) -> None:
        """List all counters in a configuration file"""
        full_file_path = self.get_full_file_path(file_name)
        data = self.read_yaml(full_file_path)
        print("Counters in: {}".format(file_name))
        for counter in data:
            print(counter)

    def add_counters_to_a_file(self, file_name: str, counters: list) -> None:
        """Add counters to a config file"""
        full_file_path = self.get_full_file_path(file_name)
        data = self.read_yaml(full_file_path)
        if isinstance(data, list):
            for counter in counters:
                if counter not in data:
                    data.append(counter)
            self.write_yaml(data, full_file_path)
        else:
            list_ = []
            for counter in counters:
                if counter not in list_:
                    list_.append(counter)
            self.write_yaml(list_, full_file_path)

    def remove_counters_from_file(self, file_name: str, counters: list) -> None:
        """Remove counters from a configuragtion file"""
        full_file_path = self.get_full_file_path(file_name)
        data = self.read_yaml(full_file_path)
        for counter in counters:
            if counter in data:
                data.remove(counter)
        self.write_yaml(data, full_file_path)

    def set_main_counter(self, counter: str) -> None:
        """
        Sets de main counter that will be used in the scans. This will set the counter
        thats going to be shown in the main tab in the DAF live view (daf.live)
        """
        self.experiment_file_dict["main_scan_counter"] = counter
        self.write_flag = True

    def delete_configuration_file(self, file_name: str):
        """Delete a configuration file configuration. Sometimes it wont be possible to delete a sys conf file"""
        full_file_path = self.get_full_file_path(file_name)
        os.remove(full_file_path)

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        if self.parsed_args_dict["set_default"]:
            self.set_default_counters(self.parsed_args_dict["set_default"])

        if self.parsed_args_dict["new"]:
            self.create_new_configuration_file(self.parsed_args_dict["new"])

        if self.parsed_args_dict["add_counter"]:
            self.add_counters_to_a_file(
                self.parsed_args_dict["add_counter"][0],
                self.parsed_args_dict["add_counter"][1:],
            )

        if self.parsed_args_dict["remove_counter"]:
            self.remove_counters_from_file(
                self.parsed_args_dict["remove_counter"][0],
                self.parsed_args_dict["remove_counter"][1:],
            )

        if self.parsed_args_dict["main_counter"]:
            self.set_main_counter(self.parsed_args_dict["main_counter"])

        if self.parsed_args_dict["remove"]:
            for file in self.parsed_args_dict["remove"]:
                self.delete_configuration_file(file)

        if self.parsed_args_dict["list"]:
            self.list_configuration_files()

        if self.parsed_args_dict["list_all_counters"]:
            self.list_all_counters()

        if isinstance(self.parsed_args_dict["list_counters"], list):
            for file in self.parsed_args_dict["list_counters"]:
                self.list_counter_in_a_configuration_file(file)

        if self.write_flag:
            self.write_to_experiment_file(self.experiment_file_dict)


@daf_log
def main() -> None:
    obj = ManageCounters()
    obj.run_cmd()


if __name__ == "__main__":
    main()
