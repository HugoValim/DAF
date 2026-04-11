#!/usr/bin/env python3

from daf.utils.decorators import cli_decorator
from daf.command_line.scan.daf_scan_utils import ScanBase

_ABSOLUTE, _RELATIVE = "absolute", "relative"

_SCAN_DOCS = {
    1: {
        _ABSOLUTE: (
            "Perform an absolute scan in one of the diffractometer motors",
            "Eg:\n    daf.ascan -m 1 10 100 .1\n    daf.ascan --mu 1 10 100 .1 -o my_scan\n    ",
        ),
        _RELATIVE: (
            "Perform a relative scan in one of the diffractometer motors",
            "Eg:\n    daf.lup -m -2 2 100 .1\n    daf.dscan -m -2 2 100 .1\n    daf.dscan -m -2 2 100 .1 -np -o my_file\n    ",
        ),
    },
    2: {
        _ABSOLUTE: (
            "Perform an absolute scan in two diffractometer motors",
            "Eg:\n    daf.a2scan -d 1 10 -e 1 20 100 .1\n    ",
        ),
        _RELATIVE: (
            "Perform a relative scan in two diffractometer motors",
            "Eg:\n    daf.d2scan -m -2 2 -e -4 4 100 .1\n    ",
        ),
    },
    3: {
        _ABSOLUTE: (
            "Perform an absolute scan in three diffractometer motors",
            "Eg:\n    daf.a3scan -d 1 10 -e 1 20 -c 5 20 100 .1\n    ",
        ),
        _RELATIVE: (
            "Perform a relative scan in three diffractometer motors",
            "Eg:\n    daf.d3scan -m -2 2 -e -4 4 -c -2 2 100 .1\n    ",
        ),
    },
    4: {
        _ABSOLUTE: (
            "Perform an absolute scan in four diffractometer motors",
            "Eg:\n    daf.a4scan -d 1 10 -e 1 20 -c 5 20 -p 30 40 100 .1\n    ",
        ),
        _RELATIVE: (
            "Perform a relative scan in four diffractometer motors",
            "Eg:\n    daf.d4scan -m -2 2 -e -4 4 -c -2 2 -p -5 5 100 .1\n    ",
        ),
    },
    5: {
        _ABSOLUTE: (
            "Perform an absolute scan in five diffractometer motors",
            "Eg:\n    daf.a5scan -d 1 10 -e 1 20 -c 5 20 -p 30 40 -n -10 10 100 .1\n    ",
        ),
        _RELATIVE: (
            "Perform a relative scan in five diffractometer motors",
            "Eg:\n    daf.d5scan -m -2 2 -e -4 4 -c -2 2 -p -5 5 -n -3 3 100 .1\n    ",
        ),
    },
    6: {
        _ABSOLUTE: (
            "Perform an absolute scan in all six diffractometer motors",
            "Eg:\n    daf.a6scan -d 1 10 -e 1 20 -c 5 20 -p 30 40 -n -10 10 -m 35 46 100 .1\n    ",
        ),
        _RELATIVE: (
            "Perform a relative scan in all six diffractometer motors",
            "Eg:\n    daf.d6scan -m -2 2 -e -4 4 -c -2 2 -p -5 5 -n -3 3 -d -4 4 100 .1\n    ",
        ),
    },
}


def _build_scan_class(n: int, scan_type: str):
    """Factory: build an (A|D)Scan{N} class and its cli main function."""
    desc, epi = _SCAN_DOCS[n][scan_type]
    label = "A" if scan_type == _ABSOLUTE else "D"
    class_name = f"{label}Scan{n}"

    def __init__(self_):
        ScanBase.__init__(self_, number_of_motors=n, scan_type=scan_type)

    def run_cmd(self_):
        self_.run_scan()

    cls = type(
        class_name,
        (ScanBase,),
        {"DESC": desc, "EPI": epi, "__init__": __init__, "run_cmd": run_cmd},
    )

    main_name = f"{label.lower()}scan{n}_main"

    @cli_decorator
    def main() -> None:
        obj = cls()
        obj.run_cmd()

    return cls, main, main_name


# Generate all classes and entry-points in one pass
_exported: dict = {}
for n in range(1, 7):
    for scan_type in (_ABSOLUTE, _RELATIVE):
        cls, main, main_name = _build_scan_class(n, scan_type)
        _exported[cls.__name__] = cls
        _exported[main_name] = main
        globals()[cls.__name__] = cls
        globals()[main_name] = main

del _exported, _ABSOLUTE, _RELATIVE
