#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import dafutilities as du
doc = """

Sets the bounds of the diffractometer angles

"""

epi = '''
Eg: 
    daf.bounds --Mu -180 180 --Nu -180 180
    daf.bouns -m -180 180 -n -180 180
    '''
    

parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter, description=doc, epilog=epi)

parser.add_argument('-m', '--bound_Mu', metavar=('min', 'max'), type=float, nargs=2, help='Sets Mu bounds')
parser.add_argument('-e', '--bound_Eta', metavar=('min', 'max'),type=float, nargs=2, help='Sets Eta bounds')
parser.add_argument('-c', '--bound_Chi', metavar=('min', 'max'),type=float, nargs=2, help='Sets Chi bounds')
parser.add_argument('-p', '--bound_Phi', metavar=('min', 'max'),type=float, nargs=2, help='Sets Phi bounds')
parser.add_argument('-n', '--bound_Nu', metavar=('min', 'max'),type=float, nargs=2, help='Sets Nu bounds')
parser.add_argument('-d', '--bound_Del', metavar=('min', 'max'),type=float, nargs=2, help='Sets Del bounds')
parser.add_argument('-l', '--list', action='store_true', help='List the current bounds')
parser.add_argument('-r', '--Reset', action='store_true', help='Reset all bounds to default')

args = parser.parse_args()
dic = vars(args)
# print([(i,j) for i,j in dic.items()])
# with open ('Experiment', 'w') as doc:
#     for i,j in dic.items():
#         doc.write(str(i)+': '+str(j)+'\n')
# ndir = list2str(args.NDir)

bounds = {'bound_Mu' : [-20.0, 160.0], 'bound_Eta' : [-20.0, 160.0], 'bound_Chi' : [-5.0, 95.0], 'bound_Phi' : [-400.0, 400.0], 'bound_Nu' : [-20.0, 160.0], 'bound_Del' : [-20.0, 160.0]}

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

if args.Reset:
    
    with open('.Experiment', 'r+') as exp:
 
        lines = exp.readlines()
    
    
     
    
        for i, line in enumerate(lines):
            for j,k in bounds.items():
                
    
     
    
                if line.startswith(str(j)):
                        lines[i] = str(j)+'='+str(k)+'\n'
              
                exp.seek(0)
                


 

        for line in lines:
            exp.write(line)


dict_args = du.dict_conv()      
        
if args.list:
    
    print('')
    print('Mu    =    {}'.format(dict_args["bound_Mu"]))
    print('Eta   =    {}'.format(dict_args["bound_Eta"]))
    print('Chi   =    {}'.format(dict_args["bound_Chi"]))
    print('Phi   =    {}'.format(dict_args["bound_Phi"]))
    print('Nu    =    {}'.format(dict_args["bound_Nu"]))
    print('Del   =    {}'.format(dict_args["bound_Del"]))
    print('')    
    



log = sys.argv.pop(0).split('command_line/')[1]         

for i in sys.argv:
    log += ' ' + i

os.system("echo {} >> Log".format(log))

if dict_args['macro_flag'] == 'True':
    os.system("echo {} >> {}".format(log, dict_args['macro_file']))
