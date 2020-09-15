# This file is part of xrayutilities.
#
# xrayutilities is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2015-2016 Dominik Kriegner <dominik.kriegner@gmail.com>

"""
Module provides functions to convert a q-vector from reciprocal space to
angular space. a simple implementation uses scipy optimize routines to perform
a fit for a arbitrary goniometer.

The user is, however, expected to use the bounds variable to put restrictions
to the number of free angles to obtain reproducible results. In general only 3
angles are needed to fit an arbitrary q-vector (2 sample + 1 detector angles or
1 sample + 2 detector). More complicated restrictions can be implemented using
the lmfit package. (done upon request!)

The function is based on a fitting routine. For a specific goniometer also
analytic expressions from literature can be used as they are implemented in the
predefined experimental classes HXRD, NonCOP, and GID.
"""

import numbers

import numpy
import numpy as np
import scipy.optimize

from . import config, math
from .exception import InputError


def _makebounds(boundsin):
    """
    generate proper bounds for scipy.optimize.minimize function
    from a list/tuple of more convenient bounds.

    Parameters
    ----------
    boundsin :  list or tuple or array-like
        bounds, or fixed values. the number of entries needs to be equal to the
        number of angle in the goniometer given to the q2ang_general function
        example input for four gonimeter angles: ((0, 90), 0, (0, 180), (0,
        90))

    Returns
    -------
    tuple
        bounds to be handed over to the scipy.minimize routine. The function
        will expand fixed values to two equal bounds
    """
    boundsout = []
    for b in boundsin:
        if isinstance(b, (tuple, list, numpy.ndarray)):
            if len(b) == 2:
                boundsout.append((b[0], b[1]))
            elif len(b) == 1:
                boundsout.append((b[0], b[0]))
            else:
                raise InputError('bound values must have two or one elements')
        elif isinstance(b, numbers.Number):
            boundsout.append((b, b))  # variable fixed
        elif b is None:
            boundsout.append((None, None))  # no bound
        else:
            raise InputError('bound value is of invalid type (%s)' % type(b))

    return tuple(boundsout)


def _errornorm_q2ang(angles, qvec, hxrd, U=numpy.identity(3)):
    """
    function to determine the offset in the qposition calculated from
    a set of experimental angles and the given vector

    Parameters
    ----------
    angles :    iterable
        iterable object with angles of the goniometer
    qvec :      list or tuple or array-like
        vector with three q-coordinates
    hxrd :      Experiment
        experiment class to be used for the q calculation
    U :         array-like, optional
        orientation matrix

    Returns
    -------
    error : float
        q-space error between the current fit-guess and the user-specified
        position
    """

    qcalc = hxrd.Ang2Q.point(*angles, UB=U)

    dq = numpy.linalg.norm(qcalc - qvec)
    # print(np.round(qcalc,3))
    return dq

def pseudoAngleConst(angles, pseudo_angle, fix_angle):
    
    if pseudo_angle == 'eta=del/2':
        return angles[1] - angles[5]/2
    elif pseudo_angle == 'mu=nu/2':
        return aangles[0] - angles[4]/2
    
    PI = np.pi
    MAT = np.array
    rad = np.deg2rad
    deg = np.rad2deg
    
    Mu = angles[0]
    Eta = angles[1]
    Chi = angles[2]
    Phi= angles[3]
    Nu = angles[4]
    Del = angles[5]

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
    ttB1 = round(deg(np.arccos(np.cos(rad(Nu)) * np.cos(rad(Del)))),5)
    tB1 = ttB1/2
    
    alphain = deg(np.arcsin(-math.vector.VecDot(nz,[0,1,0])))
    
    # upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.000001))))
    upsipseudo = deg(np.arctan(np.tan(rad(Del))/np.sin(rad(Nu+0.0000000000000000001))))
    qaz = upsipseudo
    # phipseudo = deg(np.arctan(np.tan(rad(Eta))/np.sin(rad(Mu))))
    
    phipseudo = deg(np.arctan((nz.dot([1,0,0]))/(nz.dot([0,0,1]))))
    naz = phipseudo
    
    taupseudo = deg(np.arccos(np.cos(rad(alphain))*np.cos(rad(tB1))*np.cos(rad(phipseudo-upsipseudo))
                            +np.sin(rad(alphain))*np.sin(rad(tB1))))
    
    psipseudo = deg(np.arccos(round((np.cos(rad(taupseudo))*np.sin(rad(tB1))-np.sin(rad(alphain)))/
                                    (np.sin(rad(taupseudo+0.00000000001))*np.cos(rad(tB1+0.00000000001))),6)))
    
    betaout = deg(np.arcsin(2*np.sin(rad(tB1))*np.cos(rad(taupseudo)) - np.sin(rad(alphain))))
    
    omega = deg(np.arcsin((np.sin(rad(Eta))*np.sin(rad(upsipseudo))+np.sin(rad(Mu))*np.cos(rad(Eta))*
                            np.cos(rad(upsipseudo)))*np.cos(rad(tB1))-np.cos(rad(Mu))*np.cos(rad(Eta))*np.sin(rad(tB1))))
    
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


def exitAngleConst(angles, alphaf, hxrd):
    """
    helper function for an pseudo-angle constraint for the Q2AngFit-routine.

    Parameters
    ----------
    angles :    iterable
        fit parameters of Q2AngFit
    alphaf :    float
        the exit angle which should be fixed
    hxrd :      Experiment
        the Experiment object to use for qconversion
    """
    qconv = hxrd._A2QConversion
    # calc kf
    detangles = [a for a in angles[-len(qconv.detectorAxis):]]
    kf = qconv.getDetectorPos(*detangles)
    if numpy.linalg.norm(kf) == 0:
        af = 0
    else:
        ndirlab = qconv.transformSample2Lab(hxrd.Transform(hxrd.ndir), *angles)
        af = 90 - math.VecAngle(kf, ndirlab, deg=True) - alphaf
    return af


def Q2AngFit(qvec, expclass, bounds=None, ormat=numpy.identity(3),
             startvalues=None, constraints=()):
    """
    Functions to convert a q-vector from reciprocal space to angular space.
    This implementation uses scipy optimize routines to perform a fit for a
    goniometer with arbitrary number of goniometer angles.

    The user *must* use the bounds variable to put
    restrictions to the number of free angles to obtain reproducible results.
    In general only 3 angles are needed to fit an arbitrary q-vector (2 sample
    + 1 detector angles or 1 sample + 2 detector).

    Parameters
    ----------
    qvec :      tuple or list or array-like
        q-vector for which the angular positions should be calculated
    expclass :  Experiment
        experimental class used to define the goniometer for which the angles
        should be calculated.

    bounds :    tuple or list
        bounds of the goniometer angles. The number of bounds must correspond
        to the number of goniometer angles in the expclass.  Angles can also be
        fixed by supplying only one value for a particular angle. e.g.: ((low,
        up), fix, (low2, up2), (low3, up3))
    ormat :     array-like
        orientation matrix of the sample to be used in the conversion
    startvalues :   array-like
        start values for the fit, which can significantly speed up the
        conversion. The number of values must correspond to the number of
        angles in the goniometer of the expclass
    constraints :   tuple
        sequence of constraint dictionaries. This allows applying arbitrary
        (e.g. pseudo-angle) contraints by supplying according constraint
        functions. (see scipy.optimize.minimize). The supplied function will be
        called with the arguments (angles, qvec, Experiment, U).

    Returns
    -------
    fittedangles :  list
        list of fitted goniometer angles
    qerror :        float
        error in reciprocal space
    errcode :       int
        error-code of the scipy minimize function. for a successful fit the
        error code should be <=2
    """

    # check input parameters
    config.EPSILON = 1e-7
    if len(qvec) != 3:
        raise ValueError("XU.Q2AngFit: length of given q-vector is not 3 "
                         "-> invalid")
    lqvec = numpy.asarray(qvec)

    qconv = expclass._A2QConversion
    nangles = len(qconv.sampleAxis) + len(qconv.detectorAxis)

    # generate starting position for optimization
    if startvalues is None:
        start = numpy.zeros(nangles)
    else:
        start = startvalues

    # check bounds
    if bounds is None:
        bounds = numpy.zeros(2 * nangles) - 180.
        bounds[::2] = 180.
        bounds.shape = (nangles, 2)
    elif len(bounds) != nangles:
        raise ValueError("XU.Q2AngFit: number of specified bounds invalid")

    # perform optimization
    res = scipy.optimize.minimize(_errornorm_q2ang, start,
                                  args=(lqvec, expclass, ormat),
                                  method='SLSQP', bounds=_makebounds(bounds),
                                  constraints=constraints,
                                  options={'maxiter': 200,
                                           'eps': config.EPSILON,
                                           'ftol': config.EPSILON})

    x, errcode, qerror = (res.x, res.status, res.fun)
    if qerror >= 1e-7:
        if config.VERBOSITY >= config.DEBUG:
            print("XU.Q2AngFit: info: need second run")
        # make a second run
        res = scipy.optimize.minimize(_errornorm_q2ang, res.x,
                                      args=(lqvec, expclass, ormat),
                                      method='SLSQP',
                                      bounds=_makebounds(bounds),
                                      constraints=constraints,
                                      options={'maxiter': 200,
                                               'eps': config.EPSILON,
                                               'ftol': config.EPSILON})
        x, errcode, qerror = (res.x, res.status, res.fun)

    # if ((config.VERBOSITY >= config.DEBUG) or (qerror > 10*config.EPSILON and
    #                                             config.VERBOSITY >=
    #                                             config.INFO_LOW)):
    #     print("XU.Q2AngFit: q-error=%.4g with error-code %d (%s)"
    #             % (qerror, errcode, res.message))

    return x, qerror, errcode