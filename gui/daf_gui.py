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
from PyQt5.QtCore import QObject, QThread, pyqtSignal



DEFAULT = ".Experiment"

# global data_to_update # This variable holds the data processed in another Qthread and then the labels are updated in MyDisplay class

class Worker(QObject):
	finished = pyqtSignal()
	update_labels = pyqtSignal()

	
	def get_experiment_data(self, filepath=DEFAULT):
		with open(filepath) as file:
			data = yaml.safe_load(file)
		
		return data

	def ret_list(self, string):

		return [float(i) for i in string.strip('][').split(', ')]

	def call_update(self):

		data = self.get_experiment_data()
		if data != self.data:
			self.update()
			self.data = data


	def update(self):


		dict_args = du.read()
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


		mode = [int(i) for i in dict_args['Mode']]
		idir = self.ret_list(dict_args['IDir'])
		ndir = self.ret_list(dict_args['NDir'])
		rdir = self.ret_list(dict_args['RDir'])

		exp = daf.Control(*mode)
		exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = float(dict_args['Energy']), sampleor = dict_args['Sampleor'])
		exp.set_material(dict_args['Material'], float(dict_args["lparam_a"]), float(dict_args["lparam_b"]), float(dict_args["lparam_c"]), float(dict_args["lparam_alpha"]), float(dict_args["lparam_beta"]), float(dict_args["lparam_gama"]))
		exp.set_U(U)
		exp.set_constraints(Mu = float(dict_args['cons_Mu']), Eta = float(dict_args['cons_Eta']), Chi = float(dict_args['cons_Chi']), Phi = float(dict_args['cons_Phi']),
                    Nu = float(dict_args['cons_Nu']), Del = float(dict_args['cons_Del']), alpha = float(dict_args['cons_alpha']), beta = float(dict_args['cons_beta']),
                    psi = float(dict_args['cons_psi']), omega = float(dict_args['cons_omega']), qaz = float(dict_args['cons_qaz']), naz = float(dict_args['cons_naz']))
		
		hklnow = exp.calc_from_angs(float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"]))

		pseudo = exp.calc_pseudo(float(dict_args["Mu"]), float(dict_args["Eta"]), float(dict_args["Chi"]), float(dict_args["Phi"]), float(dict_args["Nu"]), float(dict_args["Del"]))
		pseudo_dict = {'alpha':pseudo[0], 'qaz':pseudo[1], 'naz':pseudo[2], 'tau':pseudo[3], 'psi':pseudo[4], 'beta':pseudo[5], 'omega':pseudo[6], 'hklnow':hklnow}



		hklnow = list(hklnow)

		mode, mode_num, cons, exp_list, samp_info = exp.show(sh = 'gui')

		bounds = {'mu' : dict_args["bound_Mu"], 
		'eta': dict_args["bound_Eta"],
		'chi' : dict_args["bound_Chi"],
		'phi' : dict_args["bound_Phi"],
		'nu' : dict_args["bound_Nu"],
		'del' : dict_args["bound_Del"]}

		global data_to_update # This variable holds the data processed in another Qthread and then the labels are updated in MyDisplay class
		
		data_to_update = {'hklnow' : hklnow, 'mode' : mode, 'mode_num' : mode_num, 'cons' : cons, 'exp_list' : exp_list, 'samp_info' : samp_info,
							'U' : U, 'UB' : UB, 'bounds' : bounds , 'pseudo_dict' : pseudo_dict}

		

	def run(self):
		"""Long-running task."""
		while True:
			self.update()
			self.update_labels.emit()
			time.sleep(1)


class MyDisplay(Display):

	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)

		self.runLongTask()
	
	def runLongTask(self):
		# Step 2: Create a QThread object
		self.thread = QThread()
		# Step 3: Create a worker object
		self.worker = Worker()
		# Step 4: Move worker to the thread
		self.worker.moveToThread(self.thread)
		# Step 5: Connect signals and slots
		self.thread.started.connect(self.worker.run)
		self.thread.start()
		self.worker.update_labels.connect(self.update)

	def ui_filename(self):
		return 'main.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def update(self):

		lb = lambda x: "{:.5f}".format(float(x)) # format float with 5 decimals

		# Update HKL pos labels
		self.ui.H_val.setText(str(lb(data_to_update['hklnow'][0])))
		self.ui.K_val.setText(str(lb(data_to_update['hklnow'][1])))
		self.ui.L_val.setText(str(lb(data_to_update['hklnow'][2])))

		# Update pseudo-angle pos labels
		self.ui.label_alpha.setText(str(lb(data_to_update['pseudo_dict']['alpha'])))
		self.ui.label_beta.setText(str(lb(data_to_update['pseudo_dict']['beta'])))
		self.ui.label_psi.setText(str(lb(data_to_update['pseudo_dict']['psi'])))
		self.ui.label_tau.setText(str(lb(data_to_update['pseudo_dict']['tau'])))
		self.ui.label_qaz.setText(str(lb(data_to_update['pseudo_dict']['qaz'])))
		self.ui.label_naz.setText(str(lb(data_to_update['pseudo_dict']['naz'])))
		self.ui.label_omega.setText(str(lb(data_to_update['pseudo_dict']['omega'])))

		# Update status mode label
		mode_text = 'MODE: ' + str(data_to_update['mode_num'][0])+str(data_to_update['mode_num'][1])+str(data_to_update['mode_num'][2])+str(data_to_update['mode_num'][3])+str(data_to_update['mode_num'][4])
		self.ui.label_mode.setText(mode_text)
		self.ui.label_mode1.setText(data_to_update['mode'][0])
		self.ui.label_mode2.setText(data_to_update['mode'][1])
		self.ui.label_mode3.setText(data_to_update['mode'][2])
		self.ui.label_mode4.setText(data_to_update['mode'][3])
		self.ui.label_mode5.setText(data_to_update['mode'][4])

		# Update status constraints label
		self.ui.label_cons1.setText(str(data_to_update['cons'][0][1]))
		self.ui.label_cons2.setText(str(data_to_update['cons'][1][1]))
		self.ui.label_cons3.setText(str(data_to_update['cons'][2][1]))
		self.ui.label_cons4.setText(str(data_to_update['cons'][3][1]))
		self.ui.label_cons5.setText(str(data_to_update['cons'][4][1]))

		# Update status experiment label
		self.ui.label_exp1.setText(str(data_to_update['exp_list'][0]))
		self.ui.label_exp2.setText(str(data_to_update['exp_list'][1]))
		self.ui.label_exp3.setText(str(data_to_update['exp_list'][2]))
		self.ui.label_exp4.setText(str(data_to_update['exp_list'][3]))
		self.ui.label_exp5.setText(str(data_to_update['exp_list'][4]))
		self.ui.label_exp6.setText(str(data_to_update['exp_list'][5]))

		# Update sample info label
		self.ui.label_samp_name.setText(str(data_to_update['samp_info'][0]))
		self.ui.label_samp_a.setText(str(data_to_update['samp_info'][1]))
		self.ui.label_samp_b.setText(str(data_to_update['samp_info'][2]))
		self.ui.label_samp_c.setText(str(data_to_update['samp_info'][3]))
		self.ui.label_samp_alpha.setText(str(data_to_update['samp_info'][4]))
		self.ui.label_samp_beta.setText(str(data_to_update['samp_info'][5]))
		self.ui.label_samp_gamma.setText(str(data_to_update['samp_info'][6]))
		

		#Update status Matrixes label

		#U
		self.ui.label_u00.setText(str(data_to_update['U'][0][0]))
		self.ui.label_u01.setText(str(data_to_update['U'][0][1]))
		self.ui.label_u02.setText(str(data_to_update['U'][0][2]))
		self.ui.label_u10.setText(str(data_to_update['U'][1][0]))
		self.ui.label_u11.setText(str(data_to_update['U'][1][1]))
		self.ui.label_u12.setText(str(data_to_update['U'][1][2]))
		self.ui.label_u20.setText(str(data_to_update['U'][2][0]))
		self.ui.label_u21.setText(str(data_to_update['U'][2][1]))
		self.ui.label_u22.setText(str(data_to_update['U'][2][2]))

		#UB
		self.ui.label_ub00.setText(str(data_to_update['UB'][0][0]))
		self.ui.label_ub01.setText(str(data_to_update['UB'][0][1]))
		self.ui.label_ub02.setText(str(data_to_update['UB'][0][2]))
		self.ui.label_ub10.setText(str(data_to_update['UB'][1][0]))
		self.ui.label_ub11.setText(str(data_to_update['UB'][1][1]))
		self.ui.label_ub12.setText(str(data_to_update['UB'][1][2]))
		self.ui.label_ub20.setText(str(data_to_update['UB'][2][0]))
		self.ui.label_ub21.setText(str(data_to_update['UB'][2][1]))
		self.ui.label_ub22.setText(str(data_to_update['UB'][2][2]))

		#Update motor bounds


		self.ui.label_mu_bounds.setText(data_to_update['bounds']["mu"])
		self.ui.label_eta_bounds.setText(data_to_update['bounds']["eta"])
		self.ui.label_chi_bounds.setText(data_to_update['bounds']["chi"])
		self.ui.label_phi_bounds.setText(data_to_update['bounds']["phi"])
		self.ui.label_nu_bounds.setText(data_to_update['bounds']["nu"])
		self.ui.label_del_bounds.setText(data_to_update['bounds']["del"])
		











	    	



