#!/usr/bin/env python3


import argparse as ap

from daf.utils.print_utils import format_5_decimals
from daf.utils.decorators import cli_decorator
from daf.command_line.query.query_utils import QueryBase


class Where(QueryBase):
    """Class to show the current position, both in real and reciprocal space"""

    DESC = """Show current position in reciprocal space as well as all diffractometer's angles and pseudo-angles"""
    EPI = """
    Eg:
        daf.wh
            """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()

        args = self.parser.parse_args()
        return args

    def print_position(self) -> None:
        """Print information about angles, pseudo-angles and HKL position based on the current .Experiment file"""
        self.hkl_now = list(self.calculate_hkl_from_angles())
        self.pseudo_dict_to_update = self.get_pseudo_angles_from_motor_angles()
        print("")
        print(
            "HKL now =   ",
            format_5_decimals(self.hkl_now[0]),
            format_5_decimals(self.hkl_now[1]),
            format_5_decimals(self.hkl_now[2]),
        )
        print("")
        print(
            "Alpha   =    {}".format(
                format_5_decimals(self.pseudo_dict_to_update["alpha"])
            )
        )
        print(
            "Beta    =    {}".format(
                format_5_decimals(self.pseudo_dict_to_update["beta"])
            )
        )
        print(
            "Psi     =    {}".format(
                format_5_decimals(self.pseudo_dict_to_update["psi"])
            )
        )
        print(
            "Tau     =    {}".format(
                format_5_decimals(self.pseudo_dict_to_update["tau"])
            )
        )
        print(
            "Qaz     =    {}".format(
                format_5_decimals(self.pseudo_dict_to_update["qaz"])
            )
        )
        print(
            "Naz     =    {}".format(
                format_5_decimals(self.pseudo_dict_to_update["naz"])
            )
        )
        print(
            "Omega   =    {}".format(
                format_5_decimals(self.pseudo_dict_to_update["omega"])
            )
        )
        print("")
        print(
            "Del     =    {}".format(
                format_5_decimals(self.experiment_file_dict["motors"]["del"]["value"])
            )
        )
        print(
            "Eta     =    {}".format(
                format_5_decimals(self.experiment_file_dict["motors"]["eta"]["value"])
            )
        )
        print(
            "Chi     =    {}".format(
                format_5_decimals(self.experiment_file_dict["motors"]["chi"]["value"])
            )
        )
        print(
            "Phi     =    {}".format(
                format_5_decimals(self.experiment_file_dict["motors"]["phi"]["value"])
            )
        )
        print(
            "Nu      =    {}".format(
                format_5_decimals(self.experiment_file_dict["motors"]["nu"]["value"])
            )
        )
        print(
            "Mu      =    {}".format(
                format_5_decimals(self.experiment_file_dict["motors"]["mu"]["value"])
            )
        )
        print("")

    def update_pseudo_angles_and_hkl(self):
        """Write calculated pseudo-angles and HKL to disk"""
        float_hkl = [float(i) for i in self.hkl_now]
        self.pseudo_dict_to_update["hklnow"] = float_hkl
        self.update_experiment_file(self.pseudo_dict_to_update)
        self.write_to_experiment_file(self.experiment_file_dict)

    def run_cmd(self) -> None:
        self.print_position()
        self.update_pseudo_angles_and_hkl()


@cli_decorator
def main() -> None:
    obj = Where()
    obj.run_cmd()


if __name__ == "__main__":
    main()
