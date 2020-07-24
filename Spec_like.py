#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import xrayutilities as xu
import numpy as np
import pandas as pd
from tqdm import tqdm
import sys


class TablePrinter(object):
    "Print a list of dicts as a table"
    def __init__(self, fmt, sep=' ', ul=None):
        """        
        @param fmt: list of tuple(heading, key, width)
                        heading: str, column label
                        key: dictionary key to value to print
                        width: int, column width in chars
        @param sep: string, separation between columns
        @param ul: string, character to underline column label, or None for no underlining
        """
        super(TablePrinter,self).__init__()
        self.fmt   = str(sep).join('{lb}{0}:{1}{rb}'.format(key, width, lb='{', rb='}') for heading,key,width in fmt)
        self.head  = {key:heading for heading,key,width in fmt}
        self.ul    = {key:str(ul)*width for heading,key,width in fmt} if ul else None
        self.width = {key:width for heading,key,width in fmt}

    def row(self, data):
        return self.fmt.format(**{ k:str(data.get(k,''))[:w] for k,w in self.width.items() })

    def __call__(self, dataList):
        _r = self.row
        res = [_r(data) for data in dataList]
        res.insert(0, _r(self.head))
        if self.ul:
            res.insert(1, _r(self.ul))
        return '\n'.join(res)


class Control(object):
    
    colunas = {1:{0 : '--', 1 : 'del_fix', 2 : 'nu_fix', 3 : 'qaz_fix', 4 : 'naz_fix', 5 : 'zone', 6 : '--'},
               2:{0 : '--', 1 : '\u03B1 = \u03B2', 2 : '\u03B1 fix', 3 : '\u03B2 fix', 4 : 'psi_fix', 5 : '--', 6 : '--'},
               3:{0 : '\u03C9 fix', 1 : 'eta_fix', 2 : 'mu_fix', 3 : 'chi_fix', 4 : 'phi_fix', 5 : '\u03B7 = \u03B4/2', 6 : '\u03BC = \u03BD/2'},
               4:{0 : '--', 1 : 'eta_fix', 2 : 'mu_fix', 3 : 'chi_fix', 4 : 'phi_fix', 5 : '--', 6 : '--'},
               5:{0 : '--', 1 : 'eta_fix', 2 : 'mu_fix', 3 : 'chi_fix', 4 : 'phi_fix', 5 : '--', 6 : '--'}}
    

    
    def __init__(self, *args):
        
        for i in (args):
            if i not in (0,1,2,3,4,5,6):
                raise ValueError('The values of columns must be between 0 and 6')
        
        if args[0] == 0 and args[1] == 0:
            if len(args) <= 3:
                raise ValueError('''If de two first columns are set to 0, the columns 4 and 5 must be given''')
            elif args[3] == 0 or args[4] == 0:
                raise ValueError('''If de two first columns are set to 0, the columns 4 and 5 must not be 0''')
        
        if args[0] == 5:
            raise('Zone mode was not implemented yet')
        
        self.col1 = args[0]
        self.col2 = args[1]
        self.col3 = args[2]
        
        if len(args) >= 4:
            self.col4 = args[3]
        else:
            self.col4 = 0
        
        if len(args) == 5:
            self.col5 = args[4]
        else:
            self.col5 = 0
        
        self.space = 12
        self.marker = '\u2501'
        self.column_marker = '\u2503'
        self.center = self.column_marker+"{:^" + str(self.space - 2) + "}" + self.column_marker
        self.roundfit = 5
        
        self.setup = (Control.colunas[1][self.col1], Control.colunas[2][self.col2], Control.colunas[3][self.col3], 
              Control.colunas[4][self.col4], Control.colunas[5][self.col5])

     
        angles = {'--' : 'x', 'del_fix' : 'Del', 'nu_fix' : 'Nu', 'mu_fix' : 'Mu', 
                  'eta_fix' : 'Eta', 'chi_fix' : 'Chi','phi_fix' : 'Phi'}
        
        cons = {'--' : 'x', 'qaz_fix' : 'qaz', 'naz_fix' : 'naz', '\u03B1 = \u03B2' : 'aeqb', 
                     '\u03B1 fix' : 'alpha', '\u03B2 fix' : 'beta', 'psi_fix' : 'psi', '\u03C9 fix' : 'omega',
                     '\u03B7 = \u03B4/2' : 'eta=del/2', '\u03BC = \u03BD/2' : 'mu=nu/2'}
        
        self.motcon = list()
        self.const = list()
      
        for i in range(len(self.setup)):
            if self.setup[i] in angles.keys():
                if i == 0 and self.setup[i] == '--':
                    pass
                    
                elif i == 1 and self.setup[i] == '--':
                    pass
                
                else:    
                    self.motcon.append(angles[self.setup[i]])
         
            else:
                if self.setup[i] in cons.keys():
                    self.const.append(cons[self.setup[i]])
            
   
        
        
       
        # print(self.const)
        self.fix = list()
        
        
        for i in self.motcon:
            if i != 'x':
               self.fix.append(i)
     
        
        
        if 'Mu' in self.fix:
            self.Mu_bound = 0
        else:
            self.Mu_bound = (-180,180)
        
        if 'Eta' in self.fix:
            self.Eta_bound = 0
        else:
            self.Eta_bound = (-180,180)
        
        if 'Chi' in self.fix:
            self.Chi_bound = 0
        else:
            self.Chi_bound = (-5,95)
        
        if 'Phi' in self.fix:
            self.Phi_bound = 0
        else:
            self.Phi_bound = (30,400)
            
        if 'Nu' in self.fix:
            self.Nu_bound = 0
        else:
            self.Nu_bound = (-180,180)
            
        if 'Del' in self.fix:
            self.Del_bound = 0
        else:
            self.Del_bound = (-180,180)
        
     
        self.constrain = [(self.const[i],0) if self.const[i] not in ('eta=del/2', 'mu=nu/2', 'aeqb') else (self.const[i], '--') for i in range(len(self.const))]
 
        self.idir = (0,0,1)
        self.ndir = (1,1,0)
        self.sampleor = 'x+'
        self.en = 8000
        self.lam = xu.en2lam(self.en)
        self.posrestrict = ()
        self.negrestrict = ()
        self.fcsv = '{0:.4f}'.format


    
    
    def set_hkl(self, HKL):
        
        self.hkl = HKL
    
    def set_material(self, sample):
        
        materiais = {'Si':xu.materials.Si, 'Al' : xu.materials.Al, 'Co' : xu.materials.Co,
                     'Cu' : xu.materials.Cu, 'Cr' : xu.materials.Cr, 'Fe' : xu.materials.Fe, 
                     'Ge' : xu.materials.Ge, 'MgO' : xu.materials.MgO, 'Sn' : xu.materials.Sn,
                     'LaB6' : xu.materials.LaB6}
                     
        self.samp = materiais[sample]
    
    def pseudoAngleConst(angles, pseudo_angle, fix_angle):
    
        if pseudo_angle == 'eta=del/2':
            return angles[1] - angles[5]/2
        elif pseudo_angle == 'mu=nu/2':
            return angles[0] - angles[4]/2
        
        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg
        
        Mu = angles[0] + 1e-6
        if pseudo_angle == 'Mu':
            return Mu - fix_angle
        
        Eta = angles[1] + 1e-6
        if pseudo_angle == 'Eta':
            return Eta - fix_angle
        
        Chi = angles[2] + 1e-6
        if pseudo_angle == 'Chi':
            return Chi - fix_angle
        
        Phi= angles[3] + 1e-6
        if pseudo_angle == 'Phi':
            return Phi - fix_angle
        
        Nu = angles[4] + 1e-6
        if pseudo_angle == 'Nu':
            return Nu - fix_angle
        
        Del = angles[5] + 1e-6
        if pseudo_angle == 'Del':
            return Del - fix_angle
    
        PHI = MAT([[np.cos(rad(Phi)),    np.sin(rad(Phi)),   0],
              [-np.sin(rad(Phi)),  np.cos(rad(Phi)),     0],
              [0,                         0,             1]])
    
        CHI = MAT([[np.cos(rad(Chi)),    0,           np.sin(rad(Chi))],
                  [0,                       1,                   0],
                  [-np.sin(rad(Chi)),    0,           np.cos(rad(Chi))]])
        
        ETA = MAT([[np.cos(rad(Eta)),    np.sin(rad(Eta)),   0],
                   [-np.sin(rad(Eta)),   np.cos(rad(Eta)),   0],
                   [0,                         0,           1]])
        
        MU = MAT([[1,                       0,                      0],
                  [0,            np.cos(rad(Mu)),    -np.sin(rad(Mu))],
                  [0,            np.sin(rad(Mu)),    np.cos(rad(Mu))]])
        
        DEL = MAT([[np.cos(rad(Del)),    np.sin(rad(Del)),   0],
                   [-np.sin(rad(Del)),   np.cos(rad(Del)),   0],
                   [0,                       0,              1]])
        
        NU = MAT([[1,                    0,                         0],
                  [0,            np.cos(rad(Nu)),    -np.sin(rad(Nu))],
                  [0,            np.sin(rad(Nu)),    np.cos(rad(Nu))]])
        
        Z = MU.dot(ETA).dot(CHI).dot(PHI)
        nz = Z.dot([0,0,1])
        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        tB1 = ttB1/2
        
        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))
        
        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
        upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu))))
        qaz = upsipseudo
        # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))
        
        phipseudo = deg(np.arctan((nz.dot([1,0,0]))/(nz.dot([0,0,1]))))
        naz = phipseudo
        
        arg1 = np.cos(rad(alphain))*np.cos(rad(tB1))*np.cos(rad(phipseudo-upsipseudo))+np.sin(rad(alphain))*np.sin(rad(tB1))
        if arg1 >1:
            arg1 = 0.999999999999999999999
        elif arg1 < -1:
            arg3 = -0.99999999999999999999
        taupseudo = deg(np.arccos(arg1))
        
        arg2 = (np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1)))
        if arg2 >1:
            arg2 = 0.999999999999999999999
        elif arg2 < -1:
            arg2 = -0.99999999999999999999
   
        
        psipseudo = deg(np.arccos(arg2))
        
        # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))
        # print(arg3)
        if arg3 >1:
            arg3 = 0.99999999999999999999
        # elif arg3 < -1:
        #     arg3 = -0.9999999999999999999
        # print(arg3)
        betaout = deg(np.arcsin(arg3))
        
        arg4 = (np.sin(rad(Eta))*np.sin(rad(upsipseudo))+np.sin(rad(Mu))*np.cos(rad(Eta))*np.cos(rad(upsipseudo)))*np.cos(rad(tB1))-np.cos(rad(Mu))*np.cos(rad(Eta))*np.sin(rad(tB1))
        if arg4 >1:
         arg4 = 0.999999999999999999999
        elif  arg4 < -1:
            arg3 = -0.999999999999999999
        omega = deg(np.arcsin(arg4))
        
        a = (alphain, upsipseudo, phipseudo, taupseudo, psipseudo, betaout, omega)
        # print(np.round(a,3))
      
        
        if pseudo_angle == 'alpha':
            return alphain - fix_angle
        
        elif pseudo_angle == 'beta':
            return betaout - fix_angle
        
        elif pseudo_angle == 'qaz':     
            return upsipseudo - fix_angle
        
        elif pseudo_angle == 'naz':
            return phipseudo - fix_angle
        
        elif pseudo_angle == 'tau':
            return taupseudo - fix_angle
       
        elif pseudo_angle == 'psi':
            # print(psipseudo - fix_angle)
            return psipseudo - fix_angle
        
        elif pseudo_angle == 'omega':
            return omega - fix_angle
        
        elif pseudo_angle == 'aeqb':
            # print(betaout - alphain)
            return betaout - alphain
    
    def set_constraints(self, *args, setineq = None, **kwargs):

        if args:
            s = 0
            if 'eta=del/2' in self.const:
                s+=1
            if 'mu=nu/2' in self.const:
                s+=1
            if 'aeqb' in self.const:
                s+=1
                
            if len(args) != 0:
                if len(args) != (len(self.constrain)-s):
                    raise ValueError('Constraints passed must have the same size of constrained angles')
                
                elif self.col2 == 1 and self.col3 == 0:
                    args=list(args)
                    args.append(args[-1])
                    self.constrain = [(self.const[i],args[i]) if self.const[i] not in ('eta=del/2', 'mu=nu/2', 'aeqb') else (self.const[i], '--') for i in range(len(self.const))]
                
                else:
                    self.constrain = [(self.const[i],args[i]) if self.const[i] not in ('eta=del/2', 'mu=nu/2', 'aeqb') else (self.const[i], '--') for i in range(len(self.const))]

        self.posrestrict = [setineq]
        
        if kwargs:
            if 'Mu' in kwargs.keys() and 'Mu' in self.fix:
                self.Mu_bound = kwargs['Mu']
            
            if 'Eta' in kwargs.keys() and 'Eta' in self.fix:
                self.Eta_bound = kwargs['Eta']
     
            if 'Chi' in kwargs.keys() and 'Chi' in self.fix:
                self.Chi_bound = kwargs['Chi']
         
            if 'Phi' in kwargs.keys() and 'Phi' in self.fix:
                self.Phi_bound = kwargs['Phi']
          
            if 'Nu' in kwargs.keys() and 'Nu' in self.fix:
                self.Nu_bound = kwargs['Nu']
         
            if 'Del' in kwargs.keys() and 'Del' in self.fix:
                self.Del_bound = kwargs['Del']
            

    
    def set_circle_constrain(self, **kwargs):
         
        if 'Mu' in kwargs.keys() and 'Mu' not in self.fix:
            self.Mu_bound = kwargs['Mu']
        
        if 'Eta' in kwargs.keys() and 'Eta' not in self.fix:
            self.Eta_bound = kwargs['Eta']
 
        if 'Chi' in kwargs.keys() and 'Chi' not in self.fix:
            self.Chi_bound = kwargs['Chi']
     
        if 'Phi' in kwargs.keys() and 'Phi' not in self.fix:
            self.Phi_bound = kwargs['Phi']
      
        if 'Nu' in kwargs.keys() and 'Nu' not in self.fix:
            self.Nu_bound = kwargs['Nu']
     
        if 'Del' in kwargs.keys() and 'Del' not in self.fix:
            self.Del_bound = kwargs['Del']
    
    def set_exp_conditions(self, idir = (0,0,1), ndir = (1,1,0), sampleor = 'x+', en = 8000):
        
        self.idir = idir
        self.ndir = ndir
        self.sampleor = sampleor
         
        ENWL = en
       
        if ENWL > 50 :
              self.en = ENWL
              self.lam = xu.en2lam(en)
        else:
              self.lam = ENWL
              self.en = xu.lam2en(lam)
            
   
    def set_print_options(self, marker = '\u2501', column_marker = '\u2503', space = 12):
     
        self.marker = marker
        self.column_marker = column_marker
        
        if space > 10:
            if space % 2 == 0:
                self.space = space
            elif space % 2 == 0:
                self.space = space - 1
        else:
            self.space = 10
           
        self.center = self.column_marker+"{:^" + str(self.space - 2) + "}" + self.column_marker
   
        if self.space > 10:
            self.roundfit = int(4 + ((self.space - 10)/2))
        else:
            self.roundfit = 4
      
    
    
    def __str__(self):
        
        if self.isscan:
            return  repr(self.formscantxt)
     
        
        else:
            dprint = {'x' : '--', 'Mu' : self.Mu_bound, 'Eta' : self.Eta_bound, 'Chi' : self.Chi_bound,
                      'Phi' : self.Phi_bound, 'Nu' : self.Nu_bound, 'Del' : self.Del_bound}
            
            
            self.forprint = self.constrain.copy()
            
            if self.col1 in (1,2):
                if self.col1 == 1:
                    self.forprint.insert(0,(self.setup[0],self.Del_bound))
                elif self.col1 == 2:
                    self.forprint.insert(0,(self.setup[0],self.Nu_bound))
                for i in self.motcon:
                    if i not in ('Del', 'Nu'):
                        self.forprint.append((i,dprint[i]) )
                if self.col2 ==0:
                    self.forprint.insert(1,('XD', '--'))
        
            else:
                if self.col1 == 0 and self.col2 ==0:
                    
                    self.forprint.insert(0,('XD', '--'))
                    self.forprint.insert(0,('XD', '--'))              
    
                    for i in self.motcon:
                        self.forprint.append((i,dprint[i]))
          
               
                elif self.col1 == 0:
                   
                    self.forprint.insert(0,('XD', '--'))
                   
                   
                    for i in self.motcon:
                        self.forprint.append((i,dprint[i]))
                   
                   
                    
                
                elif self.col2 == 0:
                    self.forprint.insert(1,('XD', '--'))
                    # self.forprint.pop()
          
                    for i in self.motcon:
                        self.forprint.append((i,dprint[i]))
                else:
                    for i in self.motcon:
                        self.forprint.append((i,dprint[i]))
    
            data = [{'col1':self.center.format('MODE'), 'col2':self.center.format(self.setup[0]), 'col3':self.center.format(self.setup[1]), 'col4':self.center.format(self.setup[2]), 'col5':self.center.format(self.setup[3]), 'col6' : self.center.format(self.setup[4]), 'col7' : self.center.format('Error')},
                    {'col1':self.center.format(str(self.col1)+str(self.col2)+str(self.col3)+str(self.col4)+str(self.col5)), 'col2':self.center.format(self.forprint[0][1]), 'col3':self.center.format(self.forprint[1][1]), 'col4':self.center.format(self.forprint[2][1]), 'col5':self.center.format(self.forprint[3][1]), 'col6' : self.center.format(self.forprint[4][1]), 'col7' : self.center.format('%.3g' % self.qerror)},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('2Theta exp'), 'col2':self.center.format('Dhkl'), 'col3':self.center.format('Energy'), 'col4':self.center.format('HKL'), 'col5' : self.center.format('HKLCalc'), 'col6':self.center.format('idir:'+str(self.idir[0])+str(self.idir[1])+str(self.idir[2])), 'col7' : self.center.format('Sample')},
                    {'col1':self.center.format(np.round(self.ttB1,self.roundfit)), 'col2':self.center.format(np.round(self.dhkl,self.roundfit)), 'col3':self.center.format(np.round(self.en,self.roundfit)),'col4':self.center.format(str(self.hkl[0])+str(self.hkl[1])+str(self.hkl[2])), 'col5' : self.center.format(str(int(self.hkl_calc[0]))+str(int(self.hkl_calc[1]))+str(int(self.hkl_calc[2]))), 'col6':self.center.format('ndir:'+str(self.ndir[0])+str(self.ndir[1])+str(self.ndir[2])), 'col7' : self.center.format(self.sampleID+' '+self.sampleor)},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('Alpha'), 'col2':self.center.format('Beta'), 'col3':self.center.format('Psi'), 'col4':self.center.format('Tau'), 'col5':self.center.format('Qaz'), 'col6' : self.center.format('Naz'), 'col7' : self.center.format('Omega')},
                    {'col1':self.center.format(np.round(self.alphain,self.roundfit)), 'col2':self.center.format(np.round(self.betaout,self.roundfit)), 'col3':self.center.format(np.round(self.psipseudo,self.roundfit)), 'col4':self.center.format(np.round(self.taupseudo,self.roundfit)), 'col5':self.center.format(np.round(self.qaz,self.roundfit)), 'col6' : self.center.format(np.round(self.naz,self.roundfit)), 'col7' : self.center.format(np.round(self.omega,self.roundfit))},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('Del'), 'col2':self.center.format('Eta'), 'col3':self.center.format('Chi'), 'col4':self.center.format('Phi'), 'col5':self.center.format('Nu'), 'col6' : self.center.format('Mu'), 'col7' : self.center.format('--')},
                    {'col1':self.center.format(np.round(self.Del,self.roundfit)), 'col2':self.center.format(np.round(self.Eta,self.roundfit)), 'col3':self.center.format(np.round(self.Chi,self.roundfit)), 'col4':self.center.format(np.round(self.Phi,self.roundfit)), 'col5':self.center.format(np.round(self.Nu,self.roundfit)), 'col6' : self.center.format(np.round(self.Mu,self.roundfit)), 'col7' : self.center.format('--')},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space}
                    ]
        
            fmt = [
                    ('', 'col1',   self.space),
                    ('', 'col2',   self.space),
                    ('', 'col3',   self.space),
                    ('', 'col4',   self.space),
                    ('', 'col5',   self.space),
                    ('', 'col6',   self.space),
                    ('', 'col7',   self.space)
                    
                   ]
            
            return TablePrinter(fmt, ul=self.marker)(data)  
         
            
     
        
     
          
    
    def __call__(self, *args, **kwargs):
        """
        wrapper function for motor_angles(...)
        """
        return self.motor_angles(*args, **kwargs)
    
    def scan_generator(self, hkli, hklf, points):
        
        ini = np.array(hkli)
        fin = np.array(hklf)
        scanlist = np.linspace(hkli,hklf,points)
        return scanlist        
    
    def motor_angles(self, *args, **kwargs):
        
        self.isscan = False

        self.sampleID = self.samp.name
        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg

        
        self.qconv = xu.experiment.QConversion(['y+', 'x-', 'z+', 'x-'], ['y+', 'x-'], [0, 0, 1]) # Sirius coordinate axes system
        
        
        # qconv = xu.experiment.QConversion(['x+', 'z-', 'y+', 'z-'], ['x+', 'z-'], [0, 1, 0]) # Sirius coordinate axes system
        
        self.hrxrd = xu.HXRD(self.samp.Q(self.idir), self.samp.Q(self.ndir), en = self.en, qconv= self.qconv, sampleor = self.sampleor)
        
        self.Q_material = self.samp.Q(self.hkl)


        self.Q_lab = self.hrxrd.Transform(self.Q_material)
      
       
        self.dhkl = self.samp.planeDistance(self.hkl)
        tilt = xu.math.vector.VecAngle(self.hkl, self.samp.Q(self.ndir), deg=True)   
        
        # print(np.round(self.preangs,3))
        self.bounds = (self.Mu_bound, self.Eta_bound, self.Chi_bound, 
                        self.Phi_bound, self.Nu_bound, self.Del_bound)
    
        if 'sv' in kwargs.keys():
            self.start = kwargs['sv']
            # print(self.start)
        else:
            self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
            self.start = (0,0,0,0,0,self.preangs[3])
        
           
        self.errflag = 0
        self.trythis = [i for i in ['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'] if i not in self.fix and i not in self.posrestrict]
        pseudoconst = Control.pseudoAngleConst

        
      
        if len(self.constrain) != 0:

            while True:
       
         
                if len(self.constrain) == 1:
                    
                    if self.errflag == 0:
                        
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])}]
                        
                    elif self.errflag == 1:
                        break
                     
                elif len(self.constrain) == 2:
                  
                    if self.errflag == 0:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])}]
                                   
                    
                    if self.errflag == 1:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])}]
                    
                    if self.errflag == 2:
                        
                        break
                
                elif len(self.constrain) == 3:
        
                    
                    if self.errflag == 0:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[2][0], self.constrain[2][1])}]
                        
                    elif self.errflag == 1:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[2][0], self.constrain[2][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])}]
                    
                    elif self.errflag == 2:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[2][0], self.constrain[2][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])}]
                    
                    elif self.errflag == 3:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[2][0], self.constrain[2][1])}]
                    
                    elif self.errflag == 4:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[2][0], self.constrain[2][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])}]
                    
                    elif self.errflag == 5:
                    
                        restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[2][0], self.constrain[2][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[0][0], self.constrain[0][1])},
                                    {'type':'eq', 'fun': lambda a: pseudoconst(a, self.constrain[1][0], self.constrain[1][1])}]
                    
                    elif self.errflag == 6:
                        break
                
                if self.errflag == 0:
                 
                    if not None in self.posrestrict: 
                        # print('taaqui')
                        for i in self.posrestrict:
                         
                            restrict.insert(0,{'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i[0], i[1])})
                            
                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict)
                
                if qerror > 1e-5:
                    dinerror = 10
                    for i in self.trythis:
                        
                        restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict)
                        # print(i,qerror)
                        # print(i)
                        
                        if qerror < 1e-5:
                            break
                        restrict.pop()
                 
                if qerror > 1e-5:
                    self.errflag +=1
                else:
                    break
                
        else:
                restrict = []    
                if not None in self.posrestrict: 
                    for i in self.posrestrict:
                        restrict.insert(0,{'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i[0], i[1])})
                    ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict)
                    if qerror > 1e-5:
                        
                        for i in self.trythis:
                    
                            restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                            ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict)
                            
                            if qerror < 1e-5:
                                break
                            restrict.pop()
                    
                else:
                    
                    ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start)
                    if qerror > 1e-5:
                        
                        for i in self.trythis:
                    
                            restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                            ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict)
                            # print(i,qerror)
                            if qerror < 1e-5:
                                break
                            restrict.pop()
                
                

            

        
  
        self.qerror = qerror
        self.hkl_calc = np.round(self.hrxrd.Ang2HKL(*ang,mat=self.samp),5)
        # print(self.hkl_calc)
        
        self.Mu, self.Eta, self.Chi, self.Phi = (ang[0], ang[1], ang[2], ang[3])
        self.Nu, self.Del = (ang[4], ang[5])
        
        
        ## Matrices from 4S+2D angles, H. You, JAC, 1999, 32, 614-23
        #
        PHI = MAT([[np.cos(rad(self.Phi)),    np.sin(rad(self.Phi)),   0],
                  [-np.sin(rad(self.Phi)),  np.cos(rad(self.Phi)),     0],
                  [0,                         0,             1]])
        
        CHI = MAT([[np.cos(rad(self.Chi)),    0,           np.sin(rad(self.Chi))],
                  [0,                       1,                   0],
                  [-np.sin(rad(self.Chi)),    0,           np.cos(rad(self.Chi))]])
        
        ETA = MAT([[np.cos(rad(self.Eta)),    np.sin(rad(self.Eta)),   0],
                   [-np.sin(rad(self.Eta)),   np.cos(rad(self.Eta)),   0],
                   [0,                         0,           1]])
        
        MU = MAT([[1,                       0,                      0],
                  [0,            np.cos(rad(self.Mu)),    -np.sin(rad(self.Mu))],
                  [0,            np.sin(rad(self.Mu)),    np.cos(rad(self.Mu))]])
        
        DEL = MAT([[np.cos(rad(self.Del)),    np.sin(rad(self.Del)),   0],
                   [-np.sin(rad(self.Del)),   np.cos(rad(self.Del)),   0],
                   [0,                       0,              1]])
        
        NU = MAT([[1,                    0,                         0],
                  [0,            np.cos(rad(self.Nu)),    -np.sin(rad(self.Nu))],
                  [0,            np.sin(rad(self.Nu)),    np.cos(rad(self.Nu))]])
        
        Z = MU.dot(ETA).dot(CHI).dot(PHI)
        nz = Z.dot([0,0,1])
        ttB1 = deg(np.arccos(np.cos(rad(self.Nu)) * np.cos(rad(self.Del))))
        tB1 = ttB1/2
        
        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))
        
        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
        upsipseudo = deg(np.arctan(np.tan(rad(self.Del))/np.sin(rad(self.Nu))))
        qaz = upsipseudo
        # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))
        
        phipseudo = deg(np.arctan((nz.dot([1,0,0]))/(nz.dot([0,0,1]))))
        naz = phipseudo
        
        arg1 = np.cos(rad(alphain))*np.cos(rad(tB1))*np.cos(rad(phipseudo-upsipseudo))+np.sin(rad(alphain))*np.sin(rad(tB1))
        if arg1 >1:
            arg1 = 0.999999999999999999999
        taupseudo = deg(np.arccos(arg1))
        
        arg2 = (np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1)))
        if arg2 >1:
            arg2 = 0.999999999999999999999
        
        psipseudo = deg(np.arccos(arg2))
        
        # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))
        # print(arg3)
        # if arg3 >1:
        #     arg3 = 0.999999999999999999999
        # elif arg3 < -1:
        #     arg3 = -0.99999999999999999999
        betaout = deg(np.arcsin(arg3))
        
        arg4 = (np.sin(rad(self.Eta))*np.sin(rad(upsipseudo))+np.sin(rad(self.Mu))*np.cos(rad(self.Eta))*np.cos(rad(upsipseudo)))*np.cos(rad(tB1))-np.cos(rad(self.Mu))*np.cos(rad(self.Eta))*np.sin(rad(tB1))
        if arg4 >1:
         arg4 = 0.999999999999999999999
        omega = deg(np.arcsin(arg4))
        
      
        self.ttB1 = ttB1
        self.tB1 = ttB1/2
        self.alphain = alphain
        self.qaz = qaz
        self.naz = naz
        self.taupseudo = taupseudo
        self.psipseudo = psipseudo
        self.betaout = betaout
        self.omega = omega
        

  
        return [self.Mu, self.Eta, self.Chi, self.Phi, self.Nu, self.Del, self.ttB1, self.tB1, self.alphain, self.qaz, self.naz, self.taupseudo, self.psipseudo, self.betaout, self.omega, "{0:.2e}".format(self.qerror)], [self.fcsv(self.Mu), self.fcsv(self.Eta), self.fcsv(self.Chi), self.fcsv(self.Phi), self.fcsv(self.Nu), self.fcsv(self.Del), self.fcsv(self.ttB1), self.fcsv(self.tB1), self.fcsv(self.alphain), self.fcsv(self.qaz), self.fcsv(self.naz), self.fcsv(self.taupseudo), self.fcsv(self.psipseudo), self.fcsv(self.betaout), self.fcsv(self.omega), [self.fcsv(self.hkl_calc[0]), self.fcsv(self.hkl_calc[1]), self.fcsv(self.hkl_calc[2])], "{0:.2e}".format(self.qerror)] 
                                                                                                                                                                                                                                                                                                                 
    def scan(self, hkli, hklf, points, diflimit = 0.1, path = '/home/hugo/Documentos/CNPEM/scans/', name = 'testscan.txt', sep = ','):
        
        scl = Control.scan_generator(self, hkli, hklf, points)
        angslist = list()
        self.hkl = scl[0]
        a,b = Control.motor_angles(self)
        sv = a[:6]
    
        for i in tqdm(scl):
            self.hkl = i
            a,b = Control.motor_angles(self, sv=sv)
            angslist.append(b)
            teste = np.abs(np.array(a[:6]) - np.array(sv))
            if np.max(teste) > diflimit:
                raise (" Exceded limit of difractometer angles change")
           
            if float(a[-1]) > 1e-5:
                raise('qerror is too big, process failed')
            
            sv = a[:6]

        
        self.isscan = True

     
        self.formscantxt = pd.DataFrame(angslist, columns=['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', '2\u03B8', '\u03B8', 'alpha', 'qaz', 'naz',
                                                                                             'tau', 'psi', 'beta', 'omega',"HKL Calc", 'Error'])  

        self.formscan = self.formscantxt[['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', 'Error']]
        self.formscantxt.to_csv(path+name, sep=sep)
        
        pd.options.display.max_rows = None
        pd.options.display.max_columns = 0
     

                
    


    