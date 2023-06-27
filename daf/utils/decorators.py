import os
import sys

from daf import __version__
from daf.utils import dafutilities as du

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
    log_message = sys.argv.pop(0).split("/")[-1]
    for i in sys.argv:
        log_message += " " + i
    with open(LOG_FILE_NAME, "a") as file_object:
        file_object.write(log_message + "\n")


def log_macro(dargs):
    """Function to generate the log and macro files"""
    log = sys.argv.pop(0).split("command_line/")[1]
    for i in sys.argv:
        log += " " + i
    os.system("echo {} >> Log".format(log))
    if dargs["macro_flag"] == "True":
        os.system("echo {} >> {}".format(log, dict_args["macro_file"]))


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
        print("Your configuration file version is older than 1.0.0")
        print(
            "Your .Experiment file will be removed, please run daf.init to generate an up-to-date file"
        )
        if os.path.isfile(du.DEFAULT):
            os.remove(du.DEFAULT)
        sys.exit(0)
