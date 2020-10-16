#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du
doc = """

Move in the reciprocal space by giving a HKL 

"""

epi = '''
Eg:
    daf.mv 1 1 1
    daf.mv 1 0 0 -v
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)

parser.add_argument('Move', metavar='H K L', type=float, nargs=3, help='Move to a desired HKL')
parser.add_argument('-v', '--verbose', action='store_true', help='Show full output')


args = parser.parse_args()
dic = vars(args)
  
    
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
Mu_bound = ret_list(dict_args['bound_Mu'])
Eta_bound = ret_list(dict_args['bound_Eta'])
Chi_bound = ret_list(dict_args['bound_Chi'])
Phi_bound = ret_list(dict_args['bound_Phi'])
Nu_bound = ret_list(dict_args['bound_Nu'])
Del_bound = ret_list(dict_args['bound_Del'])

# print(type(dict_args['IDir']))
# print(type(idir))

exp = daf.Control(*mode)
exp.set_hkl(args.Move)
exp.set_material(dict_args['Material'])
exp.set_exp_conditions(idir = idir, ndir = ndir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
exp.set_U(U)
exp.set_constraints(Mu = float(dict_args['cons_Mu']), Eta = float(dict_args['cons_Eta']), Chi = float(dict_args['cons_Chi']), Phi = float(dict_args['cons_Phi']),
                    Nu = float(dict_args['cons_Nu']), Del = float(dict_args['cons_Del']), alpha = float(dict_args['cons_alpha']), beta = float(dict_args['cons_beta']),
                    psi = float(dict_args['cons_psi']), omega = float(dict_args['cons_omega']), qaz = float(dict_args['cons_qaz']), naz = float(dict_args['cons_naz']))



startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]

exp(sv = startvalue)
error = exp.qerror
if error > 1e-4:
    exp()
if args.verbose:
    exp.set_print_options(marker = '', column_marker='', space=12)
    print(exp)
angs = exp.export_angles()

exp_dict = {'Mu':angs[0], 'Eta':angs[1], 'Chi':angs[2], 'Phi':angs[3], 'Nu':angs[4], 'Del':angs[5], 'tt':angs[6],
            'theta':angs[7], 'alpha':angs[8], 'qaz':angs[9], 'naz':angs[10], 'tau':angs[11], 'psi':angs[12], 'beta':angs[13], 'omega':angs[14], 'hklnow':list(angs[15])}

# print(exp_dict['hklnow'])
# print(angs[15])

if float(angs[16]) < 1e-4:
    with open('.Experiment', 'r+') as exp:
 
        lines = exp.readlines()
    
    
     
    
        for i, line in enumerate(lines):
            for j,k in exp_dict.items():
                
    
     
    
                if line.startswith(str(j)):
                        lines[i] = str(j)+'='+str(k)+'\n'
              
            exp.seek(0)
                
              
    
        
        for line in lines:
            exp.write(line)
        
        

else:
    print('Can\'t find the HKL')


       
        

log = sys.argv.pop(0).split('command_line/')[1]    

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")