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
        "console_scripts": ["hello-world = daf.command_line.query.status:main"]
    },
)
