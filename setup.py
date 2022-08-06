#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="daf_test",
    version="0.0.1",
    description="A Module to control x-ray diffraction experiments that uses a 6-circle diffractometer",
    long_description=readme(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    author="Hugo Campos",
    author_email="hugo.campos@lnls.br",
    url="https://github.com/lnls-sol/sol-view",
    install_requires=[
        "pandas",
    ],
    package_data={"daf.gui.ui": ["*.ui", "icons/*.svg"]},
    include_package_data=True,
    packages=find_packages(where=".", exclude=["test", "test.*", "tests"]),
    entry_points={
        "console_scripts": [
            "daf.bounds = daf.command_line.experiment.bounds:main",
            "daf.expt = daf.command_line.experiment.experiment_configuration:main",
            "daf.mc = daf.command_line.experiment.manage_counters:main",
            "daf.cons = daf.command_line.experiment.mode_constraints:main",
            "daf.mode = daf.command_line.experiment.operation_mode:main",
            "daf.ub = daf.command_line.experiment.set_u_ub_matrix:main",
            "daf.amv = daf.command_line.move.ang_move:main",
            "daf.ca = daf.command_line.move.hkl_calc:main",
            "daf.mv = daf.command_line.move.hkl_move:main",
            "daf.rmap = daf.command_line.move.reciprocal_space_map:main",
            "daf.ramv = daf.command_line.move.rel_ang_move:main",
            "daf.status = daf.command_line.query.status:main",
            "daf.wh = daf.command_line.query.where:main",
            "daf.ascan = daf.command_line.scan.a1scan:main",
            "daf.a2scan = daf.command_line.scan.a2scan:main",
            "daf.a3scan = daf.command_line.scan.a3scan:main",
            "daf.a4scan = daf.command_line.scan.a4scan:main",
            "daf.a5scan = daf.command_line.scan.a5scan:main",
            "daf.a6scan = daf.command_line.scan.a6scan:main",
            "daf.dscan = daf.command_line.scan.d1scan:main",
            "daf.d2scan = daf.command_line.scan.d2scan:main",
            "daf.d3scan = daf.command_line.scan.d3scan:main",
            "daf.d4scan = daf.command_line.scan.d4scan:main",
            "daf.d5scan = daf.command_line.scan.d5scan:main",
            "daf.d6scan = daf.command_line.scan.d6scan:main",
            "daf.ffscan = daf.command_line.scan.from_file_scan:main",
            "daf.scan = daf.command_line.scan.hkl_scan:main",
            "daf.mesh = daf.command_line.scan.mesh_scan:main",
            "daf.tscan = daf.command_line.scan.time_scan:main",
            "daf.init = daf.command_line.support.init:main",
            "daf.reset = daf.command_line.support.reset:main",
            "daf.setup = daf.command_line.support.setup:main",
        ],
    },
)
