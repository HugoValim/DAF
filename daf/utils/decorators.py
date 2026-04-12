import logging
import os
import sys

from daf import __version__
from daf.utils import dafutilities as du

logger = logging.getLogger(__name__)

LOG_FILE_NAME = "Log"


def cli_decorator(func: callable):
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        # Do the log
        daf_log()
        check_version()
        return ret

    return wrapper


def daf_log():
    """Function to be used as a decorator. It builds the log file"""
    log_message = sys.argv[0].split("/")[-1] if sys.argv else ""
    for i in sys.argv[1:]:
        log_message += " " + i
    with open(LOG_FILE_NAME, "a") as file_object:
        file_object.write(log_message + "\n")


def log_macro(dargs):
    """Function to generate the log and macro files"""
    log = sys.argv[0].split("command_line/")[1] if sys.argv else ""
    for i in sys.argv[1:]:
        log += " " + i
    with open(LOG_FILE_NAME, "a") as f:
        f.write(log + "\n")
    if dargs["macro_flag"] == "True":
        with open(dargs["macro_file"], "a") as f:
            f.write(log + "\n")


def check_version():
    """Check the version of current file if it exists, if the version is deprecated remove the file"""
    reset_flag = False
    try:
        data = du.read_yml(du.DEFAULT)
        if (
            data["version"].split(".")[0] != __version__.split(".")[0]
        ):  # If Version if different from "1.x.y" remove data:
            reset_flag = True
    except (KeyError, FileNotFoundError, TypeError):
        reset_flag = True

    if reset_flag:
        logger.warning("Your configuration file version is older than 1.0.0")
        logger.warning(
            "Your .Experiment file will be removed, please run daf.init to generate an up-to-date file"
        )
        if os.path.isfile(du.DEFAULT):
            os.remove(du.DEFAULT)
        sys.exit(0)
