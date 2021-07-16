from os import path
from pydm import Display
import os
import subprocess
import dafutilities as du
import xrayutilities as xu
import numpy as np

class MyDisplay(Display):


	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)



		self.update_reflections()
		self.ui.pushButton_refs_reset.clicked.connect(self.update_reflections)
		self.ui.pushButton_refs_save.clicked.connect(self.save_reflections)
		
		self.pushButton_2_ref_calc.clicked.connect(self.calc_from_2_ref)
		self.pushButton_3_ref_calc.clicked.connect(self.calc_from_3_ref)
		self.ui.frame_sample.setEnabled(False)
		self.ui.checkBox_sample.stateChanged.connect(self.sample_checkbox_state_changed)
		self.pushButton_sample.clicked.connect(self.set_new_sample)

		self.update_u_labels()
		self.ui.pushButton_reset_u.clicked.connect(self.update_u_labels)
		self.ui.pushButton_set_u.clicked.connect(self.set_u_matrix)


		self.update_ub_labels()
		self.ui.pushButton_reset_ub.clicked.connect(self.update_ub_labels)
		self.ui.pushButton_set_ub.clicked.connect(self.set_ub_matrix)


	def ui_filename(self):
		return 'ub.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def get_experiment_file(self):

		dict_args = du.read()
		return dict_args

	def ret_list(self, string):

		return [float(i) for i in string.strip('][').split(', ')]

	def format_decimals(self, x):
		return "{:.5f}".format(float(x)) # format float with 5 decimals

	def update_reflections(self):

		data = self.get_experiment_file()

		if data['hkl1'] != '':
			
			self.hkl1 = True
			r1 = self.ret_list(data['hkl1'])
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
			r2 = self.ret_list(data['hkl2'])
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
			r3 = self.ret_list(data['hkl3'])
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

	def sample_checkbox_state_changed(self):

		if self.ui.checkBox_sample.isChecked():
		    self.ui.frame_sample.setEnabled(True)
		else:
		    self.ui.frame_sample.setEnabled(False)

	def set_new_sample(self):

		samp_name = self.ui.lineEdit_sample.text()

		os.system("daf.expt -m {}".format(samp_name))




	def update_u_labels(self):

		data = self.get_experiment_file()

		Uw = data['U_mat'].split(',')


		U1 = [self.format_decimals(float(i)) for i in Uw[0].strip('][').split(' ') if i != '']
		U2 = [self.format_decimals(float(i)) for i in Uw[1].strip('][').split(' ') if i != '']
		U3 = [self.format_decimals(float(i)) for i in Uw[2].strip('][').split(' ') if i != '']
		U = np.array([U1, U2, U3])

		
		self.ui.lineEdit_u_00.setText(str(U[0][0]))
		self.ui.lineEdit_u_01.setText(str(U[0][1]))
		self.ui.lineEdit_u_02.setText(str(U[0][2]))
		self.ui.lineEdit_u_10.setText(str(U[1][0]))
		self.ui.lineEdit_u_11.setText(str(U[1][1]))
		self.ui.lineEdit_u_12.setText(str(U[1][2]))
		self.ui.lineEdit_u_20.setText(str(U[2][0]))
		self.ui.lineEdit_u_21.setText(str(U[2][1]))
		self.ui.lineEdit_u_22.setText(str(U[2][2]))

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

		UBw = data['UB_mat'].split(',')


		UB1 = [self.format_decimals(float(i)) for i in UBw[0].strip('][').split(' ') if i != '']
		UB2 = [self.format_decimals(float(i)) for i in UBw[1].strip('][').split(' ') if i != '']
		UB3 = [self.format_decimals(float(i)) for i in UBw[2].strip('][').split(' ') if i != '']
		UB = np.array([UB1, UB2, UB3])

		
		self.ui.lineEdit_ub_00.setText(str(UB[0][0]))
		self.ui.lineEdit_ub_01.setText(str(UB[0][1]))
		self.ui.lineEdit_ub_02.setText(str(UB[0][2]))
		self.ui.lineEdit_ub_10.setText(str(UB[1][0]))
		self.ui.lineEdit_ub_11.setText(str(UB[1][1]))
		self.ui.lineEdit_ub_12.setText(str(UB[1][2]))
		self.ui.lineEdit_ub_20.setText(str(UB[2][0]))
		self.ui.lineEdit_ub_21.setText(str(UB[2][1]))
		self.ui.lineEdit_ub_22.setText(str(UB[2][2]))

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
		os.system("daf.ub -UB {} {} {} {} {} {} {} {} {}".format(ub_00, ub_01, ub_02, ub_10, ub_11, ub_12, ub_20, ub_21, ub_22))





		






		
		
			



		
