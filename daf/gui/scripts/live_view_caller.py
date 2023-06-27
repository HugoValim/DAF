#!/usr/bin/env python3

import subprocess
from os import path

from daf.utils.decorators import cli_decorator
from daf.utils.generate_daf_default import default
from daf.utils.dafutilities import DAFIO


@cli_decorator
def main() -> None:
    data = DAFIO.only_read()
    kafka_topic = data["kafka_topic"]
    print(kafka_topic)
    proc = subprocess.Popen(
        "kbl {}".format(kafka_topic),
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        # stdin=subprocess.PIPE,
        shell=True,
    )
    return proc


if __name__ == "__main__":
    main()
