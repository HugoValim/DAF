#!/usr/bin/env python3

import subprocess
from os import path

from daf.utils.log import daf_log


@daf_log
def main() -> None:
    path_to_bin = path.join(path.dirname(path.realpath(__file__)), "../live_view.py")
    proc = subprocess.Popen(
        "pydm --hide-nav-bar {}".format(path_to_bin),
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        # stdin=subprocess.PIPE,
        shell=True,
    )
    return proc


if __name__ == "__main__":
    main()
