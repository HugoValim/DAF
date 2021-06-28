from os import path
from pydm import Display

import sys
import os
import daf
import numpy as np
import dafutilities as du
import yaml
import time
from PyQt5 import QtWidgets, QtGui, QtCore




DEFAULT = ".Experiment"

class MyDisplay(Display):

	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)

		self.update()

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(5000) #trigger 5 seconds.

# 
	def ui_filename(self):
		return 'main2.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def get_experiment_data(self, filepath=DEFAULT):
		with open(filepath) as file:
			data = yaml.safe_load(file)
		self.data = data
		return data

	def ret_list(self, string):

		return [float(i) for i in string.strip('][').split(', ')]


	def update(self):


		dict_args = du.read()
		Uw = dict_args['U_mat'].split(',')


		U1 = [float(i) for i in Uw[0].strip('][').split(' ') if i != '']
		U2 = [float(i) for i in Uw[1].strip('][').split(' ') if i != '']
		U3 = [float(i) for i in Uw[2].strip('][').split(' ') if i != '']
		U = np.array([U1, U2, U3])


		mode = [int(i) for i in dict_args['Mode']]
		idir = self.ret_list(dict_args['IDir'])
		ndir = self.ret_list(dict_args['NDir'])
		rdir = self.ret_list(dict_args['RDir'])

		exp = daf.Control(*mode)
		exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
		exp.set_material(dict_args['Material'], float(dict_args["lparam_a"]), float(dict_args["lparam_b"]), float(dict_args["lparam_c"]), float(dict_args["lparam_alpha"]), float(dict_args["lparam_beta"]), float(dict_args["lparam_gama"]))
		exp.set_U(U)
		hklnow = exp.calc_from_angs(float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"]))
		
		pseudo = exp.calc_pseudo(float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"]))
		pseudo_dict = {'alpha':pseudo[0], 'qaz':pseudo[1], 'naz':pseudo[2], 'tau':pseudo[3], 'psi':pseudo[4], 'beta':pseudo[5], 'omega':pseudo[6], 'hklnow':hklnow}



		hklnow = list(hklnow)


		lb = lambda x: "{:.5f}".format(float(x))

		self.get_experiment_data()

		# Update HKL pos labels
		self.ui.H_val.setText(str(lb(hklnow[0])))
		self.ui.K_val.setText(str(lb(hklnow[1])))
		self.ui.L_val.setText(str(lb(hklnow[2])))

		# Update pseudo-angle pos labels
		self.ui.label_alpha.setText(str(lb(pseudo_dict['alpha'])))
		self.ui.label_beta.setText(str(lb(pseudo_dict['beta'])))
		self.ui.label_psi.setText(str(lb(pseudo_dict['psi'])))
		self.ui.label_tau.setText(str(lb(pseudo_dict['tau'])))
		self.ui.label_qaz.setText(str(lb(pseudo_dict['qaz'])))
		self.ui.label_naz.setText(str(lb(pseudo_dict['naz'])))
		self.ui.label_omega.setText(str(lb(pseudo_dict['omega'])))





	    	



