#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import xrayutilities as xu
import numpy as np
import pandas as pd
from tqdm import tqdm
import sys
from numpy import linalg as LA
import os
import dafutilities as du




PI = np.pi
MAT = np.array
rad = np.deg2rad
deg = np.rad2deg












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
        self.centshow = "{:^" + str(16 - 2) + "}"
        
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
        
        self.nref = (0,0,1)
        self.idir = (0,0,1)
        self.ndir = (1,1,0)
        self.sampleor = 'x+'
        self.en = 8000
        self.lam = xu.en2lam(self.en)
        self.posrestrict = ()
        self.negrestrict = ()
        self.fcsv = '{0:.4f}'.format
        self.U = np.identity(3)
        # self.qconv = xu.experiment.QConversion(['y+', 'x-', 'z+', 'x-'], ['y+', 'x-'], [0, 0, 1]) # Sirius coordinate axes system
        self.qconv = xu.experiment.QConversion(['x+', 'z-', 'y+', 'z-'], ['x+', 'z-'], [0, 1, 0]) # Coordenada YOU 1999
    
    def show(self, sh):
        
        dprint = {'x' : '--', 'Mu' : self.Mu_bound, 'Eta' : self.Eta_bound, 'Chi' : self.Chi_bound,
                      'Phi' : self.Phi_bound, 'Nu' : self.Nu_bound, 'Del' : self.Del_bound}
            
        lb = lambda x: "{:.5f}".format(float(x))    

        
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
        
        fmt = [ 
                    ('', 'ident',   3),
                    ('', 'col1',   14),
                    ('', 'col2',   14),
                    ('', 'col3',   14),
                    ('', 'col4',   14),
                    ('', 'col5',   14),
                    ('', 'col6',   14),
              
                    
                   ]
        
        
        if sh == 'mode':            
            
            data = [{'ident':'','col1':self.centshow.format('MODE'), 'col2':self.centshow.format(self.setup[0]), 'col3':self.centshow.format(self.setup[1]), 'col4':self.centshow.format(self.setup[2]), 'col5':self.centshow.format(self.setup[3]), 'col6' : self.centshow.format(self.setup[4])},
                    {'ident':'','col1':self.centshow.format(str(self.col1)+str(self.col2)+str(self.col3)+str(self.col4)+str(self.col5)), 'col2':self.centshow.format(self.forprint[0][1]), 'col3':self.centshow.format(self.forprint[1][1]), 'col4':self.centshow.format(self.forprint[2][1]), 'col5':self.centshow.format(self.forprint[3][1]), 'col6' : self.centshow.format(self.forprint[4][1])},
                        ]
                   
            
            return TablePrinter(fmt, ul='')(data)  
    
        
        if sh == 'expt':
        
            data = [{'col1':self.centshow.format('Material'), 'col2':self.centshow.format('WaveLength (\u212B)'), 'col3':self.centshow.format('Energy (keV)'), 'col4':self.centshow.format('Incidence Dir'), 'col5' : self.centshow.format('Normal Dir'), 'col6':self.centshow.format('Reference Dir')},
                    {'col1':self.centshow.format(self.samp.name), 'col2':self.centshow.format(lb(str(self.lam))), 'col3':self.centshow.format(str(lb(self.en/1000))),'col4':self.centshow.format(str(self.idir[0]) +' '+ str(self.idir[1]) +' ' + str(self.idir[2])), 'col5' : self.centshow.format(str(self.ndir[0]) + ' ' + str(self.ndir[1]) + ' ' +str(self.ndir[2])), 'col6': self.centshow.format(str(self.nref[0]) + ' ' + str(self.nref[1]) + ' ' +str(self.nref[2]))}
                   ]
            return TablePrinter(fmt, ul='')(data)  
    
    def set_hkl(self, HKL):
        
        self.hkl = HKL
    
    def set_material(self, sample, *args):
        
        materiais = {'Si':xu.materials.Si, 'Al' : xu.materials.Al, 'Co' : xu.materials.Co,
                     'Cu' : xu.materials.Cu, 'Cr' : xu.materials.Cr, 'Fe' : xu.materials.Fe, 
                     'Ge' : xu.materials.Ge, 'MgO' : xu.materials.MgO, 'Sn' : xu.materials.Sn,
                     'LaB6' : xu.materials.LaB6, 'Al2O3' : xu.materials.Al2O3}
                     
        if sample in materiais.keys():
            self.samp = materiais[sample]
        
        else:
            self.samp = xu.materials.Crystal(str(sample),xu.materials.SGLattice(1, args[0], args[1], args[2], args[3], args[4], args[5]))

    
    def uphi(self, Mu, Eta, Chi, Phi, Nu, Del):
        
        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg
        
        
        
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
        
        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        theta = ttB1/2
        
        invphi = LA.inv(PHI)
        invchi = LA.inv(CHI)
        inveta = LA.inv(ETA)
        invmu = LA.inv(MU)
        
        Ql1 = MAT([np.sin(rad(Del)),
                   np.cos(rad(Del))*np.cos(rad(Nu)) - 1,
                   np.cos(rad(Del))*np.sin(rad(Nu))])
        
        Ql = Ql1* (1/(2*np.sin(rad(theta))))
        
        # uphi = invphi.dot(invchi).dot(inveta).dot(invmu).dot(Ql)
        uphi = PHI.T.dot(CHI.T).dot(ETA.T).dot(MU.T).dot(Ql)
        return uphi, theta
    
    def calc_U_2HKL(self, h1, angh1, h2, angh2):
        
        PI = np.pi
        MAT = np.array
        rad = np.deg2rad
        deg = np.rad2deg
        
        u1p, th1 = self.uphi(*angh1)
        u2p, th2 = self.uphi(*angh2)
        
        
        h1c = self.samp.B.dot(h1)
        h2c = self.samp.B.dot(h2)
      
        # Create modified unit vectors t1, t2 and t3 in crystal and phi systems
      
        t1c = h1c
        t3c = np.cross(h1c, h2c)
        t2c = np.cross(t3c, t1c)
     
        t1p = u1p  # FIXED from h1c 9July08
        t3p = np.cross(u1p, u2p)
        t2p = np.cross(t3p, t1p)
        # print(t2p)
        # ...and nornmalise and check that the reflections used are appropriate
        SMALL = 1e-4  # Taken from Vlieg's code
      
        def normalise(m):
            d = LA.norm(m)
            # if d < SMALL:
            #     raise DiffcalcException("Invalid UB reference data. Please check that the specified "
            #                               "reference reflections/orientations are not parallel.")
            return m / d
      
        t1c = normalise(t1c)
        t2c = normalise(t2c)
        t3c = normalise(t3c)
      
        t1p = normalise(t1p)
        t2p = normalise(t2p)
        t3p = normalise(t3p)
       
        Tc = MAT([t1c, t2c, t3c])
        Tp = MAT([t1p, t2p, t3p])
        TcI = LA.inv(Tc.T)
       
       
       
      
        U = Tp.T.dot(TcI)
        self.U = U
        self.UB = U.dot(self.samp.B)
        
        return U , self.UB
      
    def calc_U_3HKL(self, h1, angh1, h2, angh2, h3, angh3):
     
      PI = np.pi
      MAT = np.array
      rad = np.deg2rad
      deg = np.rad2deg  
        
      u1p, th1 = self.uphi(*angh1)
      u2p, th2 = self.uphi(*angh2)
      u3p, th3 = self.uphi(*angh3)
        
      h1p = (2*np.sin(rad(th1))/self.lam)*u1p
      h2p = (2*np.sin(rad(th2))/self.lam)*u2p
      h3p = (2*np.sin(rad(th3))/self.lam)*u3p
    
     
      H = MAT([h1, h2, h3]).T
      Hp = MAT([h1p, h2p, h3p]).T
      HI = LA.inv(H)
      UB = Hp.dot(HI)
      UB2p = UB*2*PI 
      
      GI = UB.T.dot(UB)
      G = LA.inv(GI)
      a1 = G[0,0]**0.5
      a2 = G[1,1]**0.5
      a3 = G[2,2]**0.5
      alpha1 = deg(np.arccos(G[1,2]/(a2*a3)))
      alpha2 = deg(np.arccos(G[0,2]/(a1*a3)))
      alpha3 = deg(np.arccos(G[0,1]/(a1*a2)))
      
      samp = xu.materials.Crystal('generic',xu.materials.SGLattice(1, a1, a2, a3, alpha1, alpha2, alpha3))
      
      U = UB2p.dot(LA.inv(samp.B))
      
      rparam = [a1, a2, a3, alpha1, alpha2, alpha3]
      
      self.U = U
      self.UB = UB2p
      
      self.calclp = rparam
      
      return U, UB2p, rparam    
    
    
    def set_constraints(self, *args, setineq = None, **kwargs):

        
        self.constrain = list()
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
            
            if 'qaz' in kwargs.keys() and 'qaz' in self.const:
                self.constrain.append(('qaz', kwargs['qaz']))
            
            if 'naz' in kwargs.keys() and 'naz' in self.const:
                self.constrain.append(('naz', kwargs['naz']))
            
            if 'alpha' in kwargs.keys() and 'alpha' in self.const:
                self.constrain.append(('alpha', kwargs['alpha']))
            
            if 'beta' in kwargs.keys() and 'beta' in self.const:
                self.constrain.append(('beta', kwargs['beta']))
            
            if 'psi' in kwargs.keys() and 'psi' in self.const:
                self.constrain.append(('psi', kwargs['psi']))
            
            if 'omega' in kwargs.keys() and 'omega' in self.const:
                self.constrain.append(('omega', kwargs['omega']))
            
            if 'aeqb' in self.const:
                self.constrain.append(('aeqb', '--'))
            
            if 'eta=del/2' in self.const:
                self.constrain.append(('eta=del/2', '--'))
            
            if 'mu=nu/2' in self.const:
                self.constrain.append(('mu=nu/2', '--'))
            
            
 
        
   
    
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
    
    def set_exp_conditions(self, idir = (0,0,1), ndir = (1,1,0), rdir = (0,0,1), sampleor = 'x+', en = 8000):
        
        self.idir = idir
        self.ndir = ndir
        self.nref = rdir
        self.sampleor = sampleor
         
        ENWL = en
       
        if ENWL > 50 :
              self.en = ENWL
              self.lam = xu.en2lam(en)
        else:
              self.lam = ENWL
              self.en = xu.lam2en(self.lam)
    
    
    def two_theta_max(self):
        
        if type(self.bounds[4]) == float:
            nub = self.bounds[4]
        else:
            nub = np.linspace(self.bounds[4][0], self.bounds[4][1], 1000)
        
        if type(self.bounds[5]) == float:
            delb = self.bounds[5]
        else:
            delb = np.linspace(self.bounds[5][0], self.bounds[5][1], 1000)
            
        delb, nub = np.meshgrid(delb, nub)
        R = np.cos(np.radians(delb))*np.cos(np.radians(nub))
        Z = np.arccos(R)
     
        return np.degrees(np.max(Z)), np.degrees(np.min(Z))      
   
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
             
            lb = lambda x: "{:.5f}".format(float(x))    
            
            data = [{'col1':self.center.format('MODE'), 'col2':self.center.format(self.setup[0]), 'col3':self.center.format(self.setup[1]), 'col4':self.center.format(self.setup[2]), 'col5':self.center.format(self.setup[3]), 'col6' : self.center.format(self.setup[4]), 'col7' : self.center.format('Error')},
                    {'col1':self.center.format(str(self.col1)+str(self.col2)+str(self.col3)+str(self.col4)+str(self.col5)), 'col2':self.center.format(self.forprint[0][1]), 'col3':self.center.format(self.forprint[1][1]), 'col4':self.center.format(self.forprint[2][1]), 'col5':self.center.format(self.forprint[3][1]), 'col6' : self.center.format(self.forprint[4][1]), 'col7' : self.center.format('%.3g' % self.qerror)},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('2Theta exp'), 'col2':self.center.format('Dhkl'), 'col3':self.center.format('Energy (keV)'), 'col4':self.center.format('H'), 'col5' : self.center.format('K'), 'col6':self.center.format('L'), 'col7' : self.center.format('Sample')},
                    {'col1':self.center.format(lb(self.ttB1)), 'col2':self.center.format(lb(self.dhkl)), 'col3':self.center.format(lb(self.en/1000)),'col4':self.center.format(str(self.hkl_calc[0])), 'col5' : self.center.format(str(self.hkl_calc[1])), 'col6':self.center.format(str(self.hkl_calc[2])), 'col7' : self.center.format(self.sampleID+' '+self.sampleor)},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('Alpha'), 'col2':self.center.format('Beta'), 'col3':self.center.format('Psi'), 'col4':self.center.format('Tau'), 'col5':self.center.format('Qaz'), 'col6' : self.center.format('Naz'), 'col7' : self.center.format('Omega')},
                    {'col1':self.center.format(lb(self.alphain)), 'col2':self.center.format(lb(self.betaout)), 'col3':self.center.format(lb(self.psipseudo)), 'col4':self.center.format(lb(self.taupseudo)), 'col5':self.center.format(lb(self.qaz)), 'col6' : self.center.format(lb(self.naz)), 'col7' : self.center.format(lb(self.omega))},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('Del'), 'col2':self.center.format('Eta'), 'col3':self.center.format('Chi'), 'col4':self.center.format('Phi'), 'col5':self.center.format('Nu'), 'col6' : self.center.format('Mu'), 'col7' : self.center.format('--')},
                    {'col1':self.center.format(lb(self.Del)), 'col2':self.center.format(lb(self.Eta)), 'col3':self.center.format(lb(self.Chi)), 'col4':self.center.format(lb(self.Phi)), 'col5':self.center.format(lb(self.Nu)), 'col6' : self.center.format(lb(self.Mu)), 'col7' : self.center.format('--')},
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
    
    def set_U(self, U):
      
        self.U = U
     
    def calc_from_angs(self, Mu,Eta,Chi,Phi,Nu,Del):
        
        
        self.hrxrd = xu.HXRD(self.idir, self.ndir, en = self.en, qconv= self.qconv, sampleor = self.sampleor)
        hkl = self.hrxrd.Ang2HKL(Mu,Eta,Chi,Phi,Nu,Del, mat=self.samp, en = self.en, U = self.U)
        self.hkl = hkl
        return hkl
     
    def export_angles(self):
        
        return [self.Mu, self.Eta, self.Chi, self.Phi, self.Nu, self.Del, self.ttB1, self.tB1, self.alphain, self.qaz, self.naz, self.taupseudo, self.psipseudo, self.betaout, self.omega, self.hkl_calc, "{0:.2e}".format(self.qerror)]
    
    
    def calc_pseudo(self, Mu, Eta, Chi, Phi, Nu, Del):
        
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
        # n = [0,0,1]
        n = self.nref
        nc = self.samp.B.dot(n)
        nphi = self.U.dot(nc)
        nphihat = nphi/LA.norm(nphi)
        nz = Z.dot(nphihat)
        
        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        tB1 = ttB1/2
        
        
        
        A1 = (self.samp.a1)
        A2 = (self.samp.a2)
        A3 = (self.samp.a3)
        
        vcell = A1.dot(np.cross(A2,A3))
        
        B1 = np.cross(self.samp.a2,self.samp.a3)/vcell
        B2 = np.cross(self.samp.a3,self.samp.a1)/vcell
        B3 = np.cross(self.samp.a1,self.samp.a2)/vcell
        
        q = self.samp.Q(self.hkl) # eq (1)
        normQ = LA.norm(q)
        Qhat = q/normQ
        
        
        # n = n[0]*B1 + n[1]*B2 + n[2]*B3
        # normn = LA.norm(n)
        
        # nhat = n/normn
    
        
        taupseudo = deg(np.arccos(Qhat.dot(nphihat)))    
        
        
        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))
        
        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
        
        
        upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu))))
        qaz = upsipseudo
        # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))
        
        phipseudo = deg(np.arctan((nz.dot([1,0,0]))/(nz.dot([0,0,1]))))
        naz = phipseudo
        
        # arg1 = np.cos(rad(alphain))*np.cos(rad(tB1))*np.cos(rad(phipseudo-upsipseudo))+np.sin(rad(alphain))*np.sin(rad(tB1))
        # if arg1 >1:
        #     arg1 = 0.999999999999999999999
        # elif arg1 < -1:
        #     arg3 = -0.99999999999999999999
       
        
        arg2 = (np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1)))
        if arg2 >1:
            arg2 = 0.999999999999999999999
        elif arg2 < -1:
            arg2 = -0.99999999999999999999
   
        
        psipseudo = deg(np.arccos(arg2))
        
        arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))
        # print(arg3)
        if arg3 >1:
            arg3 = 0.99999999999999999999
        elif arg3 < -1:
            arg3 = -0.9999999999999999999
        # print(arg3)
        betaout = deg(np.arcsin(arg3))
        
        arg4 = (np.sin(rad(Eta))*np.sin(rad(upsipseudo))+np.sin(rad(Mu))*np.cos(rad(Eta))*np.cos(rad(upsipseudo)))*np.cos(rad(tB1))-np.cos(rad(Mu))*np.cos(rad(Eta))*np.sin(rad(tB1))
        if arg4 >1:
          arg4 = 0.999999999999999999999
        elif  arg4 < -1:
            arg3 = -0.999999999999999999
        omega = deg(np.arcsin(arg4))
        
        return (alphain, qaz, naz, taupseudo, psipseudo, betaout, omega)
    
    def pseudoAngleConst(self, angles, pseudo_angle, fix_angle):
    
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
        # n = [0,0,1]
        n = self.nref
        nc = self.samp.B.dot(n)
        nphi = self.U.dot(nc)
        nphihat = nphi/LA.norm(nphi)

        nz = Z.dot(nphihat)
        
        A1 = (self.samp.a1)
        A2 = (self.samp.a2)
        A3 = (self.samp.a3)
        
        vcell = A1.dot(np.cross(A2,A3))
        
        B1 = np.cross(self.samp.a2,self.samp.a3)/vcell
        B2 = np.cross(self.samp.a3,self.samp.a1)/vcell
        B3 = np.cross(self.samp.a1,self.samp.a2)/vcell
        
        q = self.samp.Q(self.hkl) # eq (1)
        normQ = LA.norm(q)
        Qhat = q/normQ
        
        
        # n = n[0]*B1 + n[1]*B2 + n[2]*B3
        # normn = LA.norm(n)
        
        # nhat = n/normn
    
        
        # taupseudo = deg(np.arccos(Qhat.dot(nhat)))
        taupseudo = deg(np.arccos(Qhat.dot(nphihat)))    

        
        
        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        tB1 = ttB1/2
        
        
        
        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))
        
        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
        # print(f"tandel = {np.tan(rad(Del))}")
        # print(f'sinNu = {np.sin(rad(Nu))}')
        
        upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu))))
        qaz = upsipseudo
        # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))
        
        phipseudo = deg(np.arctan((nz.dot([1,0,0]))/(nz.dot([0,0,1]))))
        naz = phipseudo
        
        # arg1 = np.cos(rad(alphain))*np.cos(rad(tB1))*np.cos(rad(phipseudo-upsipseudo))+np.sin(rad(alphain))*np.sin(rad(tB1))
        # if arg1 >1:
        #     arg1 = 0.999999999999999999999
        # elif arg1 < -1:
        #     arg3 = -0.99999999999999999999
        # taupseudo = deg(np.arccos(arg1))
        
     
        
        arg2 = (np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1)))
        if arg2 >1:
            arg2 = 0.999999999999999999999
        elif arg2 < -1:
            arg2 = -0.99999999999999999999
   
        
        psipseudo = deg(np.arccos(arg2))
        
        arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))
        # print(arg3)
        if arg3 >1:
            arg3 = 0.99999999999999999999
        elif arg3 < -1:
            arg3 = -0.9999999999999999999
        # # print(arg3)
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
    
    
    def motor_angles(self, *args, qvec = False, calc = True, **kwargs):
        
        self.isscan = False

        self.sampleID = self.samp.name


        self.hrxrd = xu.HXRD(self.idir, self.ndir, en = self.en, qconv= self.qconv, sampleor = self.sampleor)
        
      
        self.bounds = (self.Mu_bound, self.Eta_bound, self.Chi_bound, 
                        self.Phi_bound, self.Nu_bound, self.Del_bound)
        if calc:
            if qvec is not False:
                self.Q_lab = qvec
                
                
            else:
                self.Q_material = self.samp.Q(self.hkl)
                
                self.Q_lab = self.hrxrd.Transform(self.Q_material)
        
          
           
            self.dhkl = self.samp.planeDistance(self.hkl)
            tilt = xu.math.vector.VecAngle(self.hkl, self.samp.Q(self.ndir), deg=True)   
            
       
        
            if 'sv' in kwargs.keys():
                self.start = kwargs['sv']
                # print(self.start)
            # else:
            #     self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
            #     self.start = (0,0,0,0,0,self.preangs[3])
            
            
            self.errflag = 0
            self.trythis = [i for i in ['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del'] if i not in self.fix and i not in self.posrestrict]
            pseudoconst = Control.pseudoAngleConst
    
            
          
            if len(self.constrain) != 0:
    
                while True:
           
             
                    if len(self.constrain) == 1:
                        
                        if self.errflag == 0:
                            
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])}]
                            
                        elif self.errflag == 1:
                            break
                         
                    elif len(self.constrain) == 2:
                      
                        if self.errflag == 0:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])}]
                                       
                        
                        if self.errflag == 1:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])}]
                        
                        if self.errflag == 2:
                            
                            break
                    
                    elif len(self.constrain) == 3:
            
                        
                        if self.errflag == 0:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[2][0], self.constrain[2][1])}]
                            
                        elif self.errflag == 1:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[2][0], self.constrain[2][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])}]
                        
                        elif self.errflag == 2:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[2][0], self.constrain[2][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])}]
                        
                        elif self.errflag == 3:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[2][0], self.constrain[2][1])}]
                        
                        elif self.errflag == 4:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[2][0], self.constrain[2][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])}]
                        
                        elif self.errflag == 5:
                        
                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[2][0], self.constrain[2][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[0][0], self.constrain[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.constrain[1][0], self.constrain[1][1])}]
                        
                        elif self.errflag == 6:
                            break
                    
                    if self.errflag == 0:
                     
                        if not None in self.posrestrict: 
                            for i in self.posrestrict:
                             
                                restrict.insert(0,{'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i[0], i[1])})         
                                   
                    ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat = self.U)
                    # print(self.fix)
                    if qerror > 1e-5:
                            if 'Del' not in self.fix and 'Eta' not in self.fix:
                                self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                                self.start = (0,0,0,0,0,self.preangs[3])
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                            else:
                                self.sv = [0,0,0,0,0,0]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                
                            # if qerror > 1e-5:
                            #     dinerror = 10
                            #     for i in self.trythis:
                                    
                            #         restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                            #         ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                            
                            #         if qerror < 1e-5:
                            #             break
                            #         restrict.pop()
                         
                    if qerror > 1e-5:
                        self.errflag +=1
                    else:
                        break
                    
            else:
                    restrict = []    
                    if not None in self.posrestrict: 
                        for i in self.posrestrict:
                            restrict.insert(0,{'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i[0], i[1])})
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat = self.U)
                        if qerror > 1e-5:
                            if 'Del' not in self.fix and 'Eta' not in self.fix:
                                self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                                self.start = (0,0,0,0,0,self.preangs[3])
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                            else:
                                self.sv = [0,0,0,0,0,0]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                
                            # if qerror > 1e-5:
                            #     dinerror = 10
                            #     for i in self.trythis:
                                    
                            #         restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                            #         ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                            
                            #         if qerror < 1e-5:
                            #             break
                            #         restrict.pop()
                            # for i in self.trythis:
                        
                            #     restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                            #     ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat = self.U)
                                
                            #     if qerror < 1e-5:
                            #         break
                            #     restrict.pop()
                        
                    else:
                        
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat = self.U)
                        if qerror > 1e-5:
                            if 'Del' not in self.fix and 'Eta' not in self.fix:
                                self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                                self.start = (0,0,0,0,0,self.preangs[3])
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                            else:
                                self.sv = [0,0,0,0,0,0]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                
                            # if qerror > 1e-5:
                            #     dinerror = 10
                            #     for i in self.trythis:
                                    
                            #         restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                            #         ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                            
                            #         if qerror < 1e-5:
                            #             break
                            #         restrict.pop()
                            
                            
                            # for i in self.trythis:
                        
                            #     restrict.append({'type': 'ineq', 'fun': lambda a:  pseudoconst(a, i, 0.3)})
                            #     ang, qerror, errcode = xu.Q2AncondagFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat = self.U)
                            #     # print(i,qerror)
                            #     if qerror < 1e-5:
                            #         break
                            #     restrict.pop()
                    
                    
    
                
    
                    n = [0,0,1]
      
            self.qerror = qerror
            self.hkl_calc = np.round(self.hrxrd.Ang2HKL(*ang,mat=self.samp, en = self.en, U=self.U),5)
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
    
            # n = [0,0,1]
            n = self.nref
            nc = self.samp.B.dot(n)
            nphi = self.U.dot(nc)
            nphihat = nphi/LA.norm(nphi)
            # print(nphihat)
            nz = Z.dot(nphihat)
            
            A1 = (self.samp.a1)
            A2 = (self.samp.a2)
            A3 = (self.samp.a3)
            
            vcell = A1.dot(np.cross(A2,A3))
            
            B1 = np.cross(self.samp.a2,self.samp.a3)/vcell
            B2 = np.cross(self.samp.a3,self.samp.a1)/vcell
            B3 = np.cross(self.samp.a1,self.samp.a2)/vcell
            
            q = self.samp.Q(self.hkl) # eq (1)
            normQ = LA.norm(q)
            Qhat = q/normQ
            
    
            # n = n[0]*B1 + n[1]*B2 + n[2]*B3
            # normn = LA.norm(n)
            
            # nhat = n/normn
        
            
            taupseudo = deg(np.arccos(Qhat.dot(nphihat)))    
            
            
            
            ttB1 = deg(np.arccos(np.cos(rad(self.Nu)) * np.cos(rad(self.Del))))
            tB1 = ttB1/2
            
            alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))
            
            # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
            upsipseudo = deg(np.arctan(np.tan(rad(self.Del))/np.sin(rad(self.Nu))))
            qaz = upsipseudo
            # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))
            
            phipseudo = deg(np.arctan((nz.dot([1,0,0]))/(nz.dot([0,0,1]))))
            naz = phipseudo
            
            # arg1 = np.cos(rad(alphain))*np.cos(rad(tB1))*np.cos(rad(phipseudo-upsipseudo))+np.sin(rad(alphain))*np.sin(rad(tB1))
            # if arg1 >1:
            #     arg1 = 0.99999999999999999999
            # taupseudo = deg(np.arccos(arg1))
          
            
            arg2 = (np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1)))
            if arg2 >1:
                arg2 = 0.999999999999999999999
            elif arg2 < -1:
                arg2 = -0.99999999999999999999
            # print(arg2)
            psipseudo = deg(np.arccos(arg2))
            
            arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
            arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))
            # print(arg3)
            if arg3 >1:
                arg3 = 0.999999999999999999999
            elif arg3 < -1:
                arg3 = -0.99999999999999999999
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
                                       

                                                                                                                                                  
    def scan(self, hkli, hklf, points, diflimit = 0.1, write = False, name = 'testscan.txt', sep = ',', startvalues = [0,0,0,0,0,0]):
        
        scl = Control.scan_generator(self, hkli, hklf, points)
        angslist = list()
        # self.hkl = scl[0]
        # a,b = self.motor_angles(self)qmax = 2 * k0 * math.sin(math.radians(ttmin/2.))
        # sv = a[:6]
        # initial = np.round(self.hrxrd.Ang2HKL(*startvalues,mat=self.samp, en = self.en, U=self.U),5)
        # print(initial)
        for i in tqdm(scl):
            self.hkl = i
            a,b = self.motor_angles(self, sv=startvalues)
            angslist.append(b)
            teste = np.abs(np.array(a[:6]) - np.array(startvalues))
            
            # print(np.max(teste))
         
            if np.max(teste) > diflimit and diflimit != 0:
                raise ("Exceded max limit of angles variation")
           
            if float(a[-1]) > 1e-5:
                raise('qerror is too big, process failed')
            
            startvalues = a[:6]
            
     
        
        self.isscan = True
     
        self.formscantxt = pd.DataFrame(angslist, columns=['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', '2\u03B8', '\u03B8', 'alpha', 'qaz', 'naz',
                                                                                             'tau', 'psi', 'beta', 'omega','HKL Calc', 'Error'])  

        self.formscan = self.formscantxt[['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', 'Error']]
        
        if write:
            self.formscantxt.to_csv(name, sep=sep)
        
        pd.options.display.max_rows = None
        pd.options.display.max_columns = 0
        

        
        
    def show_reciprocal_space_plane(self, ttmax=None, ttmin = None, maxqout=0.01, scalef=100, ax=None, color=None,
            show_Laue=True, show_legend=True, projection='perpendicular',
            label=None):
        """
        show a plot of the coplanar diffraction plane with peak positions for the
        respective material. the size of the spots is scaled with the strength of
        the structure factor
    
        Parameters
        ----------
        mat:        Crystal
            instance of Crystal for structure factor calculations
        exp:        Experiment
            instance of Experiment (needs to be HXRD, or FourC for onclick action
            to work correctly). defines the inplane and out of plane direction as
            well as the sample azimuth
        ttmax:      float, optional
            maximal 2Theta angle to consider, by default 180deg
        maxqout:    float, optional
            maximal out of plane q for plotted Bragg peaks as fraction of exp.k0
        scalef:     float, optional
            scale factor for the marker size
        ax:         matplotlib.Axes, optional
            matplotlib Axes to use for the plot, useful if multiple materials
            should be plotted in one plot
        color:      matplotlib color, optional
        show_Laue:  bool, optional
            flag to indicate if the Laue zones should be indicated
        show_legend:    bool, optional
            flag to indiate if a legend should be shown
        projection: 'perpendicular', 'polar', optional
            type of projection for Bragg peaks which do not fall into the
            diffraction plane. 'perpendicular' (default) uses only the inplane
            component in the scattering plane, whereas 'polar' uses the vectorial
            absolute value of the two inplane components. See also the 'maxqout'
            option.
        label:  None or str, optional
            label to be used for the legend. If 'None' the name of the material
            will be used.
    
        Returns
        -------
        Axes, plot_handle
        """
        import math
        import numpy
        exp = self.hrxrd
        mat = self.samp
        pi = np.pi
        EPSILON = 1e-7
        def import_matplotlib_pyplot(funcname='XU'):
            """
            lazy import function of matplotlib.pyplot
        
            Parameters
            ----------
            funcname :      str
                identification string of the calling function
        
            Returns
            -------
            flag :  bool
                the flag is True if the loading was successful and False otherwise.
            pyplot
                On success pyplot is the matplotlib.pyplot package.
            """
            try:
                from matplotlib import pyplot as plt

                # from .mpl_helper import SqrtAllowNegScale
                return True, plt
            except ImportError:# print(d['qvec'][m][ind['ind'][0]])
                if config.VERBOSITY >= config.INFO_LOW:
                    print("%s: Warning: plot functionality not available" % funcname)
                return False, None
        
        def get_peaks(mat, exp, ttmax):
            """
            Parameters
            ----------
            mat:        Crystal
                instance of Crystal for structure factor calculations
            exp:        Experiment
                instance of Experiment (likely HXRD, or FourC)
            tt_cutoff:  float
                maximal 2Theta angle to consider, by default 180deg
    
            Returns
            -------
            ndarray
                data array with columns for 'q', 'qvec', 'hkl', 'r' for the Bragg
                peaks
            """
           
            ttmax = 180
            # print(d['qvec'][m][ind['ind'][0]])
            
            # calculate maximal Bragg indices
            hma = int(math.ceil(xu.math.vector.VecNorm(mat.a1) * exp.k0 / pi *
                                math.sin(math.radians(ttmax / 2.))))
            hmi = -hma
            kma = int(math.ceil(xu.math.vector.VecNorm(mat.a2) * exp.k0 / pi *
                                math.sin(math.radians(ttmax / 2.))))
            kmi = -kma
            lma = int(math.ceil(xu.math.vector.VecNorm(mat.a3) * exp.k0 / pi *
                                math.sin(math.radians(ttmax / 2.))))
            lmi = -lma
    
            # calculate structure factors
            qmax = 2 * exp.k0 * math.sin(math.radians(ttmax/2.))
            hkl = numpy.mgrid[hma:hmi-1:-1,
                              kma:kmi-1:-1,
                              lma:lmi-1:-1].reshape(3, -1).T
            q = mat.Q(hkl)
            qnorm = xu.math.vector.VecNorm(q)
            m = qnorm < qmax
    
            data = numpy.zeros(numpy.sum(m), dtype=[('q', numpy.double),
                                                    ('qvec', numpy.ndarray),
                                                    ('r', numpy.double),
                                                    ('hkl', numpy.ndarray)])
            data['q'] = qnorm[m]
            data['qvec'] = list(exp.Transform(q[m]))
            rref = abs(mat.StructureFactor((0, 0, 0), exp.energy)) ** 2
            data['r'] = numpy.abs(mat.StructureFactorForQ(q[m], exp.energy)) ** 2
            data['r'] /= rref
            data['hkl'] = list(hkl[m])
    
            return data
    
        plot, plt = import_matplotlib_pyplot('XU.materials')
    
        if not plot:
            print('matplotlib needed for show_reciprocal_space_plane')
            return
    
        if ttmax is None:
            ttmax = 180
    
        d = get_peaks(mat, exp, ttmax)
        k0 = exp.k0
    
        if not ax:
            fig = plt.figure(figsize=(9, 5))
            ax = plt.subplot(111)
        else:
            fig = ax.get_figure()
            plt.sca(ax)
    
        plt.axis('scaled')
        ax.set_autoscaley_on(False)
        ax.set_autoscalex_on(False)
        plt.xlim(-2.05*k0, 2.05*k0)
        plt.ylim(-0.05*k0, 2.05*k0)
    
        if show_Laue:
            c = plt.matplotlib.patches.Circle((0, 0), 2*k0, facecolor='#FF9180',
                                              edgecolor='none')
            ax.add_patch(c)
            qmax = 2 * k0 * math.sin(math.radians(ttmax/2.))
            c = plt.matplotlib.patches.Circle((0, 0), qmax, facecolor='#FFFFFF',
                                              edgecolor='none')
            ax.add_patch(c)
            if ttmin:
                qmax = 2 * k0 * math.sin(math.radians(ttmin/2.))
                c = plt.matplotlib.patches.Circle((0, 0), qmax, facecolor='#FF9180',
                                                  edgecolor='none')
                ax.add_patch(c)
    
            c = plt.matplotlib.patches.Circle((0, 0), 2*k0, facecolor='none',
                                              edgecolor='0.5')
            ax.add_patch(c)
            c = plt.matplotlib.patches.Circle((k0, 0), k0, facecolor='none',
                                              edgecolor='0.5')
            ax.add_patch(c)
            c = plt.matplotlib.patches.Circle((-k0, 0), k0, facecolor='none',
                                              edgecolor='0.5')
            ax.add_patch(c)
            plt.hlines(0, -2*k0, 2*k0, color='0.5', lw=0.5)
            plt.vlines(0, -2*k0, 2*k0, color='0.5', lw=0.5)
    
        # generate mask for plotting
        m = numpy.zeros_like(d, dtype=numpy.bool)
        for i, (q, r) in enumerate(zip(d['qvec'], d['r'])):
            if (abs(q[0]) < maxqout*k0 and r > EPSILON):
                m[i] = True
    
        x = numpy.empty_like(d['r'][m])
        y = numpy.empty_like(d['r'][m])
        s = numpy.empty_like(d['r'][m])
        for i, (qv, r) in enumerate(zip(d['qvec'][m], d['r'][m])):
            if projection == 'perpendicular':
                x[i] = qv[1]
            else:
                x[i] = numpy.sign(qv[1])*numpy.sqrt(qv[0]**2 + qv[1]**2)
            y[i] = qv[2]
            s[i] = r*scalef
        label = label if label else mat.name
        h = plt.scatter(x, y, s=s, zorder=2, label=label)
        from matplotlib import pyplot as plt
        # plt.show(block=True)
        if color:
            h.set_color(color)
    
        plt.xlabel(r'$Q$ inplane ($\mathrm{\AA^{-1}}$)')
        plt.ylabel(r'$Q$ out of plane ($\mathrm{\AA^{-1}}$)')
    
        if show_legend:
            if len(fig.legends) == 1:
                fig.legends[0].remove()
            fig.legend(*ax.get_legend_handles_labels(), loc='upper right')
        plt.tight_layout()
    
        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
    
        def update_annot(ind):
            pos = h.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            text = "{}\n{}".format(mat.name,
                                   str(d['hkl'][m][ind['ind'][0]]))
            
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor(h.get_facecolor()[0])
            annot.get_bbox_patch().set_alpha(0.2)
    
        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = h.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()
    
        def click(event):
            if event.inaxes == ax:
                cont, ind = h.contains(event)
                
                if cont:
                    popts = numpy.get_printoptions()
                    numpy.set_printoptions(precision=4, suppress=True)
                    # print(d['qvec'][m][ind['ind'][0]])
                    dict_args = du.dict_conv()
                    startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]
                    
                    hkl = (d['hkl'][m][ind['ind'][0]])
                    self.hkl = hkl
               
                    ang = Control.motor_angles(self, qvec = d['qvec'][m][ind['ind'][0]], sv = startvalue)
                    angles = [ang[0][0], ang[0][1], ang[0][2], ang[0][3], ang[0][4], ang[0][5], float(ang[0][-1])]
                    
                    text = "{}\nhkl: {}\nangles: {}".format(
                        mat.name, str(d['hkl'][m][ind['ind'][0]]), str(angles))
                    numpy.set_printoptions(**popts)
                    # print(text)
                    
                    
                    # print(angles)
                    pseudo = self.calc_pseudo(*angles[:6])
                    exp_dict = {'Mu':angles[0], 'Eta':angles[1], 'Chi':angles[2], 'Phi':angles[3], 'Nu':angles[4], 'Del':angles[5],'alpha':pseudo[0],
                                'qaz':pseudo[1], 'naz':pseudo[2], 'tau':pseudo[3], 'psi':pseudo[4], 'beta':pseudo[5], 'omega':pseudo[6], 'hklnow':list(self.hkl_calc)}
                    if angles[6] < 1e-4:
                        with open('.Experiment', 'r+') as exp:
     
                            lines = exp.readlines()
                        
                        
                         
                        
                            for i, line in enumerate(lines):
                                for j,k in exp_dict.items():
                                    
                        
                         
                        
                                    if line.startswith(str(j)):
                                            lines[i] = str(j)+'='+str(k)+'\n'
                                  
                                exp.seek(0)
                    
                  
        
            
                            for line in lines:
                                exp.write(line)
                        
                        os.system("daf.wh")
                    else:
                        print('Can\'t find the reflection')
                    
        fig.canvas.mpl_connect("motion_notify_event", hover)
        fig.canvas.mpl_connect("button_press_event", click)
        plt.show(block=True)
        return ax, h
    

