#!/usr/bin/env python3

from daf.utils.decorators import cli_decorator
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
        self.write_flag = False

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "-m",
            "--cons_mu",
            metavar="ang",
            type=float,
            help="constrain Mu, default: 0",
        )
        self.parser.add_argument(
            "-e",
            "--cons_eta",
            metavar="ang",
            type=float,
            help="constrain Eta, default: 0",
        )
        self.parser.add_argument(
            "-c",
            "--cons_chi",
            metavar="ang",
            type=float,
            help="constrain Chi, default: 0",
        )
        self.parser.add_argument(
            "-p",
            "--cons_phi",
            metavar="ang",
            type=float,
            help="constrain Phi, default: 0",
        )
        self.parser.add_argument(
            "-n",
            "--cons_nu",
            metavar="ang",
            type=float,
            help="constrain Nu, default: 0",
        )
        self.parser.add_argument(
            "-d",
            "--cons_del",
            metavar="ang",
            type=float,
            help="constrain Del, default: 0",
        )
        self.parser.add_argument(
            "-a",
            "--cons_alpha",
            metavar="ang",
            type=float,
            help="constrain alpha, default: 0",
        )
        self.parser.add_argument(
            "-b",
            "--cons_beta",
            metavar="ang",
            type=float,
            help="constrain beta, default: 0",
        )
        self.parser.add_argument(
            "-psi",
            "--cons_psi",
            metavar="ang",
            type=float,
            help="constrain psi, default: 0",
        )
        self.parser.add_argument(
            "-o",
            "--cons_omega",
            metavar="ang",
            type=float,
            help="constrain omega, default: 0",
        )
        self.parser.add_argument(
            "-q",
            "--cons_qaz",
            metavar="ang",
            type=float,
            help="constrain qaz, default: 0",
        )
        self.parser.add_argument(
            "-naz",
            "--cons_naz",
            metavar="ang",
            type=float,
            help="constrain naz, default: 0",
        )
        self.parser.add_argument(
            "-r",
            "--reset",
            action="store_true",
            help="reset all contrained angles to default (0)",
        )
        self.parser.add_argument(
            "-l", "--list", action="store_true", help="list constrained angles"
        )
        args = self.parser.parse_args()
        return args

    _PSEUDO_CONS = ("alpha", "beta", "psi", "qaz", "naz", "omega")
    _MOTOR_CONS = ("mu", "eta", "chi", "phi", "nu", "del")

    def reset_to_constraints_zero(self) -> None:
        """Reset all constraints to 0 (the default value), it writes directly to the .Experiment file"""
        for motor in self._MOTOR_CONS:
            self.experiment_file_dict[f"cons_{motor}"] = 0
        for pseudo in self._PSEUDO_CONS:
            self.experiment_file_dict[f"cons_{pseudo}"] = 0

    def list_contraints(self) -> None:
        """Method to print the current constraints"""
        print("")
        for pseudo in self._PSEUDO_CONS:
            val = self.experiment_file_dict[f"cons_{pseudo}"]
            print(f"{pseudo.capitalize():5} =    {val}")
        print("")
        for motor in self._MOTOR_CONS:
            val = self.experiment_file_dict[f"cons_{motor}"]
            print(f"{motor.capitalize():4} =    {val}")
        print("")

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        if self.parsed_args_dict["reset"]:
            self.reset_to_constraints_zero()
        self.update_experiment_file(self.parsed_args_dict)
        if self.parsed_args_dict["list"]:
            self.list_contraints()
        self.write_to_experiment_file(self.parsed_args_dict)


@cli_decorator
def main() -> None:
    obj = ModeConstraints()
    obj.run_cmd()


if __name__ == "__main__":
    main()
