#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse as ap
import sys
import os
import daf
import numpy as np
import dafutilities as du
import pandas as pd
import matplotlib.pyplot
doc = """

Move by setting a HKL or by a given diffractometer angle

"""

epi = "\n Eg: \n daf.move -mv 1 0 0, \n daf.move --Eta 15 -Del 30"


parser = ap.ArgumentParser(description=doc, epilog=epi)

# parser.add_argument('hkli', metavar='', type=float, nargs=3, help='Initial HKL for scan')
# parser.add_argument('hklf', metavar='', type=float, nargs=3, help='Final HKL for scan')
# parser.add_argument('points', metavar='', type=int, help='Number of points for the scan')
parser.add_argument('-n', '--scan_name', metavar='', type=str, help='Name of the scan')
parser.add_argument('-s', '--step', metavar='', type=float, help='Step for the scan')
parser.add_argument('-sep', '--separator', metavar='', type=str, help='Chose the separator of scan file, default: ,')
parser.add_argument('-m', '--Max_diff', metavar='', type=float, help='Max difference of angles variation, if 0 is given no verification will be done')
parser.add_argument('-v', '--verbose', action='store_true', help='Show full output')


args = parser.parse_args()
dic = vars(args)


matplotlib.pyplot.show(block=True)
with open('Experiment', 'r+') as exp:
 
    lines = exp.readlines()


 

    for i, line in enumerate(lines):
        for j,k in dic.items():
            

 

            if line.startswith(str(j)):
                if k != None:
                    lines[i] = str(j)+'='+str(k)+'\n'
          
            exp.seek(0)
            


 

    for line in lines:
        exp.write(line)


     
dict_args = du.dict_conv()
        
def ret_list(string):
    
    return [float(i) for i in string.strip('][').split(', ')]


Uw = dict_args['U_mat'].split(',')


U1 = [float(i) for i in Uw[0].strip('][').split(' ') if i != '']
U2 = [float(i) for i in Uw[1].strip('][').split(' ') if i != '']
U3 = [float(i) for i in Uw[2].strip('][').split(' ') if i != '']
U = np.array([U1, U2, U3])




    
mode = [int(i) for i in dict_args['Mode']]    
idir = ret_list(dict_args['IDir'])
ndir = ret_list(dict_args['NDir'])
Mu_bound = ret_list(dict_args['bound_Mu'])
Eta_bound = ret_list(dict_args['bound_Eta'])
Chi_bound = ret_list(dict_args['bound_Chi'])
Phi_bound = ret_list(dict_args['bound_Phi'])
Nu_bound = ret_list(dict_args['bound_Nu'])
Del_bound = ret_list(dict_args['bound_Del'])

exp = daf.Control(*mode)
exp.set_hkl([1, 0,0])
exp.set_material(dict_args['Material'])
exp.set_exp_conditions(idir = idir, ndir = ndir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
exp.set_U(U)
exp.set_constraints(Mu = float(dict_args['cons_Mu']), Eta = float(dict_args['cons_Eta']), Chi = float(dict_args['cons_Chi']), Phi = float(dict_args['cons_Phi']),
                    Nu = float(dict_args['cons_Nu']), Del = float(dict_args['cons_Del']), alpha = float(dict_args['cons_alpha']), beta = float(dict_args['cons_beta']),
                    psi = float(dict_args['cons_psi']), omega = float(dict_args['cons_omega']), qaz = float(dict_args['cons_qaz']), naz = float(dict_args['cons_naz']))




startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]

#
# exp.scan(args.hkli, args.hklf, args.points, diflimit = float(dict_args['Max_diff']), name = dict_args['scan_name'], write=True, sep=dict_args['separator'])

startvalue = [float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"])]

exp(sv = startvalue)
exp.show_reciprocal_space_plane(ttmax = 160)

def show_reciprocal_space_plane(self, ttmax=None, maxqout=0.01, scalef=100, ax=None, color=None,
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
    exp = exp.hrxrd
    mat = dict_args['Material']
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
        except ImportError:
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
            # print(h.contains(event))
            if cont:
                popts = numpy.get_printoptions()
                numpy.set_printoptions(precision=4, suppress=True)
                # print(d['qvec'][m][ind['ind'][0]])
         
                ang = Control.motor_angles(self, qvec = d['qvec'][m][ind['ind'][0]])
                angles = [np.round(ang[0][0], 4), np.round(ang[0][1], 4), np.round(ang[0][2], 4), np.round(ang[0][3], 4), np.round(ang[0][4], 4), np.round(ang[0][5], 4), float(ang[0][-1])]
           
                text = "{}\nhkl: {}\nangles: {}".format(
                    mat.name, str(d['hkl'][m][ind['ind'][0]]), str(angles))
                numpy.set_printoptions(**popts)
                print(text)

    fig.canvas.mpl_connect("motion_notify_event", hover)
    fig.canvas.mpl_connect("button_press_event", click)
    plt.show(block=True)
    return ax, h
    
if args.verbose:
    pd.options.display.max_rows = None
    pd.options.display.max_columns = 0
     
    print(exp)


log = sys.argv.pop(0).split('command_line/')[1]    

for i in sys.argv:
    log += ' ' + i

os.system(f"echo {log} >> Log")

if dict_args['macro_flag'] == 'True':
    os.system(f"echo {log} >> {dict_args['macro_file']}")