from os import path
from pydm import Display
import os
import subprocess
import dafutilities as du
import xrayutilities as xu

class MyDisplay(Display):


	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)


		self.set_combobox_options()
		self.ui.frame_new_mat.setEnabled(False)
		self.ui.checkBox_new_mat.stateChanged.connect(self.checkbox_state_changed)
		self.ui.pushButton_set.clicked.connect(self.set_sample)

	def ui_filename(self):
		return 'sample.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def get_experiment_file(self):

		dict_args = du.read()
		return dict_args

	def ret_list(self, string):

		return [float(i) for i in string.strip('][').split(', ')]

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


	def set_combobox_options(self):

		items = self.materials()
		items_sorted = list(items.keys())
		items_sorted.sort()
		self.ui.comboBox_materials.addItems(items_sorted)
		
	def checkbox_state_changed(self):

		if self.ui.checkBox_new_mat.isChecked():
		    self.ui.frame_new_mat.setEnabled(True)
		else:
		    self.ui.frame_new_mat.setEnabled(False)


	def set_sample(self):

		if self.ui.checkBox_new_mat.isChecked():
			if self.ui.lineEdit_samp_name.text() != '':
				samp = self.ui.lineEdit_samp_name.text()
				a = self.ui.lineEdit_a.text()
				b = self.ui.lineEdit_b.text()
				c = self.ui.lineEdit_c.text()
				alpha = self.ui.lineEdit_alpha.text()
				beta = self.ui.lineEdit_beta.text()
				gamma = self.ui.lineEdit_gamma.text()
			
				subprocess.Popen("daf.expt -m {} -p ".format(samp, a, b, c, alpha, beta, gamma), shell = True)

		else:

			samp = self.ui.comboBox_materials.currentText()

			subprocess.Popen("daf.expt -m {}".format(samp), shell = True)


		
		
			



		
