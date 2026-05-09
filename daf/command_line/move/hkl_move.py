#!/usr/bin/env python3

from daf.utils.decorators import cli_decorator
from daf.core.hkl_move import HKLMove as CoreHKLMove
from daf.command_line.move.move_utils import MoveBase, _add_hkl_display_args


class HKLMove(MoveBase):
    DESC = """Move in the reciprocal space by giving a HKL"""
    EPI = """
    Eg:
        daf.mv 1 1 1
        daf.mv 1 0 0 -q
        daf.mv 1 1 1 -m '*' -cm 'I' -s 16

        """

    # Maximum acceptable error for HKL calculation success
    _MAX_ERROR_THRESHOLD = 1e-4

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
            help="H, K, L position to be moved",
        )
        _add_hkl_display_args(self.parser)

        args = self.parser.parse_args()
        return args

    def write_angles_if_small_error(self, error: float) -> None:
        """Writes to .Experiment file if the minimization was successful"""
        if float(error) > CoreHKLMove()._max_error:
            print("Can't find the HKL {}".format(self.parsed_args.hkl_position))
            return
        exp_dict = self.exp.solution().to_angle_dict()
        self.update_experiment_file(exp_dict)
        self.write_to_experiment_file(exp_dict, is_motor_set_point=True)

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        hkl_move = CoreHKLMove(file_store=self.io, max_error=self._MAX_ERROR_THRESHOLD)
        result = hkl_move.calculate(
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
        self.write_angles_if_small_error(result.hkl_error)


@cli_decorator
def main() -> None:
    obj = HKLMove()
    obj.run_cmd()


if __name__ == "__main__":
    main()
