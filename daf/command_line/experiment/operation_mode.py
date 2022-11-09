#!/usr/bin/env python3

from daf.utils.log import daf_log
from daf.command_line.experiment.experiment_utils import ExperimentBase


class OperationMode(ExperimentBase):
    DESC = """
                 >detector<  >Reference<     >Sample<     >Sample<     >Sample<
                    g_mode1      g_mode2      g_mode3      g_mode4      g_mode5
            0             .            .  omega-fixed            X            X  0
            1   Delta-fixed   Alpha=Beta    Eta-fixed    Eta-fixed    Eta-fixed  1
            2      Nu-fixed  Alpha-fixed     Mu-fixed     Mu-fixed     Mu-fixed  2
            3     Qaz-fixed   Beta-fixed    Chi-fixed    Chi-fixed    Chi-fixed  3
            4     Naz-fixed    Psi-fixed    Phi-fixed    Phi-fixed    Phi-fixed  4
            5         Zone*            X    Eta=Del/2            X            X  5
            6       Energy*            X      Mu=Nu/2            X            X  6

            *not implemented
            """

    EPI = """
        Eg:
            daf.mode 215, this will set Nu fix, Alpha=Beta, Eta=Del/2
            See daf.cons to set constraints
          """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument(
            "Mode",
            type=str,
            help="sets the operation mode of the diffractometer, following the same modes as used in Spec, the mode should be passed without spaces",
        )
        args = self.parser.parse_args()
        return args

    def run_cmd(self) -> None:
        """Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface"""
        self.update_experiment_file(self.parsed_args_dict, is_str=True)
        self.write_to_experiment_file(self.experiment_file_dict)


@daf_log
def main() -> None:
    obj = OperationMode()
    obj.run_cmd()


if __name__ == "__main__":
    main()
