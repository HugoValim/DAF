#!/usr/bin/env python3

from daf.utils.log import daf_log
from daf.command_line.scan.daf_scan_utils import ScanBase


class A3Scan(ScanBase):

    DESC = """Perform an absolute scan using three of the diffractometer motors"""
    EPI = """
    Eg:
        daf.a3scan -d 1 10 -e 1 20 -c 5 20 100 .1
        daf.a3scan -d 1 10 -e 1 20 -c 5 20 100 .1 -o my_scan -np
        """

    def __init__(self):
        super().__init__(number_of_motors=3, scan_type="absolute")

    def run_cmd(self):
        """Method to print the user required information"""
        self.run_scan()


@daf_log
def main() -> None:
    obj = A3Scan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
