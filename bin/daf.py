#!/usr/bin/env python3

import sys
import subprocess
import xrayutilities as xu
import numpy as np
import pandas as pd
from tqdm import tqdm
from numpy import linalg as LA
from math import pi, sqrt, sin, cos, atan2, acos
import os

from reciprocal_map import ReciprocalMapWindow


PI = np.pi
MAT = np.array
rad = np.deg2rad
deg = np.rad2deg


class TablePrinter:
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


class Control(ReciprocalMapWindow):

    COLUMNS = {1:{0 : '--', 1 : 'del_fix', 2 : 'nu_fix', 3 : 'qaz_fix', 4 : 'naz_fix', 5 : 'zone', 6 : '--'},
               2:{0 : '--', 1 : 'alpha = beta', 2 : 'alpha fix', 3 : 'beta fix', 4 : 'psi_fix', 5 : '--', 6 : '--'},
               3:{0 : 'omega fix', 1 : 'eta_fix', 2 : 'mu_fix', 3 : 'chi_fix', 4 : 'phi_fix', 5 : 'eta = delta/2', 6 : 'mu = nu/2'},
               4:{0 : '--', 1 : 'eta_fix', 2 : 'mu_fix', 3 : 'chi_fix', 4 : 'phi_fix', 5 : '--', 6 : '--'},
               5:{0 : '--', 1 : 'eta_fix', 2 : 'mu_fix', 3 : 'chi_fix', 4 : 'phi_fix', 5 : '--', 6 : '--'}}


    def __init__(self, *args):

        
        self.setup = self.parse_mode_args(args)
        self.handle_constraints()

        self.space = 12
        self.marker = '-'
        self.column_marker = '|'
        self.center = self.column_marker+"{:^" + str(self.space - 2) + "}" + self.column_marker
        self.roundfit = 5
        self.centshow = "{:^" + str(16 - 2) + "}"


        

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

    def parse_mode_args(self, mode):
        self.mode = mode

        for i in (mode):
            if i not in (0,1,2,3,4,5,6):
                raise ValueError('The values of columns must be between 0 and 6')

        if mode[0] == 0 and mode[1] == 0:
            if len(mode) <= 3:
                raise ValueError('''If de two first columns are set to 0, the columns 4 and 5 must be given''')
            elif mode[3] == 0 or mode[4] == 0:
                raise ValueError('''If de two first columns are set to 0, the columns 4 and 5 must not be 0''')

        if mode[0] == 5:
            raise('Zone mode was not implemented yet')
        if mode[0] == 6:
            raise('Energy mode was not implemented yet')

        self.col1 = mode[0]
        self.col2 = mode[1]
        self.col3 = mode[2]

        if len(mode) >= 4:
            self.col4 = mode[3]
        else:
            self.col4 = 0

        if len(mode) == 5:
            self.col5 = mode[4]
        else:
            self.col5 = 0

        return (self.COLUMNS[1][self.col1], self.COLUMNS[2][self.col2], self.COLUMNS[3][self.col3],
              self.COLUMNS[4][self.col4], self.COLUMNS[5][self.col5])

    def handle_constraints(self):
        """Logic to set up the constraints based on the given operation mode"""
        angles = {'--' : 'x', 'del_fix' : 'Del', 'nu_fix' : 'Nu', 'mu_fix' : 'Mu',
                  'eta_fix' : 'Eta', 'chi_fix' : 'Chi','phi_fix' : 'Phi'}

        cons = {'--' : 'x', 'qaz_fix' : 'qaz', 'naz_fix' : 'naz', 'alpha = beta' : 'aeqb',
                     'alpha fix' : 'alpha', 'beta fix' : 'beta', 'psi_fix' : 'psi', 'omega fix' : 'omega',
                     'eta = delta/2' : 'eta=del/2', 'mu = nu/2' : 'mu=nu/2'}

        self.motor_constraints = []
        self.pseudo_angle_constraints = []

        for i in range(len(self.setup)):
            if self.setup[i] in angles.keys():
                if i == 0 and self.setup[i] == '--':
                    pass

                elif i == 1 and self.setup[i] == '--':
                    pass

                else:
                    self.motor_constraints.append(angles[self.setup[i]])

            else:
                if self.setup[i] in cons.keys():
                    self.pseudo_angle_constraints.append(cons[self.setup[i]])

        self.fixed_motor_list = []
        for i in self.motor_constraints:
            if i != 'x':
               self.fixed_motor_list.append(i)
        if 'Mu' in self.fixed_motor_list:
            self.Mu_bound = 0
        else:
            self.Mu_bound = (-180,180)
        if 'Eta' in self.fixed_motor_list:
            self.Eta_bound = 0
        else:
            self.Eta_bound = (-180,180)
        if 'Chi' in self.fixed_motor_list:
            self.Chi_bound = 0
        else:
            self.Chi_bound = (-5,95)
        if 'Phi' in self.fixed_motor_list:
            self.Phi_bound = 0
        else:
            self.Phi_bound = (30,400)
        if 'Nu' in self.fixed_motor_list:
            self.Nu_bound = 0
        else:
            self.Nu_bound = (-180,180)
        if 'Del' in self.fixed_motor_list:
            self.Del_bound = 0
        else:
            self.Del_bound = (-180,180)                

        self.pseudo_constraints_w_value_list = [(self.pseudo_angle_constraints[i],0) if self.pseudo_angle_constraints[i] not in ('eta=del/2', 'mu=nu/2', 'aeqb') else (self.pseudo_angle_constraints[i], '--') for i in range(len(self.pseudo_angle_constraints))]



    def show(self, sh, ident = 3, space = 22):

        self.centshow = "{:^" + str(space - 2) + "}"

        dprint = {'x' : '--', 'Mu' : self.Mu_bound, 'Eta' : self.Eta_bound, 'Chi' : self.Chi_bound,
                      'Phi' : self.Phi_bound, 'Nu' : self.Nu_bound, 'Del' : self.Del_bound}

        lb = lambda x: "{:.5f}".format(float(x))


        self.forprint = self.pseudo_constraints_w_value_list.copy()

        if self.col1 in (1,2):
            if self.col1 == 1:
                self.forprint.insert(0,(self.setup[0],self.Del_bound))
            elif self.col1 == 2:
                self.forprint.insert(0,(self.setup[0],self.Nu_bound))
            for i in self.motor_constraints:
                if i not in ('Del', 'Nu'):
                    self.forprint.append((i,dprint[i]) )
            if self.col2 ==0:
                self.forprint.insert(1,('XD', '--'))

        else:
            if self.col1 == 0 and self.col2 ==0:

                self.forprint.insert(0,('XD', '--'))
                self.forprint.insert(0,('XD', '--'))

                for i in self.motor_constraints:
                    self.forprint.append((i,dprint[i]))


            elif self.col1 == 0:

                self.forprint.insert(0,('XD', '--'))


                for i in self.motor_constraints:
                    self.forprint.append((i,dprint[i]))


            elif self.col2 == 0:
                self.forprint.insert(1,('XD', '--'))
                # self.forprint.pop()

                for i in self.motor_constraints:
                    self.forprint.append((i,dprint[i]))
            else:
                for i in self.motor_constraints:
                    self.forprint.append((i,dprint[i]))

        conscols = [self.col1, self.col2, self.col3, self.col4, self.col5]
        experiment_list = [self.sampleor, lb(self.lam), lb(self.en/1000),'[' + str(self.idir[0]) +','+ str(self.idir[1]) +',' + str(self.idir[2]) + ']', '[' + str(self.ndir[0]) + ',' + str(self.ndir[1]) + ',' +str(self.ndir[2]) + ']', '[' + str(self.nref[0]) + ',' + str(self.nref[1]) + ',' +str(self.nref[2]) + ']']
        sample_info = [self.samp.name, self.samp.a, self.samp.b, self.samp.c, self.samp.alpha, self.samp.beta, self.samp.gamma]

        fmt = [
                    ('', 'ident',   ident),
                    ('', 'col1',   space),
                    ('', 'col2',   space),
                    ('', 'col3',   space),
                    ('', 'col4',   space),
                    ('', 'col5',   space),
                    ('', 'col6',   space),


                   ]


        if sh == 'mode':

            data = [{'ident':'','col1':self.centshow.format('MODE'), 'col2':self.centshow.format(self.setup[0]), 'col3':self.centshow.format(self.setup[1]), 'col4':self.centshow.format(self.setup[2]), 'col5':self.centshow.format(self.setup[3]), 'col6' : self.centshow.format(self.setup[4])},
                    {'ident':'','col1':self.centshow.format(str(self.col1)+str(self.col2)+str(self.col3)+str(self.col4)+str(self.col5)), 'col2':self.centshow.format(self.forprint[0][1]), 'col3':self.centshow.format(self.forprint[1][1]), 'col4':self.centshow.format(self.forprint[2][1]), 'col5':self.centshow.format(self.forprint[3][1]), 'col6' : self.centshow.format(self.forprint[4][1])},
                        ]


            return TablePrinter(fmt, ul='')(data)


        if sh == 'expt':

            data = [{'col1':self.centshow.format('Sampleor'), 'col2':self.centshow.format('WaveLength (angstrom)'), 'col3':self.centshow.format('Energy (keV)'), 'col4':self.centshow.format('Incidence Dir'), 'col5' : self.centshow.format('Normal Dir'), 'col6':self.centshow.format('Reference Dir')},
                    {'col1':self.centshow.format(self.sampleor), 'col2':self.centshow.format(lb(str(self.lam))), 'col3':self.centshow.format(str(lb(self.en/1000))),'col4':self.centshow.format(str(self.idir[0]) +' '+ str(self.idir[1]) +' ' + str(self.idir[2])), 'col5' : self.centshow.format(str(self.ndir[0]) + ' ' + str(self.ndir[1]) + ' ' +str(self.ndir[2])), 'col6': self.centshow.format(str(self.nref[0]) + ' ' + str(self.nref[1]) + ' ' +str(self.nref[2]))}
                   ]


            return TablePrinter(fmt, ul='')(data)


        if sh == 'sample':

            fmt = [
                    ('', 'ident',   ident),
                    ('', 'col1',   space),
                    ('', 'col2',   space),
                    ('', 'col3',   space),
                    ('', 'col4',   space),
                    ('', 'col5',   space),
                    ('', 'col6',   space),
                    ('', 'col7',   space), 
                   ]

            data = [{'col1':self.centshow.format('Sample'), 'col2':self.centshow.format('a'), 'col3':self.centshow.format('b'), 'col4':self.centshow.format('c'), 'col5' : self.centshow.format('Alpha'), 'col6':self.centshow.format('Beta'), 'col7':self.centshow.format('Gamma')},
                    {'col1':self.centshow.format(self.samp.name), 'col2':self.centshow.format(lb(str(self.samp.a))), 'col3':self.centshow.format(str(lb(self.samp.b))),'col4':self.centshow.format(str(lb(self.samp.c))), 'col5' : self.centshow.format(str(lb(self.samp.alpha))), 'col6': self.centshow.format(str(lb(self.samp.beta))), 'col7' : self.centshow.format(str(lb(self.samp.gamma)))}
                   ]
        
            return TablePrinter(fmt, ul='')(data)
        

        if sh == 'gui':
            

            return self.setup, conscols, self.forprint, experiment_list, sample_info

    def set_hkl(self, HKL):

        self.hkl = HKL

    def set_material(self, sample, *args):

        self.predefined_samples = {'Si':xu.materials.Si, 'Al' : xu.materials.Al, 'Co' : xu.materials.Co,
                     'Cu' : xu.materials.Cu, 'Cr' : xu.materials.Cr, 'Fe' : xu.materials.Fe,
                     'Ge' : xu.materials.Ge, 'Sn' : xu.materials.Sn,
                     'LaB6' : xu.materials.LaB6, 'Al2O3' : xu.materials.Al2O3, 'C' : xu.materials.C,
                     'C_HOPG' : xu.materials.C_HOPG, 'InAs' : xu.materials.InAs, 'InP' : xu.materials.InP,
                     'InSb' : xu.materials.InSb, 'GaP' : xu.materials.GaP, 'GaAs' : xu.materials.GaAs,
                     'AlAs' : xu.materials.AlAs, 'GaSb' : xu.materials.GaSb, 'GaAsWZ' : xu.materials.GaAsWZ,
                     'GaAs4H' : xu.materials.GaAs4H, 'GaPWZ' : xu.materials.GaPWZ, 'InPWZ' : xu.materials.InPWZ,
                     'InAs4H' : xu.materials.InAs4H, 'InSbWZ' : xu.materials.InSbWZ, 'InSb4H' : xu.materials.InSb4H,
                     'PbTe' : xu.materials.PbTe, 'PbSe' : xu.materials.PbSe, 'CdTe' : xu.materials.CdTe,
                     'CdSe' : xu.materials.CdSe, 'CdSe_ZB' : xu.materials.CdSe_ZB, 'HgSe' : xu.materials.HgSe,
                     'NaCl' : xu.materials.NaCl, 'MgO' : xu.materials.MgO, 'GaN' : xu.materials.GaN,
                     'BaF2' : xu.materials.BaF2, 'SrF2' : xu.materials.SrF2, 'CaF2' : xu.materials.CaF2,
                     'MnO' : xu.materials.MnO, 'MnTe' : xu.materials.MnTe, 'GeTe' : xu.materials.GeTe,
                     'SnTe' : xu.materials.SnTe, 'Au' : xu.materials.Au, 'Ti' : xu.materials.Ti,
                     'Mo' : xu.materials.Mo, 'Ru' : xu.materials.Ru, 'Rh' : xu.materials.Rh,
                     'V' : xu.materials.V, 'Ta' : xu.materials.Ta, 'Nb' : xu.materials.Nb,
                     'Pt' : xu.materials.Pt, 'Ag2Se' : xu.materials.Ag2Se, 'TiO2' : xu.materials.TiO2,
                     'MnO2' : xu.materials.MnO2, 'VO2_Rutile' : xu.materials.VO2_Rutile, 'VO2_Baddeleyite' : xu.materials.VO2_Baddeleyite,
                     'SiO2' : xu.materials.SiO2, 'In' : xu.materials.In, 'Sb' : xu.materials.Sb, 
                     'Ag' : xu.materials.Ag, 'SnAlpha' : xu.materials.SnAlpha, 'CaTiO3' : xu.materials.CaTiO3,
                     'SrTiO3' : xu.materials.SrTiO3, 'BaTiO3' : xu.materials.BaTiO3, 'FeO' : xu.materials.FeO,
                     'CoO' : xu.materials.CoO, 'Fe3O4' : xu.materials.Fe3O4, 'Co3O4' : xu.materials.Co3O4,
                     'FeRh' : xu.materials.FeRh, 'Ir20Mn80' : xu.materials.Ir20Mn80, 'CoFe' : xu.materials.CoFe,
                     'CoGa' : xu.materials.CoFe, 'CuMnAs' : xu.materials.CuMnAs, 'Mn3Ge_cub' : xu.materials.Mn3Ge_cub,
                     'Mn3Ge' : xu.materials.Mn3Ge, 'Pt3Cr' : xu.materials.Pt3Cr, 'TiN' : xu.materials.TiN}

        if sample in self.predefined_samples.keys():
            self.samp = self.predefined_samples[sample]

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
            if d < SMALL:

                raise DiffcalcException("Invalid UB reference data. Please check that the specified "
                                          "reference reflections/orientations are not parallel.")
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

    def dot3(self, x, y):
        """z = dot3(x ,y) -- where x, y are 3*1 Jama matrices"""
        return x[0, 0] * y[0, 0] + x[1, 0] * y[1, 0] + x[2, 0] * y[2, 0]

    def bound(self, x):
        """
        moves x between -1 and 1. Used to correct for rounding errors which may
        have moved the sin or cosine of a value outside this range.
        """
        SMALL = 1e-10
        if abs(x) > (1 + SMALL):
            raise AssertionError(
                "The value (%f) was unexpectedly too far outside -1 or 1 to "
                "safely bound. Please report this." % x)
        if x > 1:
            return 1
        if x < -1:
            return -1
        return x


    def _get_quat_from_u123(self, u1, u2, u3):
        q0, q1 = sqrt(1.-u1)*sin(2.*pi*u2), sqrt(1.-u1)*cos(2.*pi*u2)
        q2, q3 =    sqrt(u1)*sin(2.*pi*u3),    sqrt(u1)*cos(2.*pi*u3)
        return q0, q1, q2, q3

    def _get_rot_matrix(self, q0, q1, q2, q3):
        rot = MAT([[q0**2 + q1**2 - q2**2 - q3**2,            2.*(q1*q2 - q0*q3),            2.*(q1*q3 + q0*q2),],
                  [           2.*(q1*q2 + q0*q3), q0**2 - q1**2 + q2**2 - q3**2,            2.*(q2*q3 - q0*q1),],
                  [           2.*(q1*q3 - q0*q2),            2.*(q2*q3 + q0*q1), q0**2 - q1**2 - q2**2 + q3**2,]])
        return rot

    def angle_between_vectors(self, a, b):
        costheta = self.dot3(a * (1 / LA.norm(a)), b * (1 / LA.norm(b)))
        return np.arccos(self.bound(costheta))
    
    def _func_orient(self, vals, crystal, ref_data):
        quat = self._get_quat_from_u123(*vals)
        trial_u = self._get_rot_matrix(*quat)
        tmp_ub = trial_u * crystal.B

        res = 0
        I = MAT([[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]])

        for ref in ref_data:
            en = ref[9]
            wl = xu.en2lam(en)
            hkl_vals = np.array(ref[:3]).T
            Mu = ref[3]
            Eta = ref[4]
            Chi = ref[5]
            Phi = ref[6]
            Nu = ref[7]
            Del = ref[8]

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

            q_del = (NU * DEL - I) * MAT([[0], [2 * np.pi / wl], [0]])
            q_vals = LA.inv(PHI) * LA.inv(CHI) * LA.inv(ETA) * LA.inv(MU) * q_del

            q_hkl = tmp_ub * hkl_vals
            res += self.angle_between_vectors(q_hkl, q_vals)
        return res

    def _get_init_u123(self, um):
        
        def sign(x):
            if x < 0:
                return -1
            else:
                return 1

        tr = um[0,0] + um[1,1] + um[2,2]
        sgn_q1 = sign(um[2,1] - um[1,2])
        sgn_q2 = sign(um[0,2] - um[2,0])
        sgn_q3 = sign(um[1,0] - um[0,1])
        q0 = sqrt(1. + tr) / 2.
        q1 = sgn_q1 * sqrt(1. + um[0,0] - um[1,1] - um[2,2]) / 2.0
        q2 = sgn_q2 * sqrt(1. - um[0,0] + um[1,1] - um[2,2]) / 2.0
        q3 = sgn_q3 * sqrt(1. - um[0,0] - um[1,1] + um[2,2]) / 2.0
        u1 = (1. - um[0,0]) / 2.
        u2 = atan2(q0, q1) / (2. * pi)
        u3 = atan2(q2, q3) / (2. * pi)
        if u2 < 0: u2 += 1.
        if u3 < 0: u3 += 1.
        return u1, u2, u3

    def fit_u_matrix(self, init_u, refl_list):
        uc = self.samp
        try:
            start = list(self._get_init_u123(init_u))
            lower = [ 0, 0, 0]
            upper = [ 1, 1, 1]
            sigma = [ 1e-2, 1e-2, 1e-2]
        except AttributeError:
            raise DiffcalcException("UB matrix not initialised. Cannot run UB matrix fitting procedure.")
       
        from scipy.optimize import minimize

        ref_data = refl_list
        bounds = zip(lower, upper)
        res = minimize(self._func_orient,
                       start,
                       args=(uc, ref_data),
                       method='SLSQP',
                       tol=1e-10,
                       options={'disp' : False,
                                'maxiter': 10000,
                                'eps': 1e-6,
                                'ftol': 1e-10})
                       # bounds=bounds)
        vals = res.x
        q0, q1, q2, q3 = self._get_quat_from_u123(*vals)
        res_u = self._get_rot_matrix(q0, q1, q2, q3)
        angle = 2. * acos(q0)
        xr = q1 / sqrt(1. - q0 * q0)
        yr = q2 / sqrt(1. - q0 * q0)
        zr = q3 / sqrt(1. - q0 * q0)
        TODEG = 180/(2*np.pi)
        print (angle * TODEG, (xr, yr, zr), res)
        return res_u


    def set_constraints(self, *args, setineq = None, **kwargs):

        lb = lambda x: "{:.5f}".format(float(x))
        self.pseudo_constraints_w_value_list = list()
        if kwargs:
            if 'Mu' in kwargs.keys() and 'Mu' in self.fixed_motor_list:
                self.Mu_bound = kwargs['Mu']

            if 'Eta' in kwargs.keys() and 'Eta' in self.fixed_motor_list:
                self.Eta_bound = kwargs['Eta']

            if 'Chi' in kwargs.keys() and 'Chi' in self.fixed_motor_list:
                self.Chi_bound = kwargs['Chi']

            if 'Phi' in kwargs.keys() and 'Phi' in self.fixed_motor_list:
                self.Phi_bound = kwargs['Phi']

            if 'Nu' in kwargs.keys() and 'Nu' in self.fixed_motor_list:
                self.Nu_bound = kwargs['Nu']

            if 'Del' in kwargs.keys() and 'Del' in self.fixed_motor_list:
                self.Del_bound = kwargs['Del']

            if 'qaz' in kwargs.keys() and 'qaz' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('qaz', kwargs['qaz']))

            if 'naz' in kwargs.keys() and 'naz' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('naz', kwargs['naz']))

            if 'alpha' in kwargs.keys() and 'alpha' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('alpha', kwargs['alpha']))

            if 'beta' in kwargs.keys() and 'beta' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('beta', kwargs['beta']))

            if 'psi' in kwargs.keys() and 'psi' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('psi', kwargs['psi']))

            if 'omega' in kwargs.keys() and 'omega' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('omega', kwargs['omega']))

            if 'aeqb' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('aeqb', '--'))

            if 'eta=del/2' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('eta=del/2', '--'))

            if 'mu=nu/2' in self.pseudo_angle_constraints:
                self.pseudo_constraints_w_value_list.append(('mu=nu/2', '--'))


    def set_circle_constrain(self, **kwargs):

        if 'Mu' in kwargs.keys() and 'Mu' not in self.fixed_motor_list:
            self.Mu_bound = kwargs['Mu']

        if 'Eta' in kwargs.keys() and 'Eta' not in self.fixed_motor_list:
            self.Eta_bound = kwargs['Eta']

        if 'Chi' in kwargs.keys() and 'Chi' not in self.fixed_motor_list:
            self.Chi_bound = kwargs['Chi']

        if 'Phi' in kwargs.keys() and 'Phi' not in self.fixed_motor_list:
            self.Phi_bound = kwargs['Phi']

        if 'Nu' in kwargs.keys() and 'Nu' not in self.fixed_motor_list:
            self.Nu_bound = kwargs['Nu']

        if 'Del' in kwargs.keys() and 'Del' not in self.fixed_motor_list:
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

    def set_print_options(self, marker = '-', column_marker = '|', space = 12):

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

        lb = lambda x: "{:.5f}".format(float(x))

        if self.isscan:
            return  repr(self.formscantxt)


        else:
            dprint = {'x' : '--', 'Mu' : self.Mu_bound, 'Eta' : self.Eta_bound, 'Chi' : self.Chi_bound,
                      'Phi' : self.Phi_bound, 'Nu' : self.Nu_bound, 'Del' : self.Del_bound}


            self.forprint = self.pseudo_constraints_w_value_list.copy()


            if self.col1 in (1,2):
                if self.col1 == 1:
                    self.forprint.insert(0,(self.setup[0],self.Del_bound))
                elif self.col1 == 2:
                    self.forprint.insert(0,(self.setup[0],self.Nu_bound))
                for i in self.motor_constraints:
                    if i not in ('Del', 'Nu'):
                        self.forprint.append((i,dprint[i]) )
                if self.col2 ==0:
                    self.forprint.insert(1,('XD', '--'))

            else:
                if self.col1 == 0 and self.col2 ==0:

                    self.forprint.insert(0,('XD', '--'))
                    self.forprint.insert(0,('XD', '--'))

                    for i in self.motor_constraints:
                        self.forprint.append((i,dprint[i]))


                elif self.col1 == 0:

                    self.forprint.insert(0,('XD', '--'))


                    for i in self.motor_constraints:
                        self.forprint.append((i,dprint[i]))


                elif self.col2 == 0:
                    self.forprint.insert(1,('XD', '--'))
                    # self.forprint.pop()

                    for i in self.motor_constraints:
                        self.forprint.append((i,dprint[i]))
                else:
                    for i in self.motor_constraints:
                        self.forprint.append((i,dprint[i]))

            self.forprint = [(i[0], lb(i[1])) if i[1] != '--' else (i[0], i[1]) for i in self.forprint]


            data = [{'col1':self.center.format('MODE'), 'col2':self.center.format(self.setup[0]), 'col3':self.center.format(self.setup[1]), 'col4':self.center.format(self.setup[2]), 'col5':self.center.format(self.setup[3]), 'col6' : self.center.format(self.setup[4]), 'col7' : self.center.format('Error')},
                    {'col1':self.center.format(str(self.col1)+str(self.col2)+str(self.col3)+str(self.col4)+str(self.col5)), 'col2':self.center.format(self.forprint[0][1]), 'col3':self.center.format(self.forprint[1][1]), 'col4':self.center.format(self.forprint[2][1]), 'col5':self.center.format(self.forprint[3][1]), 'col6' : self.center.format(self.forprint[4][1]), 'col7' : self.center.format('%.3g' % self.qerror)},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('H'), 'col2' : self.center.format('K'), 'col3':self.center.format('L'), 'col4' : self.center.format('Ref vector'), 'col5':self.center.format('Energy (keV)'), 'col6':self.center.format('WL (angstrom)'), 'col7':self.center.format('Sample')},
                    {'col1':self.center.format(str(lb(self.hkl_calc[0]))), 'col2' : self.center.format(str(lb(self.hkl_calc[1]))), 'col3':self.center.format(str(lb(self.hkl_calc[2]))),'col4' : self.center.format(str(self.nref[0])+ ' ' + str(self.nref[1]) + ' ' + str(self.nref[2])),'col5':self.center.format(lb(self.en/1000)), 'col6':self.center.format(lb(self.lam)), 'col7':self.center.format(self.samp.name)},
                    {'col1':self.marker*self.space, 'col2':self.marker*self.space, 'col3':self.marker*self.space, 'col4':self.marker*self.space, 'col5':self.marker*self.space, 'col6' : self.marker*self.space,'col7':self.marker*self.space},
                    {'col1':self.center.format('Qx'), 'col2' : self.center.format('Qy'), 'col3':self.center.format('Qz'), 'col4' : self.center.format('|Q|'),'col5':self.center.format('Exp 2theta'), 'col6':self.center.format('Dhkl'), 'col7':self.center.format('FHKL (Base)')},
                    {'col1':self.center.format(str(lb(self.Qshow[0]))), 'col2' : self.center.format(str(lb(self.Qshow[1]))), 'col3':self.center.format(str(lb(self.Qshow[2]))), 'col4' : self.center.format(lb(self.Qnorm)), 'col5':self.center.format(lb(self.ttB1)), 'col6':self.center.format(lb(self.dhkl)), 'col7':self.center.format(lb(self.FHKL))},
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


    def calcUB(self):

        return self.U.dot(self.samp.B)

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
        n = self.nref
        nc = self.samp.B.dot(n)
        nchat = nc/LA.norm(nc)
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
        self.Qshow = q
        normQ = LA.norm(q)
        self.Qnorm = normQ
        Qhat = np.round(q/normQ,5)


        k = (2*np.pi)/(self.lam)
        Ki = k*np.array([0,1,0])
        Kf0 = Ki ##### eq (6)
        Kfnu = k*MAT([ np.sin(rad(Del)), np.cos(rad(Nu))*np.cos(rad(Del)), np.sin(rad(Nu))*np.cos(rad(Del))])
        Kfnunorm = LA.norm(Kfnu)
        Kfnuhat = Kfnu/Kfnunorm


        taupseudo = deg(np.arccos(np.round(Qhat.dot(nchat),5)))


        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))

        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))


        qaz = deg(np.arctan2(np.tan(rad(Del)),np.sin(rad(Nu))))


        # QLhat = MAT([ np.cos(rad(tB1))*np.sin(rad(qaz)),
        #             -np.sin(rad(tB1)),
        #             np.cos(rad(tB1))*np.cos(rad(qaz))])

        # taupseudo = deg(np.arccos(QLhat.dot(nz)))


        # naz = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))

        naz = deg(np.arctan2((nz.dot([1,0,0])),(nz.dot([0,0,1]))))


        if taupseudo == 0 or taupseudo == 180:

            Qphi = Qhat.dot(self.samp.B)
            Qphinorm = LA.norm(Qphi)
            Qphihat = Qphi/Qphinorm

            newref = MAT([np.sqrt(Qphihat[1]**2 + Qphihat[2]**2),
                                  -(Qphihat[0]*Qphihat[1])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2)),
                                  -(Qphihat[0]*Qphihat[2])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2))])

            ntmp = newref
            nctmp = self.samp.B.dot(ntmp)
            nchattmp = nc/LA.norm(nctmp)
            nphitmp = self.U.dot(nctmp)
            nphihattmp = nphitmp/LA.norm(nphitmp)

            nztmp = Z.dot(nphihattmp)
            alphatmp = deg(np.arcsin(-xu.math.vector.VecDot(nztmp,[0,1,0])))
            tautemp = deg(np.arccos(Qhat.dot(newref)))

            arg2 = np.round((np.cos(rad(tautemp))*np.sin(rad(tB1))-np.sin(rad(alphatmp)))/(np.sin(rad(tautemp))*np.cos(rad(tB1))),8)


            # print('')
            # print(' The reference vector is parallel to the Q vector, in order to calculate psi the reference\n vector {} will be used.'.format(np.round(newref,5)))

        else:

            arg2 = np.round((np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1))),8)

        psipseudo = deg(np.arccos(arg2))

        # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        # # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))

        # if arg3 >1:
        #     arg3 = 0.99999999999999999999
        # elif arg3 < -1:
        #     arg3 = -0.9999999999999999999

        # betaout = deg(np.arcsin(arg3))

        betaout = deg(np.arcsin((np.dot(Kfnuhat, nz))))


        arg4 = np.round((np.sin(rad(Eta))*np.sin(rad(qaz))+np.sin(rad(Mu))*np.cos(rad(Eta))*np.cos(rad(qaz)))*np.cos(rad(tB1))-np.cos(rad(Mu))*np.cos(rad(Eta))*np.sin(rad(tB1)),5)
        # if arg4 >1:
        #   arg4 = 0.999999999999999999999
        # elif  arg4 < -1:
        #     arg4 = -0.999999999999999999
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
        n = self.nref
        nc = self.samp.B.dot(n)
        nchat = nc/LA.norm(nc)
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
        Qhat = np.round(q/normQ,5)

        k = (2*np.pi)/(self.lam)
        Ki = k*np.array([0,1,0])
        Kf0 = Ki ##### eq (6)
        Kfnu = k*MAT([ np.sin(rad(Del)), np.cos(rad(Nu))*np.cos(rad(Del)), np.sin(rad(Nu))*np.cos(rad(Del))])
        Kfnunorm = LA.norm(Kfnu)
        Kfnuhat = Kfnu/Kfnunorm


        # taupseudo = deg(np.arccos(Qhat.dot(nhat)))
        taupseudo = deg(np.arccos(np.round(Qhat.dot(nchat),5)))


        ttB1 = deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del))))
        tB1 = ttB1/2


        alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))

        # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))


        qaz = deg(np.arctan2(np.tan(rad(Del)),np.sin(rad(Nu))))

        # QLhat = MAT([ np.cos(rad(tB1))*np.sin(rad(qaz)),
        #             -np.sin(rad(tB1)),
        #             np.cos(rad(tB1))*np.cos(rad(qaz))])

        # taupseudo = deg(np.arccos(QLhat.dot(nz)))
        # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))

        naz = deg(np.arctan2((nz.dot([1,0,0])),(nz.dot([0,0,1]))))


        if taupseudo == 0 or taupseudo == 180:

            Qphi = Qhat.dot(self.samp.B)
            Qphinorm = LA.norm(Qphi)
            Qphihat = Qphi/Qphinorm

            newref = MAT([np.sqrt(Qphihat[1]**2 + Qphihat[2]**2),
                                  -(Qphihat[0]*Qphihat[1])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2)),
                                  -(Qphihat[0]*Qphihat[2])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2))])

            ntmp = newref
            nctmp = self.samp.B.dot(ntmp)
            nchattmp = nc/LA.norm(nctmp)
            nphitmp = self.U.dot(nctmp)
            nphihattmp = nphitmp/LA.norm(nphitmp)

            nztmp = Z.dot(nphihattmp)
            alphatmp = deg(np.arcsin(-xu.math.vector.VecDot(nztmp,[0,1,0])))
            tautemp = deg(np.arccos(Qhat.dot(newref)))

            arg2 = np.round((np.cos(rad(tautemp))*np.sin(rad(tB1))-np.sin(rad(alphatmp)))/(np.sin(rad(tautemp))*np.cos(rad(tB1))),8)

        else:

            arg2 = np.round((np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1))),8)


        psipseudo = deg(np.arccos(arg2))


        # psipseudo = deg(np.arccos(arg2))


        # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
        # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))

        # if arg3 >1:
        #     arg3 = 0.99999999999999999999
        # elif arg3 < -1:
        #     arg3 = -0.9999999999999999999
        # betaout = deg(np.arcsin(arg3))

        betaout = deg(np.arcsin((np.dot(Kfnuhat, nz))))

        arg4 = np.round((np.sin(rad(Eta))*np.sin(rad(qaz))+np.sin(rad(Mu))*np.cos(rad(Eta))*np.cos(rad(qaz)))*np.cos(rad(tB1))-np.cos(rad(Mu))*np.cos(rad(Eta))*np.sin(rad(tB1)))
        # if arg4 >1:
        #   arg4 = 0.999999999999999999999
        # elif  arg4 < -1:
        #     arg4 = -0.999999999999999999
        omega = deg(np.arcsin(arg4))


        if pseudo_angle == 'alpha':
            return alphain - fix_angle

        elif pseudo_angle == 'beta':
            return betaout - fix_angle

        elif pseudo_angle == 'qaz':
            return qaz - fix_angle

        elif pseudo_angle == 'naz':
            return naz - fix_angle

        elif pseudo_angle == 'tau':
            return taupseudo - fix_angle

        elif pseudo_angle == 'psi':
            return psipseudo - fix_angle

        elif pseudo_angle == 'omega':
            return omega - fix_angle

        elif pseudo_angle == 'aeqb':
            return betaout - alphain


    def motor_angles(self, *args, qvec = False, calc = True, max_err = 1e-5, **kwargs):

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
            else:
                self.start = [0,0,0,0,0,0]

            media = lambda x,y: (x+y)/2
            # self.chute1 = [media(i[0], i[1]) if type(i) != float else i for i in self.bounds]
            self.chute1 = [45,45,45,45,45,45]


            if len(self.pseudo_constraints_w_value_list) != 0:
                    pseudoconst = Control.pseudoAngleConst


                    if len(self.pseudo_constraints_w_value_list) == 1:


                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.pseudo_constraints_w_value_list[0][0], self.pseudo_constraints_w_value_list[0][1])}]


                    elif len(self.pseudo_constraints_w_value_list) == 2:


                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.pseudo_constraints_w_value_list[0][0], self.pseudo_constraints_w_value_list[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.pseudo_constraints_w_value_list[1][0], self.pseudo_constraints_w_value_list[1][1])}]


                    elif len(self.pseudo_constraints_w_value_list) == 3:


                            restrict = [{'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.pseudo_constraints_w_value_list[0][0], self.pseudo_constraints_w_value_list[0][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.pseudo_constraints_w_value_list[1][0], self.pseudo_constraints_w_value_list[1][1])},
                                        {'type':'eq', 'fun': lambda a: pseudoconst(self, a, self.pseudo_constraints_w_value_list[2][0], self.pseudo_constraints_w_value_list[2][1])}]


                    ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat = self.U)

                    if qerror > max_err:
                            while True:
                                self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                                self.start = (0,0,0,0,0,self.preangs[3])
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 0, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                # self.start = [0, self.chute1[1], self.chute1[2], 90, self.chute1[4], self.preangs[3]]
                                # ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                # if qerror < 1e-5:
                                #     break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 90, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 180, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 270, self.chute1[4], self.chute1[5]]
                                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, constraints=restrict, ormat=self.U)
                                if qerror < max_err:
                                    break
                                break


            else:

                ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat = self.U)
                if qerror > max_err:
                    while True:
                        self.preangs = self.hrxrd.Q2Ang(self.Q_lab)
                        self.start = (0,0,0,0,0,self.preangs[3])
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 0, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 90, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        # self.start = [0, self.chute1[1], self.chute1[2], 90, self.chute1[4], self.chute1[5]]
                        # ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        # if qerror < 1e-5:
                        #     break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 180, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        self.start = [self.chute1[0], self.chute1[1], self.chute1[2], 270, self.chute1[4], self.chute1[5]]
                        ang, qerror, errcode = xu.Q2AngFit(self.Q_lab, self.hrxrd, self.bounds, startvalues = self.start, ormat=self.U)
                        if qerror < max_err:
                            break
                        break


            self.qerror = qerror
            self.hkl_calc = np.round(self.hrxrd.Ang2HKL(*ang,mat=self.samp, en = self.en, U=self.U),5)


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

            n = self.nref
            nc = self.samp.B.dot(n)
            nchat = nc/LA.norm(nc)
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
            self.Qshow = q
            normQ = LA.norm(q)
            self.Qnorm = normQ
            Qhat = np.round(q/normQ,5)
            self.FHKL = LA.norm(self.samp.StructureFactor(q, self.en))


            k = (2*np.pi)/(self.lam)
            Ki = k*np.array([0,1,0])
            Kf0 = Ki ##### eq (6)
            Kfnu = k*MAT([ np.sin(rad(self.Del)), np.cos(rad(self.Nu))*np.cos(rad(self.Del)), np.sin(rad(self.Nu))*np.cos(rad(self.Del))])
            Kfnunorm = LA.norm(Kfnu)
            Kfnuhat = Kfnu/Kfnunorm


            taupseudo = deg(np.arccos(np.round(Qhat.dot(nchat),5)))


            ttB1 = deg(np.arccos(np.cos(rad(self.Nu)) * np.cos(rad(self.Del))))
            tB1 = ttB1/2

            alphain = deg(np.arcsin(-xu.math.vector.VecDot(nz,[0,1,0])))

            # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
            qaz = deg(np.arctan2(np.tan(rad(self.Del)),np.sin(rad(self.Nu))))

            # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))

            # QLhat = MAT([ np.cos(rad(tB1))*np.sin(rad(qaz)),
            #         -np.sin(rad(tB1)),
            #         np.cos(rad(tB1))*np.cos(rad(qaz))])

            # taupseudo = deg(np.arccos(QLhat.dot(nz)))

            naz = deg(np.arctan2((nz.dot([1,0,0])),(nz.dot([0,0,1]))))


            if taupseudo == 0 or taupseudo == 180:

                Qphi = Qhat.dot(self.samp.B)
                Qphinorm = LA.norm(Qphi)
                Qphihat = Qphi/Qphinorm

                newref = MAT([np.sqrt(Qphihat[1]**2 + Qphihat[2]**2),
                                      -(Qphihat[0]*Qphihat[1])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2)),
                                      -(Qphihat[0]*Qphihat[2])/(np.sqrt(Qphihat[1]**2 + Qphihat[2]**2))])
                ntmp = newref
                nctmp = self.samp.B.dot(ntmp)
                nchattmp = nc/LA.norm(nctmp)
                nphitmp = self.U.dot(nctmp)
                nphihattmp = nphitmp/LA.norm(nphitmp)

                nztmp = Z.dot(nphihattmp)
                alphatmp = deg(np.arcsin(-xu.math.vector.VecDot(nztmp,[0,1,0])))
                tautemp = deg(np.arccos(Qhat.dot(newref)))

                arg2 = np.round((np.cos(rad(tautemp))*np.sin(rad(tB1))-np.sin(rad(alphatmp)))/(np.sin(rad(tautemp))*np.cos(rad(tB1))),8)
                if 'flagmap' not in kwargs.keys():

                    print('')
                    print('Q parallel to reference vector, so using {} as reference for Psi'.format(np.round(newref,5)))


            else:
                arg2 = (np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1)))

                arg2 = np.round((np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/(np.sin(rad(taupseudo))*np.cos(rad(tB1))),8)


            psipseudo = deg(np.arccos(arg2))
            # arg3 = 2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))
            # arg3 = ((np.cos(rad(taupseudo))*np.sin(rad(tB1))) + (np.cos(rad(tB1))*np.sin(rad(taupseudo))*np.cos(rad(psipseudo))))
            # # print(arg3)
            # if arg3 >1:
            #     arg3 = 0.999999999999999999999
            # elif arg3 < -1:
            #     arg3 = -0.99999999999999999999
            # betaout = deg(np.arcsin(arg3))

            betaout = deg(np.arcsin((np.dot(Kfnuhat, nz))))


            arg4 = np.round((np.sin(rad(self.Eta))*np.sin(rad(qaz))+np.sin(rad(self.Mu))*np.cos(rad(self.Eta))*np.cos(rad(qaz)))*np.cos(rad(tB1))-np.cos(rad(self.Mu))*np.cos(rad(self.Eta))*np.sin(rad(tB1)),5)
            # if arg4 >1:
            #   arg4 = 0.999999999999999999999
            # elif arg4 < -1:
            #     arg4 = -0.999999999999999999999
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


            return [self.Mu, self.Eta, self.Chi, self.Phi, self.Nu, self.Del, self.ttB1, self.tB1, self.alphain, self.qaz, self.naz, self.taupseudo, self.psipseudo, self.betaout, self.omega, "{0:.2e}".format(self.qerror)], [self.fcsv(self.Mu), self.fcsv(self.Eta), self.fcsv(self.Chi), self.fcsv(self.Phi), self.fcsv(self.Nu), self.fcsv(self.Del), self.fcsv(self.ttB1), self.fcsv(self.tB1), self.fcsv(self.alphain), self.fcsv(self.qaz), self.fcsv(self.naz), self.fcsv(self.taupseudo), self.fcsv(self.psipseudo), self.fcsv(self.betaout), self.fcsv(self.omega), self.fcsv(self.hkl_calc[0]), self.fcsv(self.hkl_calc[1]), self.fcsv(self.hkl_calc[2]), "{0:.2e}".format(self.qerror)]


    def scan(self, hkli, hklf, points, diflimit = 0.1, write = False, name = 'testscan.txt', sep = ',', startvalues = [0,0,0,0,0,0], gui=False):

        scl = Control.scan_generator(self, hkli, hklf, points+1)
        angslist = list()
        
        if gui:
            for i in scl:
                self.hkl = i
                a,b = self.motor_angles(self, sv=startvalues)
                angslist.append(b)
                teste = np.abs(np.array(a[:6]) - np.array(startvalues))


                if np.max(teste) > diflimit and diflimit != 0:
                    raise ("Exceded max limit of angles variation")

                if float(a[-1]) > 1e-5:
                    raise('qerror is too big, process failed')

                startvalues = a[:6]

                pd.DataFrame([b], columns=['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', '2theta', 'theta', 'alpha', 'qaz', 'naz',
                'tau', 'psi', 'beta', 'omega','H', 'K', 'L', 'Error']).to_csv('.my_scan_counter.csv', mode='a', header=False)
        
        else:
            for i in tqdm(scl):
                self.hkl = i
                a,b = self.motor_angles(self, sv=startvalues)
                angslist.append(b)
                teste = np.abs(np.array(a[:6]) - np.array(startvalues))


                if np.max(teste) > diflimit and diflimit != 0:
                    raise ("Exceded max limit of angles variation")

                if float(a[-1]) > 1e-5:
                    raise('qerror is too big, process failed')

                startvalues = a[:6]

                pd.DataFrame([b], columns=['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', '2theta', 'theta', 'alpha', 'qaz', 'naz',
                'tau', 'psi', 'beta', 'omega','H', 'K', 'L', 'Error']).to_csv('.my_scan_counter.csv', mode='a', header=False)


        self.isscan = True

        self.formscantxt = pd.DataFrame(angslist, columns=['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', '2theta', 'theta', 'alpha', 'qaz', 'naz',
                                                                                             'tau', 'psi', 'beta', 'omega','H', 'K', 'L', 'Error'])

        self.formscan = self.formscantxt[['Mu', 'Eta', 'Chi', 'Phi', 'Nu', 'Del', 'Error']]

        scan_points = [i[:6] for i in angslist] ## Get only mu, eta, chi, phi, nu, del

        


        if write:
            self.formscantxt.to_csv(name, sep=sep)

        pd.options.display.max_rows = None
        pd.options.display.max_columns = 0

        return scan_points
