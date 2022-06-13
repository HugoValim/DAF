#!/usr/bin/env python3


import argparse as ap
import numpy as np

from daf.utils.print_utils import format_5_decimals
from daf.utils.log import daf_log
from daf.utils import dafutilities as du
from daf.command_line.move.utils import MoveBase


class HKLMove(MoveBase):
    DESC  = """Move in the reciprocal space by giving a HKL"""
    EPI = '''
    Eg:
        daf.mv 1 1 1
        daf.mv 1 0 0 -q
        '''

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)
        self.exp = self.build_exp()

    def parse_command_line(self):
        super().parse_command_line()
        self.parser.add_argument('hkl-position', metavar='H K L', type=float, nargs=3, help='Move to a desired HKL')
        self.parser.add_argument('-q', '--quiet', action='store_true', help='Do not show the full output')

        args = self.parser.parse_args()
        return args


    def write_angles_if_small_error(self, error: float) -> None:
        """Writes to .Experiment file if the minimization was successful"""
        if float(error) > 1e-4:
            print('Can\'t find the HKL {}'.format(args.Move))
            return

        angs = self.exp.export_angles()
        exp_dict = {'Mu':angs[0], 'Eta':angs[1], 'Chi':angs[2], 'Phi':angs[3], 'Nu':angs[4], 'Del':angs[5], 'tt':angs[6],
            'theta':angs[7], 'alpha':angs[8], 'qaz':angs[9], 'naz':angs[10], 'tau':angs[11], 'psi':angs[12], 'beta':angs[13], 'omega':angs[14], 'hklnow':angs[15]}

        for j,k in exp_dict.items():
            if j in self.experiment_file_dict:
                if isinstance(k, np.ndarray):
                    self.experiment_file_dict[j] = k.tolist()
                else:
                    self.experiment_file_dict[j] = float(k)
        du.write(self.experiment_file_dict)

    def run_cmd(self, arguments):
        """Method to be defined be each subclass, this is the method 
        that should be run when calling the cli interface"""
        error = self.calculate_hkl(arguments['hkl-position'])
        if not arguments["quiet"]:
            self.exp.set_print_options(marker = '', column_marker='', space=14)
            print(self.exp)
        self.write_angles_if_small_error(error)
            
@daf_log
def main() -> None:
    obj = HKLMove()
    obj.run_cmd(obj.parsed_args_dict)



if __name__ == "__main__":
    main()
 




