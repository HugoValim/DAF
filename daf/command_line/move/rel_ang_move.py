#!/usr/bin/env python3

from daf.utils.decorators import cli_decorator
from daf.command_line.move.move_utils import MoveBase


class RelAngleMove(MoveBase):
    DESC = """Move the diffractometer by direct change in the angles with relative movement"""

    EPI = """
    Eg:
        daf.ramv --del 30 --eta 15
        daf.ramv -d 30 -e 15
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()
        self.motor_inputs()
        args = self.parser.parse_args()
        return args

    def write_angles(self) -> dict:
        """Write the angles in a relative way"""
        motor_position_dict = {}
        for motor in self.parsed_args_dict.keys():
            if self.parsed_args_dict[motor] is not None:
                motor_position_dict[motor] = float(
                    self.experiment_file_dict["motors"][motor]["value"]
                    + float(self.parsed_args_dict[motor])
                )
        return motor_position_dict

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        motor_dict = self.write_angles()
        self.write_to_experiment_file(motor_dict, is_motor_set_point=True, write=False)
        pseudo_dict = self.get_pseudo_angles_from_motor_angles()
        self.update_experiment_file(pseudo_dict)
        self.write_to_experiment_file(motor_dict, is_motor_set_point=True)


@cli_decorator
def main() -> None:
    obj = RelAngleMove()
    obj.run_cmd()


if __name__ == "__main__":
    main()
