from os import path
from pydm import Display
import os
import subprocess
import dafutilities as du
import xrayutilities as xu

class MyDisplay(Display):

	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)

		self.ui.pushButton_reset.clicked.connect(self.set_labels)
		self.ui.pushButton_set.clicked.connect(self.set_new_exp_conditions)
		self.ui.comboBox_sor.currentTextChanged.connect(self.on_combobox_sor_changed)
		self.ui.comboBox_e_wl.currentTextChanged.connect(self.on_combobox_en_changed)


		self.set_labels()
# 
	def ui_filename(self):
		return 'experiment.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def get_experiment_file(self):

		dict_args = du.read()
		return dict_args

	def ret_list(self, string):

		return [float(i) for i in string.strip('][').split(', ')]

	def on_combobox_sor_changed(self):

		self.ui.lineEdit_sor.setText(self.ui.comboBox_sor.currentText())

	def on_combobox_en_changed(self):

		dict_args = self.get_experiment_file()

		if str(self.ui.comboBox_e_wl.currentText()).lower() == 'energy':
			
			self.ui.lineEdit_e_wl.setText(dict_args['Energy'])
		
		elif str(self.ui.comboBox_e_wl.currentText()).lower() == 'wave length':
			
			# lb = lambda x: "{:.5f}".format(float(x))
			wl = xu.en2lam(float(dict_args['Energy']))
			self.ui.lineEdit_e_wl.setText(str(wl))

	def set_labels(self):

		dict_args = self.get_experiment_file()
		

		self.ui.lineEdit_sor.setText(dict_args['Sampleor'])

		if str(self.ui.comboBox_e_wl.currentText()).lower() == 'energy':
			
			self.ui.lineEdit_e_wl.setText(dict_args['Energy'])
		
		elif str(self.ui.comboBox_e_wl.currentText()).lower() == 'wave length':
			
			# lb = lambda x: "{:.5f}".format(float(x))
			wl = xu.en2lam(float(dict_args['Energy']))
			self.ui.lineEdit_e_wl.setText(str(wl))

		idir = self.ret_list(dict_args['IDir'])
		self.ui.lineEdit_i_1.setText(str(idir[0]))
		self.ui.lineEdit_i_2.setText(str(idir[1]))
		self.ui.lineEdit_i_3.setText(str(idir[2]))

		ndir = self.ret_list(dict_args['NDir'])
		self.ui.lineEdit_n_1.setText(str(ndir[0]))
		self.ui.lineEdit_n_2.setText(str(ndir[1]))
		self.ui.lineEdit_n_3.setText(str(ndir[2]))

		rdir = self.ret_list(dict_args['RDir'])
		self.ui.lineEdit_r_1.setText(str(rdir[0]))
		self.ui.lineEdit_r_2.setText(str(rdir[1]))
		self.ui.lineEdit_r_3.setText(str(rdir[2]))

	def set_new_exp_conditions(self):

		sampleor = self.ui.lineEdit_sor.text()

		if str(self.ui.comboBox_e_wl.currentText()).lower() == 'energy':
			
			energy = self.ui.lineEdit_e_wl.text()
		
		elif str(self.ui.comboBox_e_wl.currentText()).lower() == 'wave length':
			
			energy = xu.lam2en(float(self.ui.lineEdit_e_wl.text()))

		idir = self.ui.lineEdit_i_1.text() + ' ' + self.ui.lineEdit_i_2.text() + ' ' + self.ui.lineEdit_i_3.text()

		ndir = self.ui.lineEdit_n_1.text() + ' ' + self.ui.lineEdit_n_2.text() + ' ' + self.ui.lineEdit_n_3.text()

		rdir = self.ui.lineEdit_r_1.text() + ' ' + self.ui.lineEdit_r_2.text() + ' ' + self.ui.lineEdit_r_3.text() 

		# print("daf.expt -e {energy} -s {sampleor} -i {idir} -n {ndir} -r {rdir}".format(energy=energy, sampleor=sampleor, idir=idir, ndir=ndir, rdir=rdir))
		subprocess.Popen("daf.expt -e {energy} -s {sampleor} -i {idir} -n {ndir} -r {rdir}".format(energy=energy, sampleor=sampleor, idir=idir, ndir=ndir, rdir=rdir), shell = True)
		
			



		
