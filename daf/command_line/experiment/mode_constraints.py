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

    def reset_to_constraints_zero(self) -> None:
        """Reset all constraints to 0 (the default value), it writes directly to the .Experiment file"""
        dict_to_reset = {
            "cons_mu": 0,
            "cons_eta": 0,
            "cons_chi": 0,
            "cons_phi": 0,
            "cons_nu": 0,
            "cons_del": 0,
            "cons_alpha": 0,
            "cons_beta": 0,
            "cons_psi": 0,
            "cons_omega": 0,
            "cons_qaz": 0,
            "cons_naz": 0,
        }
        for key in dict_to_reset:
            self.experiment_file_dict[key] = dict_to_reset[key]

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
        print("Mu    =    {}".format(self.experiment_file_dict["cons_mu"]))
        print("Eta   =    {}".format(self.experiment_file_dict["cons_eta"]))
        print("Chi   =    {}".format(self.experiment_file_dict["cons_chi"]))
        print("Phi   =    {}".format(self.experiment_file_dict["cons_phi"]))
        print("Nu    =    {}".format(self.experiment_file_dict["cons_nu"]))
        print("Del   =    {}".format(self.experiment_file_dict["cons_del"]))
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


@daf_log
def main() -> None:
    obj = ModeConstraints()
    obj.run_cmd()


if __name__ == "__main__":
    main()
