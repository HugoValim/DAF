#!/usr/bin/env python3

from daf.utils.log import daf_log
from daf.command_line.experiment.experiment_utils import ExperimentBase


class ModeConstraints(ExperimentBase):
    DESC = """Function to constrain angles during the experiment"""
    EPI = """
        Eg:
            daf.cons --cons_Del 30 --cons_naz 15
            daf.amv -d 30 -cnaz 15
            """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-m",
            "--cons_Mu",
            metavar="ang",
            type=float,
            help="Constrain Mu, default: 0",
        )
        self.parser.add_argument(
            "-e",
            "--cons_Eta",
            metavar="ang",
            type=float,
            help="Constrain Eta, default: 0",
        )
        self.parser.add_argument(
            "-c",
            "--cons_Chi",
            metavar="ang",
            type=float,
            help="Constrain Chi, default: 0",
        )
        self.parser.add_argument(
            "-p",
            "--cons_Phi",
            metavar="ang",
            type=float,
            help="Constrain Phi, default: 0",
        )
        self.parser.add_argument(
            "-n",
            "--cons_Nu",
            metavar="ang",
            type=float,
            help="Constrain Nu, default: 0",
        )
        self.parser.add_argument(
            "-d",
            "--cons_Del",
            metavar="ang",
            type=float,
            help="Constrain Del, default: 0",
        )
        self.parser.add_argument(
            "-a",
            "--cons_alpha",
            metavar="ang",
            type=float,
            help="Constrain alpha, default: 0",
        )
        self.parser.add_argument(
            "-b",
            "--cons_beta",
            metavar="ang",
            type=float,
            help="Constrain beta, default: 0",
        )
        self.parser.add_argument(
            "-psi",
            "--cons_psi",
            metavar="ang",
            type=float,
            help="Constrain psi, default: 0",
        )
        self.parser.add_argument(
            "-o",
            "--cons_omega",
            metavar="ang",
            type=float,
            help="Constrain omega, default: 0",
        )
        self.parser.add_argument(
            "-q",
            "--cons_qaz",
            metavar="ang",
            type=float,
            help="Constrain qaz, default: 0",
        )
        self.parser.add_argument(
            "-cnaz",
            "--cons_naz",
            metavar="ang",
            type=float,
            help="Constrain naz, default: 0",
        )
        self.parser.add_argument(
            "-r",
            "--Reset",
            action="store_true",
            help="Reset all contrained angles to default (0)",
        )
        self.parser.add_argument(
            "-l", "--List", action="store_true", help="List constrained angles"
        )
        args = self.parser.parse_args()
        return args

    def reset_to_constraints_zero(self) -> None:
        """Reset all constraints to 0 (the default value), it writes directly to the .Experiment file"""
        dict_to_reset = {
            "cons_Mu": 0,
            "cons_Eta": 0,
            "cons_Chi": 0,
            "cons_Phi": 0,
            "cons_Nu": 0,
            "cons_Del": 0,
            "cons_alpha": 0,
            "cons_beta": 0,
            "cons_psi": 0,
            "cons_omega": 0,
            "cons_qaz": 0,
            "cons_naz": 0,
        }
        self.write_to_experiment_file(dict_to_reset)

    def list_contraints(self) -> None:
        """Method to print the current constraints"""
        print("")
        print("Alpha =    {}".format(self.experiment_file_dict["cons_alpha"]))
        print("Beta  =    {}".format(self.experiment_file_dict["cons_beta"]))
        print("Psi   =    {}".format(self.experiment_file_dict["cons_psi"]))
        print("Qaz   =    {}".format(self.experiment_file_dict["cons_qaz"]))
        print("Naz   =    {}".format(self.experiment_file_dict["cons_naz"]))
        print("Omega =    {}".format(self.experiment_file_dict["cons_omega"]))
        print("")
        print("Mu    =    {}".format(self.experiment_file_dict["cons_Mu"]))
        print("Eta   =    {}".format(self.experiment_file_dict["cons_Eta"]))
        print("Chi   =    {}".format(self.experiment_file_dict["cons_Chi"]))
        print("Phi   =    {}".format(self.experiment_file_dict["cons_Phi"]))
        print("Nu    =    {}".format(self.experiment_file_dict["cons_Nu"]))
        print("Del   =    {}".format(self.experiment_file_dict["cons_Del"]))
        print("")

    def run_cmd(self, arguments: dict) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        self.write_to_experiment_file(arguments)
        if arguments["Reset"]:
            self.reset_to_constraints_zero()
        if arguments["List"]:
            self.list_contraints()


@daf_log
def main() -> None:
    obj = OperationMode()
    obj.run_cmd(obj.parsed_args_dict)


if __name__ == "__main__":
    main()
