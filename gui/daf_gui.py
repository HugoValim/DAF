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
		self.timer.start(6000) #trigger every minute.


	def ui_filename(self):
		return 'main.ui'

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
		hklnow = list(hklnow)


		lb = lambda x: "{:.5f}".format(float(x))

		self.get_experiment_data()
		self.ui.H_val.setText(str(hkl_now[0]))
		self.ui.K_val.setText(str(hkl_now[1]))
		self.ui.L_val.setText(str(hkl_now[2]))


	    	



