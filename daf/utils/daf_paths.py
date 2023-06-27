import os
from os import path
import pathlib


class DAFPaths:
    DEFAULT_FILE_NAME = ".Experiment"
    HOME = os.getenv("HOME")
    DAF_CONFIGS = path.join(HOME, ".daf")
    SCAN_CONFIGS = path.join(DAF_CONFIGS, "scan")
    GLOBAL_EXPERIMENT_DEFAULT = path.join(DAF_CONFIGS, DEFAULT_FILE_NAME)
    LOCAL_EXPERIMENT_DEFAULT = path.join(".", DEFAULT_FILE_NAME)

    @classmethod
    def check_for_local_config(cls) -> pathlib.Path:
        """Check for if the user have a local configuration. If it exists use it, otherwise use the Global config"""
        local_path = pathlib.Path(cls.LOCAL_EXPERIMENT_DEFAULT)
        if local_path.exists():
            return local_path
        else:
            global_path = pathlib.Path(cls.GLOBAL_EXPERIMENT_DEFAULT)
            return global_path
