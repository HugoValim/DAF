#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import Spec_like as sl
import pandas as pd
#      >detector<  >Reference<     >Sample<     >Sample<     >Sample<
#         g_mode1      g_mode2      g_mode3      g_mode4      g_mode5
# 0             .            .  omega-fixed            X            X  0
# 1   Delta-fixed   Alpha=Beta    Eta-fixed    Eta-fixed    Eta-fixed  1
# 2      Nu-fixed  Alpha-fixed     Mu-fixed     Mu-fixed     Mu-fixed  2
# 3     Qaz-fixed   Beta-fixed    Chi-fixed    Chi-fixed    Chi-fixed  3
# 4     Naz-fixed    Psi-fixed    Phi-fixed    Phi-fixed    Phi-fixed  4
# 5          Zone            X    Eta=Del/2            X            X  5
# 6             X            X      Mu=Nu/2            X            X  6



if len(sys.argv) != 1:
    sys.argv.pop(0)
    mode = [int(i) for i in sys.argv[0]]
    exp = sl.Control(*mode)
    args2 = [float(i) for i in sys.argv]
    exp.set_hkl((args2[1], args2[2], args2[3]))
    scanarg = (args2[1], args2[2], args2[3]), (args2[4], args2[5], args2[6]), int(sys.argv[7])

else:
    exp = sl.Control(2, 1, 5)
    exp.set_hkl((2,1,1))
    scanarg = (1.9,2.9,3.1), (2.1,3.1,2.9), 100

exp.set_material('Si')
exp.set_exp_conditions(idir = (1,0,0), ndir = (0,0,1), en = 8000)

# exp(sv =  (20,30,90,0,30,0))
# exp.set_print_options(marker = '-', column_marker = '|',   space = 16)
exp.set_print_options(space = 16)
exp()
print(exp)
print() 
exp.scan(scanarg[0], scanarg[1], scanarg[2])
print(exp)
print()
