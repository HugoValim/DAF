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
       daf.setup -s new_setup
       daf.setup -s
       daf.setup -r my_setup1 my_setup2 my_setup3
        """

    def __init__(self):
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
            metavar="[file]",
            type=str,
            help="Change current setup to another",
        )
        self.parser.add_argument(
            "-s",
            "--save",
            metavar="file",
            nargs="?",
            const="no_args",
            help="Save the current setup, if only -s is passed them de command will overwrite de current setup",
        )
        self.parser.add_argument("-r", "--remove", metavar="file", nargs="*", help="Remove a setup")
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
            help="Add a description to this setup",
        )
        self.parser.add_argument(
            "-i",
            "--info",
            metavar="setup",
            type=str,
            help="Print detailed information about a specific setup",
        )


        args = self.parser.parse_args()
        return args

    @staticmethod
    def create_new_setup(setup_name):
        """Create a new DAF setup"""
        gdd.generate_file(file_name=setup_name, file_path=dp.DAF_CONFIGS)

    def checkout_setup(self, setup_name):
        """Change to a new DAF setup"""
        full_file_path = os.path.join(dp.DAF_CONFIGS, setup_name)
        os.system(
            "cat {} > {}".format(full_file_path, du.DEFAULT)
        )
        self.experiment_file_dict = du.read()
        self.experiment_file_dict["setup"] = setup_name
        self.write_flag = True

    @staticmethod
    def list_all_setups():
        """List all the setups that a user has"""
        setup_now = self.experiment_file_dict["setup"]
        os.system(
            "ls -A1 --ignore=*.py $HOME/.daf/ | sed 's/^/   /' | sed '/   {}$/c >  {}' ".format(
                setup_now, setup_now
            )
        )


    @staticmethod
    def write_yaml(dict_, file_path=None) -> None:
        """Method to write to a yaml file"""
        with open(file_path, "w") as file:
            yaml.dump(dict_, file)

    def run_cmd(self, arguments: dict) -> None:
        if arguments["new"]:
            self.create_new_setup(arguments["new"])
        if arguments["checkout"]:
            self.checkout_setup(arguments["checkout"])
        if arguments["list"]:
            self.list_all_setups()       
        if self.write_flag:
            du.write(self.experiment_file_dict)



@daf_log
def main() -> None:
    obj = Setup()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()


# if args.save:
#     dict_args = du.read()
#     setup_now = dict_args["setup"]
#     if args.save == "no_args":
#         os.system('cp .Experiment "$HOME/.daf/{}"'.format(setup_now))
#     else:
#         os.system('cp .Experiment "$HOME/.daf/{}"'.format(args.save))

# if args.remove:
#     dict_args = du.read()
#     setup_now = dict_args["setup"]
#     for i in args.remove:
#         if setup_now != i:
#             os.system('rm -f "$HOME/.daf/{}"'.format(i))
#         else:
#             print("")
#             print("Leave the setup before removing it")
#             print("")

# if args.description:
#     if args.description[0] != ".":
#         dict_args = du.read(filepath=du.HOME + "/.daf/" + args.description[0])
#         dict_args["setup_desc"] = args.description[1]
#         du.write(dict_args, filepath=du.HOME + "/.daf/" + args.description[0])
#     else:
#         dict_args = du.read()
#         dict_args["setup_desc"] = args.description
#         du.write(dict_args)


# if args.info:
#     dict_args = du.read()
#     if dict_args["setup"] == args.info:
#         desc = dict_args["setup_desc"]
#         print(desc)
#     else:
#         dict_args = du.read(filepath=du.HOME + "/.daf/" + args.info)
#         desc = dict_args["setup_desc"]
#         print(desc)
# du.log_macro(dict_args)
