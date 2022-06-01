#!/usr/bin/env python3
"""
     >detector<  >Reference<     >Sample<     >Sample<     >Sample<
        g_mode1      g_mode2      g_mode3      g_mode4      g_mode5
0             .            .  omega-fixed            X            X  0
1   Delta-fixed   Alpha=Beta    Eta-fixed    Eta-fixed    Eta-fixed  1
2      Nu-fixed  Alpha-fixed     Mu-fixed     Mu-fixed     Mu-fixed  2
3     Qaz-fixed   Beta-fixed    Chi-fixed    Chi-fixed    Chi-fixed  3
4     Naz-fixed    Psi-fixed    Phi-fixed    Phi-fixed    Phi-fixed  4
5         Zone*            X    Eta=Del/2            X            X  5
6       Energy*            X      Mu=Nu/2            X            X  6

*not implemented
"""

import argparse as ap
import sys
import os
import daf
import dafutilities as du

epi = '''
Eg:
    daf.mode 215, will set Nu fix, Alpha=Beta, Eta=Del/2
    '''

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=__doc__, epilog = epi)
parser.add_argument('Mode', type=str,help='Set the operation mode of the diffractometer, following the same modes as used in Spec, the mode should be passed without spaces')

args = parser.parse_args()
dic = vars(args)
dict_args = du.read()
du.log_macro(dict_args)

for j,k in dic.items():
    if j in dict_args:
        dict_args[j] = str(k)
du.write(dict_args)
