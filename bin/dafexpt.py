#!/usr/bin/env python3
"""Describe the experiment inputs"""

import argparse as ap
import sys
import os
import dafutilities as du
import numpy as np
import daf

epi = '''
Eg:
    daf.expt --Material Si --Energy 8000
    daf.expt -m Si -e 8000
    daf.expt -s x+
    daf.expt -i 1 0 0 -n 0 1 0
    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog = epi)

parser.add_argument('-m', '--Material', metavar='samp', type=str, help='Sets the material that is going to be used in the experiment')
parser.add_argument('-p', '--Lattice_parameters', metavar=('a', 'b', 'c', 'alpha', 'beta', 'gamma '), type=float, nargs=6, help='Sets lattice parameters, must be passed if defining a new material')
parser.add_argument('-i', '--IDir', metavar=('x', 'y', 'z'), type=float, nargs=3,help='Sets the reflection paralel to the incident beam')
parser.add_argument('-n', '--NDir', metavar=('x', 'y', 'z'), type=float, nargs=3,help='Sets the reflection perpendicular to the incident beam')
parser.add_argument('-r', '--RDir', metavar=('x', 'y', 'z'), type=float, nargs=3,help='Sets the reference vector')
parser.add_argument('-s', '--Sampleor', metavar='or', type=str,help='Sets the sample orientation at Phi axis')
parser.add_argument('-e', '--Energy', metavar='en', type=float, help='Sets the energy of the experiment (eV), wavelength can also be given (angstrom)')

args = parser.parse_args()
dic = vars(args)


dict_args = du.read()

for j,k in dic.items():
    if j in dict_args and k is not None:
        dict_args[j] = k
du.write(dict_args)


if args.Lattice_parameters:
    dict_args['lparam_a'] = args.Lattice_parameters[0]
    dict_args['lparam_b'] = args.Lattice_parameters[1]
    dict_args['lparam_c'] = args.Lattice_parameters[2]
    dict_args['lparam_alpha'] = args.Lattice_parameters[3]
    dict_args['lparam_beta'] = args.Lattice_parameters[4]
    dict_args['lparam_gama'] = args.Lattice_parameters[5]
    du.write(dict_args)


dict_args = du.read()

if args.Material:

    U = np.array(dict_args['U_mat'])
    mode = [int(i) for i in dict_args['Mode']]

    exp = daf.Control(*mode)
    
    if args.Material in dict_args['user_samples'].keys():
        exp.set_material(args.Material, *dict_args['user_samples'][args.Material])
    
    else: 
        exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
    exp.set_exp_conditions(en = dict_args['Energy'])
    exp.set_U(U)
    UB = exp.calcUB()
    dict_args['U_mat'] = U.tolist() # yaml doesn't handle numpy arrays well, so using python's list is a better choice
    dict_args['UB_mat'] = UB.tolist() # yaml doesn't handle numpy arrays well, so using python's list is a better choice
    predef = exp.predefined_samples
    

    if args.Material not in predef:
        if args.Material not in dict_args['user_samples'].keys():       
            nsamp_dict = dict_args['user_samples']       
            nsamp_dict[args.Material] = [dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"]]
            dict_args['user_samples'] = nsamp_dict

    
    du.write(dict_args)



log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
