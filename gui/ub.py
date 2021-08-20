from os import path
from pydm import Display
import os
import subprocess
import dafutilities as du
import xrayutilities as xu
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

class MyDisplay(Display):


	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)



		self.update_reflections()
		self.ui.pushButton_refs_reset.clicked.connect(self.update_reflections)
		self.ui.pushButton_refs_save.clicked.connect(self.save_reflections)
		
		self.pushButton_2_ref_calc.clicked.connect(self.calc_from_2_ref)
		self.pushButton_3_ref_calc.clicked.connect(self.calc_from_3_ref)
		self.pushButton_sample.clicked.connect(self.set_new_sample)

		# Umat
		self.update_u_labels()
		self.ui.pushButton_reset_u.clicked.connect(self.update_u_labels)
		self.ui.pushButton_set_u.clicked.connect(self.set_u_matrix)

		# UBmat
		self.update_ub_labels()
		self.ui.pushButton_reset_ub.clicked.connect(self.update_ub_labels)
		self.ui.pushButton_set_ub.clicked.connect(self.set_ub_matrix)

		self.set_tab_order()

	def ui_filename(self):
		return 'ub.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def set_tab_order(self):

		# Calc UB
		self.setTabOrder(self.ui.tab_calcUB, self.ui.lineEdit_h_1)
		self.setTabOrder(self.ui.lineEdit_h_1, self.ui.lineEdit_k_1)
		self.setTabOrder(self.ui.lineEdit_k_1, self.ui.lineEdit_l_1)
		self.setTabOrder(self.ui.lineEdit_l_1, self.ui.lineEdit_mu_1)
		self.setTabOrder(self.ui.lineEdit_mu_1, self.ui.lineEdit_eta_1)
		self.setTabOrder(self.ui.lineEdit_eta_1, self.ui.lineEdit_chi_1)
		self.setTabOrder(self.ui.lineEdit_chi_1, self.ui.lineEdit_phi_1)
		self.setTabOrder(self.ui.lineEdit_phi_1, self.ui.lineEdit_nu_1)
		self.setTabOrder(self.ui.lineEdit_nu_1, self.ui.lineEdit_del_1)
		self.setTabOrder(self.ui.lineEdit_del_1, self.ui.lineEdit_h_2)
		self.setTabOrder(self.ui.lineEdit_h_2, self.ui.lineEdit_k_2)
		self.setTabOrder(self.ui.lineEdit_k_2, self.ui.lineEdit_l_2)
		self.setTabOrder(self.ui.lineEdit_l_2, self.ui.lineEdit_mu_2)
		self.setTabOrder(self.ui.lineEdit_mu_2, self.ui.lineEdit_eta_2)
		self.setTabOrder(self.ui.lineEdit_eta_2, self.ui.lineEdit_chi_2)
		self.setTabOrder(self.ui.lineEdit_chi_2, self.ui.lineEdit_phi_2)
		self.setTabOrder(self.ui.lineEdit_phi_2, self.ui.lineEdit_nu_2)
		self.setTabOrder(self.ui.lineEdit_nu_2, self.ui.lineEdit_del_2)
		self.setTabOrder(self.ui.lineEdit_del_2, self.ui.lineEdit_h_3)
		self.setTabOrder(self.ui.lineEdit_h_3, self.ui.lineEdit_k_3)
		self.setTabOrder(self.ui.lineEdit_k_3, self.ui.lineEdit_l_3)
		self.setTabOrder(self.ui.lineEdit_l_3, self.ui.lineEdit_mu_3)
		self.setTabOrder(self.ui.lineEdit_mu_3, self.ui.lineEdit_eta_3)
		self.setTabOrder(self.ui.lineEdit_eta_3, self.ui.lineEdit_chi_3)
		self.setTabOrder(self.ui.lineEdit_chi_3, self.ui.lineEdit_phi_3)
		self.setTabOrder(self.ui.lineEdit_phi_3, self.ui.lineEdit_nu_3)
		self.setTabOrder(self.ui.lineEdit_nu_3, self.ui.lineEdit_del_3)
		self.setTabOrder(self.ui.lineEdit_del_3, self.ui.pushButton_refs_save)
		self.setTabOrder(self.ui.pushButton_refs_save, self.ui.pushButton_refs_reset)
		self.setTabOrder(self.ui.pushButton_refs_reset, self.ui.comboBox_2_ref)
		self.setTabOrder(self.ui.comboBox_2_ref, self.ui.pushButton_2_ref_calc)
		self.setTabOrder(self.ui.pushButton_2_ref_calc, self.ui.pushButton_3_ref_calc)
		self.setTabOrder(self.ui.pushButton_3_ref_calc, self.ui.pushButton_sample)
		self.setTabOrder(self.ui.pushButton_sample, self.ui.tab_calcUB)
		
		# Set U and UB
		self.setTabOrder(self.ui.tab_UB, self.ui.lineEdit_u_00)
		self.setTabOrder(self.ui.lineEdit_u_00, self.ui.lineEdit_u_01)
		self.setTabOrder(self.ui.lineEdit_u_01, self.ui.lineEdit_u_02)
		self.setTabOrder(self.ui.lineEdit_u_02, self.ui.lineEdit_u_10)
		self.setTabOrder(self.ui.lineEdit_u_10, self.ui.lineEdit_u_11)
		self.setTabOrder(self.ui.lineEdit_u_11, self.ui.lineEdit_u_12)
		self.setTabOrder(self.ui.lineEdit_u_12, self.ui.lineEdit_u_20)
		self.setTabOrder(self.ui.lineEdit_u_20, self.ui.lineEdit_u_21)
		self.setTabOrder(self.ui.lineEdit_u_21, self.ui.lineEdit_u_22)
		self.setTabOrder(self.ui.lineEdit_u_22, self.ui.pushButton_set_u)
		self.setTabOrder(self.ui.pushButton_set_u, self.ui.pushButton_reset_u)
		self.setTabOrder(self.ui.pushButton_reset_u, self.ui.lineEdit_ub_00)
		self.setTabOrder(self.ui.lineEdit_ub_00, self.ui.lineEdit_ub_01)
		self.setTabOrder(self.ui.lineEdit_ub_01, self.ui.lineEdit_ub_02)
		self.setTabOrder(self.ui.lineEdit_ub_02, self.ui.lineEdit_ub_10)
		self.setTabOrder(self.ui.lineEdit_ub_10, self.ui.lineEdit_ub_11)
		self.setTabOrder(self.ui.lineEdit_ub_11, self.ui.lineEdit_ub_12)
		self.setTabOrder(self.ui.lineEdit_ub_12, self.ui.lineEdit_ub_20)
		self.setTabOrder(self.ui.lineEdit_ub_20, self.ui.lineEdit_ub_21)
		self.setTabOrder(self.ui.lineEdit_ub_21, self.ui.lineEdit_ub_22)
		self.setTabOrder(self.ui.lineEdit_ub_22, self.ui.pushButton_set_ub)
		self.setTabOrder(self.ui.pushButton_set_ub, self.ui.pushButton_reset_ub)
		self.setTabOrder(self.ui.pushButton_reset_ub, self.ui.tab_UB)


	def get_experiment_file(self):

		dict_args = du.read()
		return dict_args

	def format_decimals(self, x):
		return "{:.5f}".format(float(x)) # format float with 5 decimals

	def update_reflections(self):

		data = self.get_experiment_file()

		if data['hkl1'] != '':
			
			self.hkl1 = True
			r1 = data['hkl1']
			hkl1 = r1[:3]
			angs1 = r1[3:9]

			self.ui.lineEdit_h_1.setText(str(hkl1[0]))
			self.ui.lineEdit_k_1.setText(str(hkl1[1]))
			self.ui.lineEdit_l_1.setText(str(hkl1[2]))

			self.ui.lineEdit_mu_1.setText(str(angs1[0]))
			self.ui.lineEdit_eta_1.setText(str(angs1[1]))
			self.ui.lineEdit_chi_1.setText(str(angs1[2]))
			self.ui.lineEdit_phi_1.setText(str(angs1[3]))
			self.ui.lineEdit_nu_1.setText(str(angs1[4]))
			self.ui.lineEdit_del_1.setText(str(angs1[5]))
		

		else:
			self.hkl1 = False


		if data['hkl2'] != '':
			
			self.hkl2 = True
			r2 = data['hkl2']
			hkl2 = r2[:3] 
			angs2 = r2[3:9]

			self.ui.lineEdit_h_2.setText(str(hkl2[0]))
			self.ui.lineEdit_k_2.setText(str(hkl2[1]))
			self.ui.lineEdit_l_2.setText(str(hkl2[2]))

			self.ui.lineEdit_mu_2.setText(str(angs2[0]))
			self.ui.lineEdit_eta_2.setText(str(angs2[1]))
			self.ui.lineEdit_chi_2.setText(str(angs2[2]))
			self.ui.lineEdit_phi_2.setText(str(angs2[3]))
			self.ui.lineEdit_nu_2.setText(str(angs2[4]))
			self.ui.lineEdit_del_2.setText(str(angs2[5]))
			
		

		else:
			self.hkl2 = False

		if data['hkl3'] != '':
			
			self.hkl3 = True
			r3 = data['hkl3']
			hkl3 = r3[:3]
			angs3 = r3[3:9]

			self.ui.lineEdit_h_3.setText(str(hkl3[0]))
			self.ui.lineEdit_k_3.setText(str(hkl3[1]))
			self.ui.lineEdit_l_3.setText(str(hkl3[2]))

			self.ui.lineEdit_mu_3.setText(str(angs3[0]))
			self.ui.lineEdit_eta_3.setText(str(angs3[1]))
			self.ui.lineEdit_chi_3.setText(str(angs3[2]))
			self.ui.lineEdit_phi_3.setText(str(angs3[3]))
			self.ui.lineEdit_nu_3.setText(str(angs3[4]))
			self.ui.lineEdit_del_3.setText(str(angs3[5]))
		

		else:
			self.hkl3 = False

	def save_reflections(self):

		# Reflection 1
		h1 = self.ui.lineEdit_h_1.text()
		k1 = self.ui.lineEdit_k_1.text()
		l1 = self.ui.lineEdit_l_1.text()

		mu1 = self.ui.lineEdit_mu_1.text()
		eta1 = self.ui.lineEdit_eta_1.text()
		chi1 = self.ui.lineEdit_chi_1.text()
		phi1 = self.ui.lineEdit_phi_1.text()
		nu1 = self.ui.lineEdit_nu_1.text()
		del1 = self.ui.lineEdit_del_1.text()


		# Reflection2
		h2 = self.ui.lineEdit_h_2.text()
		k2 = self.ui.lineEdit_k_2.text()
		l2 = self.ui.lineEdit_l_2.text()

		mu2 = self.ui.lineEdit_mu_2.text()
		eta2 = self.ui.lineEdit_eta_2.text()
		chi2 = self.ui.lineEdit_chi_2.text()
		phi2 = self.ui.lineEdit_phi_2.text()
		nu2 = self.ui.lineEdit_nu_2.text()
		del2 = self.ui.lineEdit_del_2.text()


		#Reflection3
		h3 = self.ui.lineEdit_h_3.text()
		k3 = self.ui.lineEdit_k_3.text()
		l3 = self.ui.lineEdit_l_3.text()

		mu3 = self.ui.lineEdit_mu_3.text()
		eta3 = self.ui.lineEdit_eta_3.text()
		chi3 = self.ui.lineEdit_chi_3.text()
		phi3 = self.ui.lineEdit_phi_3.text()
		nu3 = self.ui.lineEdit_nu_3.text()
		del3 = self.ui.lineEdit_del_3.text()


		# if self.hkl1:
		# 	print("daf.ub -r1 {} {} {} {} {} {} {} {} {}".format(h1, k1, l1, mu1, eta1, chi1, phi1, nu1, del1))
		# 	os.system("daf.ub -r1 {} {} {} {} {} {} {} {} {}".format(h1, k1, l1, mu1, eta1, chi1, phi1, nu1, del1))

		# if self.hkl2:
		# 	os.system("daf.ub -r2 {} {} {} {} {} {} {} {} {}".format(h2, k2, l2, mu2, eta2, chi2, phi2, nu2, del2))

		# if self.hkl3:
		# 	os.system("daf.ub -r3 {} {} {} {} {} {} {} {} {}".format(h3, k3, l3, mu3, eta3, chi3, phi3, nu3, del3))

		os.system("daf.ub -r1 {} {} {} {} {} {} {} {} {} -r2 {} {} {} {} {} {} {} {} {} -r3 {} {} {} {} {} {} {} {} {}".format(h1, k1, l1, mu1, eta1, chi1, phi1, nu1, del1, h2, k2, l2, mu2, eta2, chi2, phi2, nu2, del2, h3, k3, l3, mu3, eta3, chi3, phi3, nu3, del3))




	def calc_from_2_ref(self):

		self.save_reflections()

		refs_to_use = self.ui.comboBox_2_ref.currentText().split(',')

		os.system("daf.ub -c2 {} {}".format(refs_to_use[0], refs_to_use[1]))



	def calc_from_3_ref(self):

		data = self.get_experiment_file()
		
		self.save_reflections()

		os.system("daf.ub -c3")

		self.label_a.setText(self.format_decimals(data['lparam_a']))
		self.label_b.setText(self.format_decimals(data['lparam_b']))
		self.label_c.setText(self.format_decimals(data['lparam_c']))
		self.label_alpha.setText(self.format_decimals(data['lparam_alpha']))
		self.label_beta.setText(self.format_decimals(data['lparam_beta']))
		self.label_gamma.setText(self.format_decimals(data['lparam_gama']))

	def set_new_sample(self):
		dict_args = du.read()
		samples = dict_args['user_samples']
		text, result = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'New config file name')
		
		if result:
			if text in samples.keys():
				msgbox = QtWidgets.QMessageBox()
				msgbox_text = 'This samples name {} already exists, \ndo you want to overwrite it?'.format(text)
				ret = msgbox.question(self, 'Warning', msgbox_text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)

				if ret == QtWidgets.QMessageBox.Ok:
					os.system("daf.expt -m {}".format(text))

			else:
				os.system("daf.expt -m {}".format(text))

	def update_u_labels(self):

		data = self.get_experiment_file()
		
		U = np.array(data['U_mat'])

		
		self.ui.lineEdit_u_00.setText(self.format_decimals(str(U[0][0])))
		self.ui.lineEdit_u_01.setText(self.format_decimals(str(U[0][1])))
		self.ui.lineEdit_u_02.setText(self.format_decimals(str(U[0][2])))
		self.ui.lineEdit_u_10.setText(self.format_decimals(str(U[1][0])))
		self.ui.lineEdit_u_11.setText(self.format_decimals(str(U[1][1])))
		self.ui.lineEdit_u_12.setText(self.format_decimals(str(U[1][2])))
		self.ui.lineEdit_u_20.setText(self.format_decimals(str(U[2][0])))
		self.ui.lineEdit_u_21.setText(self.format_decimals(str(U[2][1])))
		self.ui.lineEdit_u_22.setText(self.format_decimals(str(U[2][2])))

	def set_u_matrix(self):

		u_00 = self.ui.lineEdit_u_00.text()
		u_01 = self.ui.lineEdit_u_01.text()
		u_02 = self.ui.lineEdit_u_02.text()
		u_10 = self.ui.lineEdit_u_10.text()
		u_11 = self.ui.lineEdit_u_11.text()
		u_12 = self.ui.lineEdit_u_12.text()
		u_20 = self.ui.lineEdit_u_20.text()
		u_21 = self.ui.lineEdit_u_21.text()
		u_22 = self.ui.lineEdit_u_22.text()
		
		# print("daf.expt -m {} -p {} {} {} {} {} {}".format(samp, a, b, c, alpha, beta, gamma))
		# subprocess.Popen("daf.ub -U {} {} {} {} {} {} {} {} {}".format(u_00, u_01, u_02, u_10, u_11, u_12, u_20, u_21, u_22), shell = True)
		os.system("daf.ub -U {} {} {} {} {} {} {} {} {}".format(u_00, u_01, u_02, u_10, u_11, u_12, u_20, u_21, u_22))
		# Whenever U changes UB changes as well, since UB depend from U
		self.update_ub_labels()


	def update_ub_labels(self):

		data = self.get_experiment_file()

		UB = np.array(data['UB_mat'])

		
		self.ui.lineEdit_ub_00.setText(self.format_decimals(str(UB[0][0])))
		self.ui.lineEdit_ub_01.setText(self.format_decimals(str(UB[0][1])))
		self.ui.lineEdit_ub_02.setText(self.format_decimals(str(UB[0][2])))
		self.ui.lineEdit_ub_10.setText(self.format_decimals(str(UB[1][0])))
		self.ui.lineEdit_ub_11.setText(self.format_decimals(str(UB[1][1])))
		self.ui.lineEdit_ub_12.setText(self.format_decimals(str(UB[1][2])))
		self.ui.lineEdit_ub_20.setText(self.format_decimals(str(UB[2][0])))
		self.ui.lineEdit_ub_21.setText(self.format_decimals(str(UB[2][1])))
		self.ui.lineEdit_ub_22.setText(self.format_decimals(str(UB[2][2])))

	def set_ub_matrix(self):

		ub_00 = self.ui.lineEdit_ub_00.text()
		ub_01 = self.ui.lineEdit_ub_01.text()
		ub_02 = self.ui.lineEdit_ub_02.text()
		ub_10 = self.ui.lineEdit_ub_10.text()
		ub_11 = self.ui.lineEdit_ub_11.text()
		ub_12 = self.ui.lineEdit_ub_12.text()
		ub_20 = self.ui.lineEdit_ub_20.text()
		ub_21 = self.ui.lineEdit_ub_21.text()
		ub_22 = self.ui.lineEdit_ub_22.text()
		
		# print("daf.expt -m {} -p {} {} {} {} {} {}".format(samp, a, b, c, alpha, beta, gamma))
		print("daf.ub -UB {} {} {} {} {} {} {} {} {}".format(ub_00, ub_01, ub_02, ub_10, ub_11, ub_12, ub_20, ub_21, ub_22))
		os.system("daf.ub -UB {} {} {} {} {} {} {} {} {}".format(ub_00, ub_01, ub_02, ub_10, ub_11, ub_12, ub_20, ub_21, ub_22))





		






		
		
			



		
