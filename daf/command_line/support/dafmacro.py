#!/usr/bin/env python3
"""Creates a macro to run commands from a script (txt) file"""

import argparse as ap
import sys
import os
import dafutilities as du


epi = """
Eg:
   daf.macro -i -n my_macro
   daf.macro -s
   daf.macro -e my_macro
    """


parser = ap.ArgumentParser(
    formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi
)
parser.add_argument(
    "-i", "--Initialize", action="store_true", help="Start recording your commands"
)
parser.add_argument("-s", "--Stop", action="store_true", help="Stop the macro")
parser.add_argument(
    "-n", "--name", metavar="name", type=str, help="Sets the name of the macro file"
)
parser.add_argument(
    "-e", "--Execute", metavar="file", type=str, help="Execute a recorded macro"
)

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()
du.log_macro(dict_args)

if args.Initialize:
    os.system("echo '#!/usr/bin/env bash' > {}".format(args.name))
    os.system("chmod 755 {}".format(args.name))
    dict_args["macro_flag"] = "True"
    dict_args["macro_file"] = args.name
    du.write(dict_args)

if args.Stop:
    dict_args["macro_flag"] = "False"
    # dict_args['macro_file'] = args.name
    du.write(dict_args)

if args.Execute:
    os.system("./{}".format(args.Execute))
