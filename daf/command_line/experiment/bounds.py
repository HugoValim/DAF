#!/usr/bin/env python3

from daf.utils.log import daf_log
from daf.command_line.experiment.experiment_utils import ExperimentBase


class Bounds(ExperimentBase):
    DESC = """Sets the bounds of the diffractometer angles"""
    EPI = """
    Eg:
        daf.bounds -m -180 180 -n -180 180
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-m",
            "--bound_Mu",
            metavar=("min", "max"),
            type=float,
            nargs=2,
            help="Sets Mu bounds",
        )
        self.parser.add_argument(
            "-e",
            "--bound_Eta",
            metavar=("min", "max"),
            type=float,
            nargs=2,
            help="Sets Eta bounds",
        )
        self.parser.add_argument(
            "-c",
            "--bound_Chi",
            metavar=("min", "max"),
            type=float,
            nargs=2,
            help="Sets Chi bounds",
        )
        self.parser.add_argument(
            "-p",
            "--bound_Phi",
            metavar=("min", "max"),
            type=float,
            nargs=2,
            help="Sets Phi bounds",
        )
        self.parser.add_argument(
            "-n",
            "--bound_Nu",
            metavar=("min", "max"),
            type=float,
            nargs=2,
            help="Sets Nu bounds",
        )
        self.parser.add_argument(
            "-d",
            "--bound_Del",
            metavar=("min", "max"),
            type=float,
            nargs=2,
            help="Sets Del bounds",
        )
        self.parser.add_argument(
            "-l", "--List", action="store_true", help="List the current bounds"
        )
        self.parser.add_argument(
            "-r", "--Reset", action="store_true", help="Reset all bounds to default"
        )

        args = self.parser.parse_args()
        return args

    def reset_bounds_to_default(self) -> None:
        """Reset all motor bounds to default. It writes directly to the .Experiment file"""
        default_bounds = {
            "bound_Mu": [-20.0, 160.0],
            "bound_Eta": [-20.0, 160.0],
            "bound_Chi": [-5.0, 95.0],
            "bound_Phi": [-400.0, 400.0],
            "bound_Nu": [-20.0, 160.0],
            "bound_Del": [-20.0, 160.0],
        }
        self.write_to_experiment_file(default_bounds)

    def list_bounds(self) -> None:
        """Method to print the current bounds"""
        print("")
        print("Mu    =    {}".format(dict_args["bound_Mu"]))
        print("Eta   =    {}".format(dict_args["bound_Eta"]))
        print("Chi   =    {}".format(dict_args["bound_Chi"]))
        print("Phi   =    {}".format(dict_args["bound_Phi"]))
        print("Nu    =    {}".format(dict_args["bound_Nu"]))
        print("Del   =    {}".format(dict_args["bound_Del"]))
        print("")

    def run_cmd(self, arguments: dict) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        self.write_to_experiment_file(arguments)
        if arguments["Reset"]:
            self.reset_bounds_to_default()
        if arguments["List"]:
            self.list_bounds()


@daf_log
def main() -> None:
    obj = Bounds()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
