#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du
import pandas as pd
import matplotlib.pyplot
from matplotlib import pyplot as plt
doc = """

Move in reciprocal space by choosing a HKL in a graphical resciprocal space map

"""

epi = '''
Eg:
    daf.rmap
    daf.rmap -i 1 1 0 -n 0 0 1
    daf.rmap -m Cu Ge
    daf.rmap -i 1 1 0 -n 0 0 1 -m Ge
    '''



parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)

# parser.add_argument('hkli', metavar='', type=float, nargs=3, help='Initial HKL for scan')
# parser.add_argument('hklf', metavar='', type=float, nargs=3, help='Final HKL for scan')
# parser.add_argument('points', metavar='', type=int, help='Number of points for the scan')
# parser.add_argument('-n', '--scan_name', metavar='', type=str, help='Name of the scan')
# parser.add_argument('-s', '--step', metavar='', type=float, help='Step for the scan')
# parser.add_argument('-sep', '--separator', metavar='', type=str, help='Chose the separator of scan file, default: ,')
# parser.add_argument('-m', '--Max_diff', metavar='', type=float, help='Max difference of angles variation, if 0 is given no verification will be done')
# parser.add_argument('-v', '--verbose', action='store_true', help='Show full output')
parser.add_argument('-i', '--IDir', metavar=('x', 'y', 'z'), type=float, nargs=3,help='Sets the plane paralel to x axis')
parser.add_argument('-n', '--NDir', metavar=('x', 'y', 'z'), type=float, nargs=3,help='Sets the plane perpendicular to x axis')
parser.add_argument('-m', '--materials', metavar = 'sample', nargs = '*', help='Add a predefined material to rmap visualization')
parser.add_argument('-s', '--scale', metavar='', type=float, help='Scale reference for the points in the map, default is 100')

args = parser.parse_args()
dic = vars(args)


matplotlib.pyplot.show(block=True)
# with open('.Experiment', 'r+') as exp:
 
#     lines = exp.readlines()


 

#     for i, line in enumerate(lines):
#         for j,k in dic.items():
            

 

#             if line.startswith(str(j)):
#                 if k != None:
#                     lines[i] = str(j)+'='+str(k)+'\n'
          
#             exp.seek(0)
            


 

#     for line in lines:
#         exp.write(line)


     
dict_args = du.dict_conv()

def ret_list(string):
    
    return [float(i) for i in string.strip('][').split(', ')]


Uw = dict_args['U_mat'].split(',')


U1 = [float(i) for i in Uw[0].strip('][').split(' ') if i != '']
U2 = [float(i) for i in Uw[1].strip('][').split(' ') if i != '']
U3 = [float(i) for i in Uw[2].strip('][').split(' ') if i != '']
U = np.array([U1, U2, U3])




    
mode = [int(i) for i in dict_args['Mode']]    
idir = ret_list(dict_args['IDir'])
ndir = ret_list(dict_args['NDir'])
rdir = ret_list(dict_args['RDir'])


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
    


Mu_bound = ret_list(dict_args['bound_Mu'])
Eta_bound = ret_list(dict_args['bound_Eta'])
Chi_bound = ret_list(dict_args['bound_Chi'])
Phi_bound = ret_list(dict_args['bound_Phi'])
Nu_bound = ret_list(dict_args['bound_Nu'])
Del_bound = ret_list(dict_args['bound_Del'])

exp = daf.Control(*mode)
exp.set_material(dict_args['Material'], float(dict_args["lparam_a"]), float(dict_args["lparam_b"]), float(dict_args["lparam_c"]), float(dict_args["lparam_alpha"]), float(dict_args["lparam_beta"]), float(dict_args["lparam_gama"]))
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
exp.set_U(U)
exp.set_constraints(Mu = float(dict_args['cons_Mu']), Eta = float(dict_args['cons_Eta']), Chi = float(dict_args['cons_Chi']), Phi = float(dict_args['cons_Phi']),
                    Nu = float(dict_args['cons_Nu']), Del = float(dict_args['cons_Del']), alpha = float(dict_args['cons_alpha']), beta = float(dict_args['cons_beta']),
                    psi = float(dict_args['cons_psi']), omega = float(dict_args['cons_omega']), qaz = float(dict_args['cons_qaz']), naz = float(dict_args['cons_naz']))



# startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]

#
# exp.scan(args.hkli, args.hklf, args.points, diflimit = float(dict_args['Max_diff']), name = dict_args['scan_name'], write=True, sep=dict_args['separator'])

# startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]

exp(calc=False)
ttmax, ttmin = exp.two_theta_max()
# print(ttmax)
ax, h = exp.show_reciprocal_space_plane(ttmax = ttmax, ttmin=ttmin, idir=paradir, ndir=normdir, scalef=args.scale)



if args.materials:
    for i in args.materials:
    
        exp = daf.Control(*mode)
        exp.set_material(str(i))
        exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
        exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
        exp.set_U(U)
        exp.set_constraints(Mu = float(dict_args['cons_Mu']), Eta = float(dict_args['cons_Eta']), Chi = float(dict_args['cons_Chi']), Phi = float(dict_args['cons_Phi']),
                            Nu = float(dict_args['cons_Nu']), Del = float(dict_args['cons_Del']), alpha = float(dict_args['cons_alpha']), beta = float(dict_args['cons_beta']),
                            psi = float(dict_args['cons_psi']), omega = float(dict_args['cons_omega']), qaz = float(dict_args['cons_qaz']), naz = float(dict_args['cons_naz']))
        
        
        
        # startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]
        
        #
        # exp.scan(args.hkli, args.hklf, args.points, diflimit = float(dict_args['Max_diff']), name = dict_args['scan_name'], write=True, sep=dict_args['separator'])
        
        # startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]
        
        exp(calc=False)
        ttmax, ttmin = exp.two_theta_max()
        # print(ttmax)
        
        ax, h2 = exp.show_reciprocal_space_plane(ttmax = ttmax, ttmin=ttmin, idir=paradir, ndir=normdir, scalef=args.scale, ax = ax)
    
     
    
     



plt.show(block=True)
ax.figure.show()


log = sys.argv.pop(0).split('command_line/')[1]    

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
