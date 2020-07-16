#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import Spec_like as sl

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
    args = [int(i) for i in sys.argv]
    exp = sl.Control(*args)
else:
    exp = sl.Control(2,1,5)
exp.set_hkl((1,1,0))
exp.set_material('Si')
exp.set_exp_conditions(idir = (1,0,0), ndir = (0,0,1))
# exp.set_constraints(3)
exp.set_circle_constrain()


# exp(sv =  (0,0,90,0,0,0))
# exp.set_print_options(marker = '-', column_marker = '|',   space = 12)
exp()
print(exp)