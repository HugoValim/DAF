#!/usr/bin/env python3
"""Consolidated angular scan command replacing AScan1..6 and DScan1..6.

A single ``daf.ascan`` entry-point that accepts ``--type`` and ``--n-motors``
flags to replace the 12 generated scan entry-points (daf.ascan..daf.a6scan,
daf.dscan/daf.lup..daf.d6scan).

Usage examples::

    daf.ascan --type absolute --n-motors 1 -m 0 10 100 0.1
    daf.ascan --type relative --n-motors 2 -m -5 5 -e -10 10 100 0.1
    daf.ascan --type absolute --n-motors 3 -m 0 10 -e 0 20 -c 0 30 100 0.1
"""

import argparse
from typing import Optional

from daf.command_line.cli_base_utils import CLIBase
from daf.command_line.scan.daf_scan_utils import ScanBase
from daf.utils.decorators import cli_decorator

_ABSOLUTE = "absolute"
_RELATIVE = "relative"
_VALID_SCAN_TYPES = (_ABSOLUTE, _RELATIVE)
_MIN_MOTORS = 1
_MAX_MOTORS = 6


class _MotorCountAction(argparse.Action):
    """Custom argparse action that validates n-motors is in [1, 6]."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: int,
        option_string: Optional[str] = None,
    ) -> None:
        if not (_MIN_MOTORS <= values <= _MAX_MOTORS):
            parser.error(
                f"--n-motors must be between {_MIN_MOTORS} and {_MAX_MOTORS}, got {values}"
            )
        setattr(namespace, self.dest, values)


class AngularScan(ScanBase):
    """Consolidated angle scan supporting 1-6 motors and absolute/relative modes."""

    DESC = (
        "Perform an absolute or relative angle scan in 1 to 6 diffractometer motors. "
        "Use --type to choose absolute or relative mode and --n-motors to set motor count."
    )
    EPI = (
        "Examples:\n"
        "    daf.ascan --type absolute --n-motors 1 -m 0 10 100 0.1\n"
        "    daf.ascan --type relative --n-motors 2 -m -5 5 -e -10 10 100 0.1\n"
        "    daf.ascan --type absolute --n-motors 3 -m 0 10 -e 0 20 -c 0 30 100 0.1\n"
    )

    def __init__(self) -> None:
        # Pre-parse --type and --n-motors before full ScanBase init so that
        # number_of_motors and scan_type are available when ScanBase calls
        # parse_command_line().
        scan_type, number_of_motors = self._pre_parse_type_and_n_motors()
        super().__init__(number_of_motors=number_of_motors, scan_type=scan_type)

    # ------------------------------------------------------------------
    # Pre-parse helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pre_parse_type_and_n_motors() -> tuple[str, int]:
        """Minimally pre-parse --type and --n-motors from sys.argv.

        Returns:
            A (scan_type, number_of_motors) tuple suitable for ScanBase.
        """
        pre_parser = argparse.ArgumentParser(add_help=False)
        pre_parser.add_argument("--type", dest="type", default=_ABSOLUTE)
        pre_parser.add_argument("--n-motors", dest="n_motors", type=int, default=1)
        known, _ = pre_parser.parse_known_args()
        return known.type, known.n_motors

    # ------------------------------------------------------------------
    # Public helpers (also used in tests via direct instantiation)
    # ------------------------------------------------------------------

    def _add_type_and_n_motors_args(self) -> None:
        """Add --type and --n-motors to self.parser."""
        self.parser.add_argument(
            "--type",
            dest="type",
            choices=list(_VALID_SCAN_TYPES),
            default=_ABSOLUTE,
            metavar="TYPE",
            help=f"Scan mode: {_ABSOLUTE!r} or {_RELATIVE!r} (default: {_ABSOLUTE!r})",
        )
        self.parser.add_argument(
            "--n-motors",
            dest="n_motors",
            type=int,
            action=_MotorCountAction,
            default=1,
            metavar="N",
            help=f"Number of motors to scan ({_MIN_MOTORS}-{_MAX_MOTORS}, default: 1)",
        )

    # ------------------------------------------------------------------
    # ScanBase overrides
    # ------------------------------------------------------------------

    def parse_command_line(self) -> argparse.Namespace:
        """Build the argument parser for the unified angular scan command."""
        CLIBase.parse_command_line(self)
        self._add_type_and_n_motors_args()
        for motor, motor_cfg in self.experiment_file_dict["motors"].items():
            self.parser.add_argument(
                "-" + motor_cfg["cli_abbrev"],
                "--" + motor,
                metavar=("start", "end"),
                type=float,
                nargs=2,
                help=f"Start and end positions for {motor}",
            )
        self.common_cli_scan_arguments()
        return self.parser.parse_args()

    def run_cmd(self) -> None:
        """Execute the angular scan."""
        self.run_scan()


@cli_decorator
def main() -> None:
    """Entry-point for the ``daf.ascan`` console script."""
    obj = AngularScan()
    obj.run_cmd()


if __name__ == "__main__":
    main()
