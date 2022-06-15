import os
import sys


def daf_log(func):
    """Function to be used as a decorator. It builds the log file"""

    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        # Do the log
        log = sys.argv.pop(0).split("command_line/")[1]
        for i in sys.argv:
            log += " " + i
        os.system("echo {} >> Log".format(log))

    return wrapper


def log_macro(dargs):
    """Function to generate the log and macro files"""
    log = sys.argv.pop(0).split("command_line/")[1]
    for i in sys.argv:
        log += " " + i
    os.system("echo {} >> Log".format(log))
    if dargs["macro_flag"] == "True":
        os.system("echo {} >> {}".format(log, dict_args["macro_file"]))
