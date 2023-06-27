#!/usr/bin/env python3

import argparse as ap
from os import path


from daf.command_line.support.support_utils import SupportBase
from daf.utils import dafutilities as du
from daf.utils.decorators import cli_decorator


class FetchPVs(SupportBase):
    DESC = """Fetch PVs so DAF become aware if they are offline or not"""
    EPI = """
    Eg:
       daf.fetch
        """

    def __init__(self):
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.io = du.DAFIO(read=False)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "-nr",
            "--no-reset",
            action="store_true",
            help="Fetch all PVS, but do not reset the file",
        )

        args = self.parser.parse_args()
        return args

    def get_offline_motors_and_write(self):
        """Get all motors that are offline and set their up bit so DAF become aware"""
        data = du.fetch_pvs_and_check_for_connection()
        self.io.write(data)

    def run_cmd(self) -> None:
        self.get_offline_motors_and_write()


@cli_decorator
def main() -> None:
    obj = FetchPVs()
    obj.run_cmd()


if __name__ == "__main__":
    main()
