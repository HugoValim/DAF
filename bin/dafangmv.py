#!/usr/bin/env python3
"""Move the diffractometer by direct change in the angles"""

import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du



epi = '''
Eg:
    daf.amv --Del 30 --Eta 15
    daf.amv -d 30 -e 15
    daf.amv -d CEN
    daf.amv -d MAX -co roi1
    '''


parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog=epi)

parser.add_argument('-m', '--Mu', metavar='ang', type=str, help='Sets Mu angle to a desired position')
parser.add_argument('-e', '--Eta', metavar='ang', type=str, help='Sets Eta angle to a desired position')
parser.add_argument('-c', '--Chi', metavar='ang', type=str, help='Sets Chi angle to a desired position')
parser.add_argument('-p', '--Phi', metavar='ang', type=str, help='Sets Phi angle to a desired position')
parser.add_argument('-n', '--Nu', metavar='ang', type=str, help='Sets Nu angle to a desired position')
parser.add_argument('-d', '--Del', metavar='ang', type=str, help='Sets Del angle to a desired position')
parser.add_argument('-co', '--counter', metavar='counter', type=str, help='Choose the counter to be used')

args = parser.parse_args()
dic = vars(args)

def write_angs():
    dict_args = du.read()
    du.log_macro(dict_args)
    dict_ = dict_args['scan_stats']
    if dict_:
        if args.counter is not None:
            CEN = dict_[args.counter]['FWHM_at']
            MAX = dict_[args.counter]['peak_at']
            stat_dict = {'CEN' : CEN, 'MAX' : MAX}
        elif dict_args['main_scan_counter']:
            CEN = dict_[dict_args['main_scan_counter']]['FWHM_at']
            MAX = dict_[dict_args['main_scan_counter']]['peak_at']
            stat_dict = {'CEN' : CEN, 'MAX' : MAX}
        else:
            values_view = dict_.keys()
            value_iterator = iter(values_view)
            first_key = next(value_iterator)
            CEN = dict_[first_key]['FWHM_at']
            MAX = dict_[first_key]['peak_at']
            stat_dict = {'CEN' : CEN, 'MAX' : MAX}


    for j,k in dic.items():
        if j in dict_args and k is not None:
            if k == 'CEN' or k == 'MAX':
                dict_args[j] = stat_dict[k]
            else:
                dict_args[j] = float(k)
    du.write(dict_args)
write_angs()

dict_args = du.read()

U = np.array(dict_args['U_mat'])


mode = [int(i) for i in dict_args['Mode']]
idir = dict_args['IDir']
ndir = dict_args['NDir']
rdir = dict_args['RDir']

exp = daf.Control(*mode)
exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])

if dict_args['Material'] in dict_args['user_samples'].keys():
    exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

else: 
    exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
# exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
exp.set_U(U)
hklnow = exp.calc_from_angs(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])
hklnow = list(hklnow)
pseudo = exp.calc_pseudo(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])

pseudo_dict = {'alpha':pseudo[0], 'qaz':pseudo[1], 'naz':pseudo[2], 'tau':pseudo[3], 'psi':pseudo[4], 'beta':pseudo[5], 'omega':pseudo[6], 'hklnow':hklnow}


for j,k in pseudo_dict.items():
    if j in dict_args:
        dict_args[j] = str(k)
du.write(dict_args)
