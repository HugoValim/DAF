#!/usr/bin/env python3

import argparse as ap
import numpy as np

from daf.utils.log import daf_log
from daf.command_line.scan.daf_scan_utils import ScanBase


class D4Scan(ScanBase):

    DESC = """Perform a relative scan in four of the diffractometer motors"""
    EPI = """
    Eg: 
        daf.d4scan -m -2 2 -e -4 4 -c -2 2 -p -5 5 100 .1
        daf.d4scan -m -2 2 -e -4 4 -c -2 2 -p -5 5 100 .1 -np -o my_file

        """


    def __init__(self):
        super().__init__(number_of_motors=4, scan_type="relative")

    def run_cmd(self, arguments):
        """
        Method to be defined be each subclass, this is the method
        that should be run when calling the cli interface
        """
        self.run_scan()


@daf_log
def main() -> None:
    obj = D4Scan()
    obj.run_cmd(obj.parsed_args)


if __name__ == "__main__":
    main()
