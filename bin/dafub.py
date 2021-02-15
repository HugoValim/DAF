#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du

doc = """

Defines UB matrix and Calculate UB matrix from 2 or 3 reflections

"""

    
epi = '''
Eg:
    daf.ub -r1 1 0 0 0 5.28232 0 2 0 10.5647
    daf.ub -r2 0 1 0 0 5.28232 2 92 0 10.5647
    daf.ub -c2
    daf.ub -U 1 0 0 0 1 0 0 0 1
    daf.up -s
    daf.up -s -p
    '''



parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)

parser.add_argument('-r1', '--hkl1', metavar=('H', 'K', 'L', 'Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'), type=float, nargs=9, help='HKL and angles for first reflection')
parser.add_argument('-r2', '--hkl2', metavar=('H', 'K', 'L', 'Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'), type=float, nargs=9, help='HKL and angles for second reflection')
parser.add_argument('-r3', '--hkl3', metavar=('H', 'K', 'L', 'Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'),type=float, nargs=9, help='HKL and angles for third reflection')
parser.add_argument('-U', '--Umatrix', metavar=('a11', 'a12', 'a13', 'a21', 'a22', 'a23', 'a31', 'a32', 'a33'), type=float, nargs=9, help='Sets U matrix')
parser.add_argument('-UB', '--UBmatrix', metavar=('a11', 'a12', 'a13', 'a21', 'a22', 'a23', 'a31', 'a32', 'a33'), type=float, nargs=9, help='Sets UB matrix')
parser.add_argument('-c2', '--Calc2', action='store_true', help='Calculate UB for 2 reflections')
parser.add_argument('-c3', '--Calc3', action='store_true', help='Calculate UB for 3 reflections, the right energy must be setted in this case')
parser.add_argument('-l', '--list', action='store_true', help='List stored reflections')
parser.add_argument('-s', '--Show', action='store_true', help='Show U and UB')
parser.add_argument('-p', '--Params', action='store_true', help='Lattice parameters if 3 reflection calculation had been done')


args = parser.parse_args()
dic = vars(args)


with open('.Experiment', 'r+') as exp:
 
    lines = exp.readlines()


 

    for i, line in enumerate(lines):
        for j,k in dic.items():
            

 

            if line.startswith(str(j)):
                if k != None:
                    lines[i] = str(j)+'='+str(k)+'\n'
          
            exp.seek(0)
            
          


    for line in lines:
        exp.write(line)



if args.UBmatrix:
    UB = np.array(args.UBmatrix).reshape(3,3)
    with open('.Experiment', 'r+') as exp:
  
          lines = exp.readlines()
     
     
      
     
          for i, line in enumerate(lines):
             
                 
     
      
     
            # if line.startswith('U'):
            #         lines[i] = 'U='+str(U[0])+','+str(U[1])+','+str(U[2])+'\n'
            if line.startswith('UB_mat'):
                    lines[i] = 'UB_mat='+str(UB[0])+','+str(UB[1])+','+str(UB[2])+'\n'
          
            exp.seek(0)
                 
               
     
     
          for line in lines:
              exp.write(line)




lb = lambda x: "{:.5f}".format(float(x))




if args.Show:
    
    dict_args = du.dict_conv()
    
    Uw = dict_args['U_mat'].split(',')


    U1 = [float(i) for i in Uw[0].strip('][').split(' ') if i != '']
    U2 = [float(i) for i in Uw[1].strip('][').split(' ') if i != '']
    U3 = [float(i) for i in Uw[2].strip('][').split(' ') if i != '']
    U = np.array([U1, U2, U3])
    
    UBw = dict_args['UB_mat'].split(',')


    UB1 = [float(i) for i in UBw[0].strip('][').split(' ') if i != '']
    UB2 = [float(i) for i in UBw[1].strip('][').split(' ') if i != '']
    UB3 = [float(i) for i in UBw[2].strip('][').split(' ') if i != '']
    UB = np.array([UB1, UB2, UB3])

    center1 = "\u2502{:^11}"
    center2 = "{:^11}"
    center3 = "{:^11}\u2502"
    fmt1 = [
                    ('', 'ident',  9),        
                    ('', 'col1',   12),
                    ('', 'col2',   12),
                    ('', 'col3',   12),
               
                   ]
    
    data1 = [{'ident':'', 'col1': center1.format(lb(U1[0])), 'col2':center2.format(lb(U1[1])), 'col3':center3.format(lb(U1[2]))},
             {'ident':'U    =   ','col1': center1.format(lb(U2[0])), 'col2':center2.format(lb(U2[1])), 'col3':center3.format(lb(U2[2]))},
             {'ident':'','col1': center1.format(lb(U3[0])), 'col2':center2.format(lb(U3[1])), 'col3':center3.format(lb(U3[2]))}
             ]
    
    data2 = [{'ident':'','col1': center1.format(lb(UB1[0])), 'col2':center2.format(lb(UB1[1])), 'col3':center3.format(lb(UB1[2]))},
             {'ident':'UB   = ','col1': center1.format(lb(UB2[0])), 'col2':center2.format(lb(UB2[1])), 'col3':center3.format(lb(UB2[2]))},
             {'ident':'','col1': center1.format(lb(UB3[0])), 'col2':center2.format(lb(UB3[1])), 'col3':center3.format(lb(UB3[2]))}
             ]
    
    Utp = daf.TablePrinter(fmt1, ul='')(data1)
    UBtp = daf.TablePrinter(fmt1, ul='')(data2)
    
    print('')
    print(Utp)
    print('')
    print(UBtp)
    print('')
    
    


if args.Params:
    
    dict_args = du.dict_conv()
    
    print('')
    print('a    =    {}'.format(dict_args["lparam_a"]))
    print('b    =    {}'.format(dict_args["lparam_b"]))
    print('c    =    {}'.format(dict_args["lparam_c"]))
    print('\u03B1    =    {}'.format(dict_args["lparam_alpha"]))
    print('\u03B2    =    {}'.format(dict_args["lparam_beta"]))
    print('\u03B3    =    {}'.format(dict_args["lparam_gama"]))
    print('')



def ret_list(string):
    
    return [float(i) for i in string.strip('][').split(', ')]

dict_args = du.dict_conv()

if dict_args['hkl1'] != '':
    r1 = ret_list(dict_args['hkl1'])
    hkl1 = r1[:3]
    angs1 = r1[3:9]
else: 
    hkl1 = None

  
if dict_args['hkl2'] != '':
    r2 = ret_list(dict_args['hkl2'])
    hkl2 = r2[:3]
    angs2 = r2[3:9]
else:
    hkl2 = None
        
if dict_args['hkl3'] != '':
    r3 = ret_list(dict_args['hkl3'])
    hkl3 = r3[:3]
    angs3 = r3[3:9]
else:
    hkl3 = None

if args.list:
    print('')
    if hkl1:
        print('HKL1: {}  {}'.format(hkl1, angs1))
    if hkl2:
        print('HKL2: {}  {}'.format(hkl2, angs2))
    if hkl3:
        print('HKL3: {}  {}'.format(hkl3, angs3))
    
    print('')

if args.Umatrix:
    U = np.array(args.Umatrix).reshape(3,3)
    mode = [int(i) for i in dict_args['Mode']]    

    exp = daf.Control(*mode)
    exp.set_material(dict_args['Material'], float(dict_args["lparam_a"]), float(dict_args["lparam_b"]), float(dict_args["lparam_c"]), float(dict_args["lparam_alpha"]), float(dict_args["lparam_beta"]), float(dict_args["lparam_gama"]))
    exp.set_exp_conditions(en = float(dict_args['Energy']))
    exp.set_U(U)
    UB = exp.calcUB()
    with open('.Experiment', 'r+') as exp:
  
          lines = exp.readlines()
     
     
      
     
          for i, line in enumerate(lines):
             
                 
     
      
     
            if line.startswith('U_mat'):
                    lines[i] = 'U_mat='+str(U[0])+','+str(U[1])+','+str(U[2])+'\n'
            if line.startswith('UB'):
                    lines[i] = 'UB_mat='+str(UB[0])+','+str(UB[1])+','+str(UB[2])+'\n'
          
            exp.seek(0)
                 
               
     
     
          for line in lines:
              exp.write(line)




if  args.Calc2:
    mode = [int(i) for i in dict_args['Mode']]    

    exp = daf.Control(*mode)
    exp.set_material(dict_args['Material'], float(dict_args["lparam_a"]), float(dict_args["lparam_b"]), float(dict_args["lparam_c"]), float(dict_args["lparam_alpha"]), float(dict_args["lparam_beta"]), float(dict_args["lparam_gama"]))
    exp.set_exp_conditions(en = float(dict_args['Energy']))
    
    U, UB = exp.calc_U_2HKL(hkl1, angs1, hkl2, angs2)

    
    with open('.Experiment', 'r+') as exp:
  
          lines = exp.readlines()
     
     
      
     
          for i, line in enumerate(lines):
             
                 
     
      
     
            if line.startswith('U_mat'):
                    lines[i] = 'U_mat='+str(U[0])+','+str(U[1])+','+str(U[2])+'\n'
            if line.startswith('UB_mat'):
                    lines[i] = 'UB_mat='+str(UB[0])+','+str(UB[1])+','+str(UB[2])+'\n'
          
            exp.seek(0)
                 
               
     
     
          for line in lines:
              exp.write(line)

if  args.Calc3:
    mode = [int(i) for i in dict_args['Mode']]    

    exp = daf.Control(*mode)
    # exp.set_material(dict_args['Material'])
    exp.set_exp_conditions(en = float(dict_args['Energy']))
    
    U, UB, rp = exp.calc_U_3HKL(hkl1, angs1, hkl2, angs2, hkl3, angs3)

    with open('.Experiment', 'r+') as exp:
 
         lines = exp.readlines()
    
    
     
    
         for i, line in enumerate(lines):
            
                
    
     
             
            if line.startswith('U_mat'):
                lines[i] = 'U_mat='+str(U[0])+','+str(U[1])+','+str(U[2])+'\n'
            
            if line.startswith('UB_mat'):
                lines[i] = 'UB_mat='+str(UB[0])+','+str(UB[1])+','+str(UB[2])+'\n'
            
            if line.startswith('lparam_a'):   
                lines[i] = 'lparam_a='+lb(rp[0])+'\n'
            if line.startswith('lparam_b'):   
                lines[i] = 'lparam_b='+lb(rp[1])+'\n'
            if line.startswith('lparam_c'):   
                lines[i] = 'lparam_c='+lb(rp[2])+'\n'
            if line.startswith('lparam_alpha'):   
                lines[i] = 'lparam_alpha='+lb(rp[3])+'\n'
            if line.startswith('lparam_beta'):   
                lines[i] = 'lparam_beta='+lb(rp[4])+'\n'
            if line.startswith('lparam_gama'):   
                lines[i] = 'lparam_gama='+lb(rp[5])+'\n'
             
          
         
            exp.seek(0)
                
              
    
    
         for line in lines:
             exp.write(line)


log = sys.argv.pop(0).split('command_line/')[1]        

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
