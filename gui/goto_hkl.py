from os import path
from pydm import Display
import os
import subprocess

class MyDisplay(Display):

	def __init__(self, parent=None, args=None, macros=None):
		super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)

		self.ui.calc_HKL.clicked.connect(self.move_in_hkl)
		self.set_tab_order()
# 
	def ui_filename(self):
		return 'goto_hkl.ui'

	def ui_filepath(self):
		return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

	def set_tab_order(self):
		self.setTabOrder(self.ui.H_set, self.ui.K_set)
		self.setTabOrder(self.ui.K_set, self.ui.L_set)
		self.setTabOrder(self.ui.L_set, self.ui.calc_HKL)
		self.setTabOrder(self.ui.calc_HKL, self.ui.H_set)

	def move_in_hkl(self):

		H = self.ui.H_set.text()
		K = self.ui.K_set.text()
		L = self.ui.L_set.text()

		os.system("daf.mv {} {} {} -q".format(H, K, L))
		# subprocess.Popen("daf.mv {} {} {} -q".format(H, K, L), shell = True)

		self.H_set.setText('')
		self.K_set.setText('')
		self.L_set.setText('')
