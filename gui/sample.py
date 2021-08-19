from os import path
from pydm import Display
import os
import subprocess
import dafutilities as du
import xrayutilities as xu
from PyQt5 import QtWidgets, QtGui, QtCore

class MyDisplay(Display):


	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)


		self.set_combobox_options()
		self.set_comboBox_materials_default()
		self.ui.frame_new_mat.setEnabled(False)
		self.ui.checkBox_new_mat.stateChanged.connect(self.checkbox_state_changed)
		self.ui.pushButton_set.clicked.connect(self.set_sample)
		self.ui.pushButton_set.clicked.connect(self.set_combobox_options)
		self.ui.pushButton_set.clicked.connect(self.set_comboBox_materials_default)
		self.set_tab_order()

	def ui_filename(self):
		return 'sample.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def set_tab_order(self):
		self.setTabOrder(self.ui.lineEdit_samp_name, self.ui.lineEdit_a)
		self.setTabOrder(self.ui.lineEdit_a, self.ui.lineEdit_b)
		self.setTabOrder(self.ui.lineEdit_b, self.ui.lineEdit_c)
		self.setTabOrder(self.ui.lineEdit_c, self.ui.lineEdit_alpha)
		self.setTabOrder(self.ui.lineEdit_alpha, self.ui.lineEdit_beta)
		self.setTabOrder(self.ui.lineEdit_beta, self.ui.lineEdit_gamma)
		self.setTabOrder(self.ui.lineEdit_gamma, self.ui.pushButton_set)

	def get_experiment_file(self):

		dict_args = du.read()
		return dict_args

	def materials(self):

		materials = {'Si':xu.materials.Si, 'Al' : xu.materials.Al, 'Co' : xu.materials.Co,
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

		return materials

	def set_comboBox_materials_default(self):

		AllItems = [self.ui.comboBox_materials.itemText(i) for i in range(self.ui.comboBox_materials.count())]
		
		sample_now = self.get_experiment_file()['Material']

		if sample_now in AllItems:

			self.ui.comboBox_materials.setCurrentIndex(AllItems.index(sample_now))

	def set_combobox_options(self):

		user_samples = self.get_experiment_file()['user_samples']
		items = self.materials()
		items = list(items.keys())
		
		for sample in user_samples.keys():
			items.append(sample)

		items.sort()
		self.ui.comboBox_materials.addItems(items)
		self.ui.comboBox_materials.setEditable(True)
		self.ui.comboBox_materials.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
		
	def checkbox_state_changed(self):

		if self.ui.checkBox_new_mat.isChecked():
		    self.ui.frame_new_mat.setEnabled(True)
		    self.ui.comboBox_materials.setEnabled(False)
		else:
		    self.ui.frame_new_mat.setEnabled(False)
		    self.ui.comboBox_materials.setEnabled(True)


	def set_sample(self):

		if self.ui.checkBox_new_mat.isChecked():
			
			samp = self.ui.lineEdit_samp_name.text()
			a = self.ui.lineEdit_a.text()
			b = self.ui.lineEdit_b.text()
			c = self.ui.lineEdit_c.text()
			alpha = self.ui.lineEdit_alpha.text()
			beta = self.ui.lineEdit_beta.text()
			gamma = self.ui.lineEdit_gamma.text()
		
			# print("daf.expt -m {} -p {} {} {} {} {} {}".format(samp, a, b, c, alpha, beta, gamma))
			# subprocess.Popen("daf.expt -m {} -p {} {} {} {} {} {}".format(samp, a, b, c, alpha, beta, gamma), shell = True)
			os.system("daf.expt -m {} -p {} {} {} {} {} {}".format(samp, a, b, c, alpha, beta, gamma))

		else:

			samp = self.ui.comboBox_materials.currentText()

			# subprocess.Popen("daf.expt -m {}".format(samp), shell = True)
			os.system("daf.expt -m {}".format(samp))


		
		
			



		
