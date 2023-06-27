#!/usr/bin/env python3

from daf.utils.decorators import cli_decorator
from daf.command_line.scan.daf_scan_utils import ScanBase


class A1Scan(ScanBase):

    DESC = """Perform an absolute scan in one of the diffractometer motors"""
    EPI = """
    Eg:
        daf.ascan -m 1 10 100 .1
        daf.ascan --mu 1 10 100 .1 -o my_scan

        """

    def __init__(self):
        super().__init__(number_of_motors=1, scan_type="absolute")

    def run_cmd(self):
        """Method to print the user required information"""
        self.run_scan()


@cli_decorator
def main() -> None:
    obj = A1Scan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
