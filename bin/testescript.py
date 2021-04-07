#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import daf as sl
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

# a = (-180,180)
# if len(sys.argv) != 1:
#     sys.argv.pop(0)
#     args = [int(sys.argv[i]) for i in range(3)]
#     exp = sl.Control(*args)
#     if len(sys.argv) > 6:
#         args2 = [float(i) for i in sys.argv]
#         print(args2)
#         exp.set_hkl((args2[3], args2[4], args2[5]))
#         scanarg = (args2[3], args2[4], args2[5]), (args2[6], args2[7], args2[8]), int(sys.argv[9])
#     else:
#         exp.set_hkl((2,1,1))
#         scanarg = (2,1,1), (2.1,1,1), 100

# else:
exp = sl.Control(2,1,5)
exp.set_hkl((2,1,1))
# scanarg = (2,1,1), (2.1,1,1), 100

exp.set_material('Si')
exp.set_exp_conditions(idir = (1,0,0), ndir = (0,0,1), en = 8000)
# exp.set_constraints(setineq=(['Del', 10]))
# exp.set_circle_constrain(Mu=a, Eta=a, Nu=a, Del=a)


# exp(sv =  (20,30,90,0,30,0))
exp.set_print_options(marker = '-', column_marker = '|',   space = 16)
# exp.set_print_options(space = 10)
# exp()

# angs1 = [0, 5.28232, 0, 2, 0, 10.5647] # 1 0 0
# angs2 = [0, 5.28232, 2, 92, 0, 10.5647] # 0 1 0
# angs3 = [0, 5.28232, 92, 92, 0, 10.5647] # 0 0 1

# u = exp.calc_U_2HKL([1,0,0], angs1, [0,1,0], angs2)
# U , p = exp.calc_U_3HKL([1,0,0], angs1, [0,1,0], angs2, [0,0,1], angs3)
# print(u)
# print(U)
# print(p)
exp()
print(exp)
print()
# exp.scan(scanarg[0], scanarg[1], scanarg[2])
# print(exp)
# print()
