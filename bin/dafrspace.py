#!/usr/bin/env python3
"""Move in reciprocal space by choosing a HKL in a graphical resciprocal space map"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du
import pandas as pd
import matplotlib.pyplot
from matplotlib import pyplot as plt

epi = '''
Eg:
    daf.rmap
    daf.rmap -i 1 1 0 -n 0 0 1
    daf.rmap -m Cu Ge
    daf.rmap -i 1 1 0 -n 0 0 1 -m Ge
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-i', '--IDir', metavar=('x', 'y', 'z'), type=float, nargs=3,help='Sets the plane paralel to x axis')
parser.add_argument('-n', '--NDir', metavar=('x', 'y', 'z'), type=float, nargs=3,help='Sets the plane perpendicular to x axis')
parser.add_argument('-m', '--materials', metavar = 'sample', nargs = '*', help='Add a predefined material to rmap visualization')
parser.add_argument('-s', '--scale', metavar='', type=float, help='Scale reference for the points in the map, default is 100')

args = parser.parse_args()
dic = vars(args)


matplotlib.pyplot.show(block=True)


dict_args = du.read()

U = np.array(dict_args['U_mat'])


mode = [int(i) for i in dict_args['Mode']]
idir = dict_args['IDir']
ndir = dict_args['NDir']
rdir = dict_args['RDir']


if args.IDir == None:
    paradir = idir
else:
    paradir = args.IDir

if args.NDir == None:
    normdir = ndir
else:
    normdir = args.NDir

if args.scale == None:
    args.scale = 100


Mu_bound = dict_args['bound_Mu']
Eta_bound = dict_args['bound_Eta']
Chi_bound = dict_args['bound_Chi']
Phi_bound = dict_args['bound_Phi']
Nu_bound = dict_args['bound_Nu']
Del_bound = dict_args['bound_Del']

exp = daf.Control(*mode)
exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['Energy'], sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
exp.set_U(U)
exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                    Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                    psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])

exp(calc=False)

ttmax, ttmin = exp.two_theta_max()

ax, h = exp.show_reciprocal_space_plane(ttmax = ttmax, ttmin=ttmin, idir=paradir, ndir=normdir, scalef=args.scale)


if args.materials:
    for i in args.materials:

        exp = daf.Control(*mode)
        exp.set_material(str(i))
        exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['Energy'], sampleor = dict_args['Sampleor'])
        exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
        exp.set_U(U)
        exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                            Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                            psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])

        exp(calc=False)
        ttmax, ttmin = exp.two_theta_max()

        ax, h2 = exp.show_reciprocal_space_plane(ttmax = ttmax, ttmin=ttmin, idir=paradir, ndir=normdir, scalef=args.scale, ax = ax)


plt.show(block=True)
ax.figure.show()


log = sys.argv.pop(0).split('command_line/')[1]

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
