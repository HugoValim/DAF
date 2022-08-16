#!/usr/bin/env python3

import argparse as ap
import sys
import os
from os import path
import yaml
import subprocess

from daf.command_line.support.support_utils import SupportBase
import daf.utils.generate_daf_default as gdd
import daf.utils.daf_paths as dp
import daf.utils.dafutilities as du
from daf.utils.log import daf_log


class Setup(SupportBase):

    DESC = """Create setups that helps user to save their previous configuration"""
    EPI = """
    Eg:
       daf.setup -c default
       daf.setup -sa new_setup
       daf.setup -s
       daf.setup -r my_setup1 my_setup2 my_setup3
       daf.setup -i .
       daf.setup -d 'my_awesome description'
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.write_flag = False

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "-n", "--new", metavar="setup name", type=str, help="Create a new setup"
        )
        self.parser.add_argument(
            "-c",
            "--checkout",
            metavar="setup",
            type=str,
            help="Change current setup to another",
        )
        self.parser.add_argument(
            "-s",
            "--save",
            action="store_true",
            help="Save the current setup",
        )
        self.parser.add_argument(
            "-sa",
            "--save-as",
            metavar="setup name",
            type=str,
            help="Save the current setup as a new setup",
        )
        self.parser.add_argument(
            "-r", "--remove", metavar="file", nargs="*", help="Remove a setup"
        )
        self.parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List all setups, showing in which one you are",
        )
        self.parser.add_argument(
            "-d",
            "--description",
            metavar="desc",
            nargs=2,
            help="Add a description to a setup, if the description should be add to this setup, you can use . to refer to it",
        )
        self.parser.add_argument(
            "-i",
            "--info",
            metavar="setup",
            type=str,
            help="Print detailed information about a specific setup, the current setup may be referred as .",
        )

        args = self.parser.parse_args()
        return args

    def get_current_setup(self) -> str:
        """Get the current setup written in the .Experiment file"""
        return self.experiment_file_dict["setup"]

    @staticmethod
    def create_new_setup(setup_name: str) -> None:
        """Create a new DAF setup"""
        gdd.generate_file(file_name=setup_name, file_path=dp.DAF_CONFIGS)

    def checkout_setup(self, setup_name: str) -> None:
        """Change to a new DAF setup"""
        full_file_path = os.path.join(dp.DAF_CONFIGS, setup_name)
        os.system("cat {} > {}".format(full_file_path, du.DEFAULT))
        self.experiment_file_dict = self.io.read()
        self.experiment_file_dict["setup"] = setup_name
        self.write_flag = True

    def list_all_setups(self) -> None:
        """List all the setups that a user has"""
        setup_now = self.get_current_setup()
        os.system(
            "ls -A1 --ignore=*.yml $HOME/.daf/ | sed 's/^/   /' | sed '/   {}$/c >  {}' ".format(
                setup_now, setup_now
            )
        )

    def save_setup(self) -> None:
        """Save the current setup"""
        setup_now = self.get_current_setup()
        gdd.generate_file(
            self.experiment_file_dict, file_path=dp.DAF_CONFIGS, file_name=setup_now
        )

    def save_as_setup(self, setup_name: str) -> None:
        """Save the current setup as a new setup"""
        gdd.generate_file(
            self.experiment_file_dict, file_path=dp.DAF_CONFIGS, file_name=setup_name
        )

    def remove_setup(self, setup_name: str) -> None:
        """Remove  a setup from users configuration"""
        setup_now = self.get_current_setup()
        if setup_now != setup_name:
            file_path_to_remove = os.path.join(dp.DAF_CONFIGS, setup_name)
            os.remove(file_path_to_remove)
        else:
            print("")
            print("Leave the setup {} before removing it".format(setup_name))
            print("")

    def update_setup_description(self, setup_name: str, description: str) -> None:
        """Update a description for one of the predefined setups"""
        setup_now = self.get_current_setup()
        if setup_name != "." and setup_name != setup_now:
            path_to_the_setup = os.path.join(dp.DAF_CONFIGS, setup_name)
            dict_args = self.io.read(filepath=path_to_the_setup)
            dict_args["setup_desc"] = description
            du.write(dict_args, filepath=path_to_the_setup)
        else:
            self.experiment_file_dict["setup_desc"] = description
            self.write_flag = True

    def print_setup_description(self, setup_name: str) -> None:
        """Print the requested setup description"""
        setup_now = self.get_current_setup()
        if setup_now == setup_name or setup_name == ".":
            desc = self.experiment_file_dict["setup_desc"]
            print(desc)
        else:
            path_to_the_setup = os.path.join(dp.DAF_CONFIGS, setup_name)
            dict_args = self.io.read(filepath=path_to_the_setup)
            desc = dict_args["setup_desc"]
            print(desc)

    def run_cmd(self) -> None:
        if self.parsed_args_dict["new"]:
            self.create_new_setup(self.parsed_args_dict["new"])
        if self.parsed_args_dict["checkout"]:
            self.checkout_setup(self.parsed_args_dict["checkout"])
        if self.parsed_args_dict["save"]:
            self.save_setup()
        if self.parsed_args_dict["save_as"]:
            self.save_as_setup(self.parsed_args_dict["save_as"])
        if self.parsed_args_dict["description"]:
            self.update_setup_description(
                self.parsed_args_dict["description"][0],
                self.parsed_args_dict["description"][1],
            )
        if self.parsed_args_dict["remove"]:
            for setup in self.parsed_args_dict["remove"]:
                self.remove_setup(setup)
        if self.parsed_args_dict["list"]:
            self.list_all_setups()
        if self.parsed_args_dict["info"]:
            self.print_setup_description(self.parsed_args_dict["info"])
        if self.write_flag:
            self.write_to_experiment_file(self.experiment_file_dict)


@daf_log
def main() -> None:
    obj = Setup()
    obj.run_cmd()


if __name__ == "__main__":
    main()
