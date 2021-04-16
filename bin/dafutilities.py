#!/usr/bin/env python3
"""Library for reading and writing experiment files"""

import yaml

DEFAULT = '.Experiment'

def read(filepath=DEFAULT):
    with open(filepath) as file:
        return yaml.safe_load(file)

def write(data, filepath=DEFAULT):
    with open(filepath, 'w') as file:
        yaml.dump(data, file)
