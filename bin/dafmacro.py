#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import dafutilities as du

doc = """

Creates a macro to run commands from a script (txt) file

"""

epi = '''
Eg:
   daf.macro -i -n my_macro
   daf.macro -s
   daf.macro -e my_macro
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog = epi)
parser.add_argument('-i', '--Initialize', action='store_true', help='Start recording your commands')
parser.add_argument('-s', '--Stop', action='store_true', help='Stop the macro')
parser.add_argument('-n', '--name', metavar='name',type=str, help='Sets the name of the macro file')
parser.add_argument('-e', '--Execute', metavar='file',type=str, help='Execute a recorded macro')

args = parser.parse_args()
dic = vars(args)

dict_args = du.dict_conv()

if args.Initialize:

    os.system("echo '#!/usr/bin/env bash' > {}".format(args.name))
    os.system("chmod 755 {}".format(args.name))

    with open('.Experiment', 'r+') as exp:

        lines = exp.readlines()




        for i, line in enumerate(lines):





            if line.startswith('macro_flag'):
                    lines[i] ='macro_flag=True\n'

            if line.startswith('macro_file'):
                    lines[i] ='macro_file='+args.name+'\n'


            exp.seek(0)




        for line in lines:
            exp.write(line)

if args.Stop:

    with open('.Experiment', 'r+') as exp:

        lines = exp.readlines()




        for i, line in enumerate(lines):





            if line.startswith('macro_flag'):
                    lines[i] ='macro_flag=False\n'

            # if line.startswith('macro_file'):
            #         lines[i] ='macro_file=macro'


            exp.seek(0)




        for line in lines:
            exp.write(line)

if args.Execute:
    os.system("./{}".format(args.Execute))


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))
