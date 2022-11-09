import os


def setup_package():
    """Set up your environment for test package"""
    if not os.path.isfile(".Experiment"):
        os.system("daf.init -s")


def teardown_package():
    """revert the state"""
