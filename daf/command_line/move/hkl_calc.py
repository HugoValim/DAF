#!/usr/bin/env python3

from daf.utils.decorators import cli_decorator
from daf.core.hkl_move import HKLMove as CoreHKLMove
from daf.command_line.move.move_utils import MoveBase, _add_hkl_display_args


class HKLCalc(MoveBase):
    DESC = (
        """Calculate the diffractometer angles needed to reach a given HKL position"""
    )
    EPI = """
    Eg:
        daf.ca 1 1 1
        daf.ca 1 0 0 -q
        daf.ca 1 1 1 -m '*' -cm 'I' -s 16

        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "hkl-position",
            metavar="H K L",
            type=float,
            nargs=3,
            help="H, K, L position to be calculated",
        )
        _add_hkl_display_args(self.parser)

        args = self.parser.parse_args()
        return args

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        self.sync_live_experiment_file()
        result = CoreHKLMove(file_store=self.io).calculate(
            self.experiment_file_dict, self.parsed_args_dict["hkl-position"]
        )
        self.exp = result.engine
        if not self.parsed_args_dict["quiet"]:
            self.exp.set_print_options(
                marker=self.parsed_args_dict["marker"],
                column_marker=self.parsed_args_dict["column_marker"],
                space=self.parsed_args_dict["size"],
            )
            print(self.exp)


@cli_decorator
def main() -> None:
    obj = HKLCalc()
    obj.run_cmd()


if __name__ == "__main__":
    main()
