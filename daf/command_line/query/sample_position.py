#!/usr/bin/env python3


import argparse as ap

from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.command_line.query.query_utils import QueryBase


class SamplePos(QueryBase):
    """Class to show the current position, both in real and reciprocal space"""

    DESC = """Show current position in reciprocal space as well as all diffractometer's angles and pseudo-angles"""
    EPI = """
    Eg:
        daf.spos
            """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self):
        super().parse_command_line()

        args = self.parser.parse_args()
        return args

    def print_position(self) -> None:
        """Print information about angles, pseudo-angles and HKL position based on the current .Experiment file"""
        print("")
        print(
            "sample_z     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["sample_z"]["value"]
                )
            )
        )
        print(
            "sample_x     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["sample_x"]["value"]
                )
            )
        )
        print(
            "sample_rx     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["sample_rx"]["value"]
                )
            )
        )
        print(
            "sample_y     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["sample_y"]["value"]
                )
            )
        )
        print(
            "sample_ry     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["sample_ry"]["value"]
                )
            )
        )
        print(
            "sample_x_s1      =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["sample_x_s1"]["value"]
                )
            )
        )
        print(
            "sample_y_s1      =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["sample_y_s1"]["value"]
                )
            )
        )
        print(
            "diffractomer_ux     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["diffractomer_ux"]["value"]
                )
            )
        )
        print(
            "diffractomer_uy     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["diffractomer_uy"]["value"]
                )
            )
        )
        print(
            "diffractomer_rx     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["diffractomer_rx"]["value"]
                )
            )
        )
        print(
            "theta_analyzer_crystal     =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["theta_analyzer_crystal"][
                        "value"
                    ]
                )
            )
        )
        print(
            "2theta_analyzer_crystal      =    {}".format(
                format_5_decimals(
                    self.experiment_file_dict["motors"]["2theta_analyzer_crystal"][
                        "value"
                    ]
                )
            )
        )
        print("")

    def run_cmd(self) -> None:
        self.print_position()


@daf_log
def main() -> None:
    obj = SamplePos()
    obj.run_cmd()


if __name__ == "__main__":
    main()
