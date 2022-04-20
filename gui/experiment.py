from os import path
from pydm import Display
import os
import subprocess
import dafutilities as du
import xrayutilities as xu
from PyQt5 import QtWidgets, QtGui, QtCore
from qtpy.QtWidgets import QApplication
import qdarkstyle

class MyDisplay(Display):

    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)
        self.app = QApplication.instance()
        self.ui.pushButton_reset.clicked.connect(self.set_labels)
        self.ui.pushButton_set.clicked.connect(self.set_new_exp_conditions)
        self.ui.comboBox_sor.currentTextChanged.connect(self.on_combobox_sor_changed)
        self.ui.comboBox_e_wl.currentTextChanged.connect(self.on_combobox_en_changed)

        # Change comboBox format
        self.ui.comboBox_sor.setEditable(True)
        self.ui.comboBox_sor.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.ui.comboBox_e_wl.setEditable(True)
        self.ui.comboBox_e_wl.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

        self.set_labels()
        self.set_combobox_sor_default()
        self.set_tab_order()
        self.center()
# 
    def ui_filename(self):
        return 'experiment.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def set_tab_order(self):

        self.setTabOrder(self.ui.lineEdit_sor, self.ui.comboBox_sor)
        self.setTabOrder(self.ui.comboBox_sor, self.ui.lineEdit_e_wl)
        self.setTabOrder(self.ui.lineEdit_e_wl, self.ui.comboBox_e_wl)
        self.setTabOrder(self.ui.comboBox_e_wl, self.ui.lineEdit_i_1)
        self.setTabOrder(self.ui.lineEdit_i_1, self.ui.lineEdit_i_2)
        self.setTabOrder(self.ui.lineEdit_i_2, self.ui.lineEdit_i_3)
        self.setTabOrder(self.ui.lineEdit_i_3, self.ui.lineEdit_n_1)
        self.setTabOrder(self.ui.lineEdit_n_1, self.ui.lineEdit_n_2)
        self.setTabOrder(self.ui.lineEdit_n_2, self.ui.lineEdit_n_3)
        self.setTabOrder(self.ui.lineEdit_n_3, self.ui.lineEdit_r_1)
        self.setTabOrder(self.ui.lineEdit_r_1, self.ui.lineEdit_r_2)
        self.setTabOrder(self.ui.lineEdit_r_2, self.ui.lineEdit_r_3)
        self.setTabOrder(self.ui.lineEdit_r_3, self.ui.pushButton_set)
        self.setTabOrder(self.ui.pushButton_set, self.ui.pushButton_reset)
        self.setTabOrder(self.ui.pushButton_reset, self.ui.lineEdit_sor)

    def get_experiment_file(self):

        dict_args = du.read()
        return dict_args

    def set_combobox_sor_default(self):

        AllItems = [self.ui.comboBox_sor.itemText(i) for i in range(self.ui.comboBox_sor.count())]

        self.ui.comboBox_sor.setCurrentIndex(AllItems.index(self.ui.lineEdit_sor.text()))

    def on_combobox_sor_changed(self):

        self.ui.lineEdit_sor.setText(self.ui.comboBox_sor.currentText())

    def on_combobox_en_changed(self):

        lb = lambda x: "{:.5f}".format(float(x)) # format float with 5 decimals
        dict_args = self.get_experiment_file()
        if str(self.ui.comboBox_e_wl.currentText()).lower() == 'energy':
            self.ui.lineEdit_e_wl.setText(str(lb(dict_args['PV_energy'] - dict_args['energy_offset'])))
        elif str(self.ui.comboBox_e_wl.currentText()).lower() == 'wave length':
            # lb = lambda x: "{:.5f}".format(float(x))
            wl = xu.en2lam(dict_args['PV_energy'] - dict_args['energy_offset'])
            self.ui.lineEdit_e_wl.setText(str(lb(wl)))

    def set_labels(self):

        dict_args = self.get_experiment_file()
        

        self.ui.lineEdit_sor.setText(dict_args['Sampleor'])

        if str(self.ui.comboBox_e_wl.currentText()).lower() == 'energy':
            
            self.ui.lineEdit_e_wl.setText(str(dict_args['PV_energy'] - dict_args['energy_offset']))
        
        elif str(self.ui.comboBox_e_wl.currentText()).lower() == 'wave length':
            
            # lb = lambda x: "{:.5f}".format(float(x))
            wl = xu.en2lam(dict_args['PV_energy'] - dict_args['energy_offset'])
            self.ui.lineEdit_e_wl.setText(str(wl))

        idir = dict_args['IDir']
        self.ui.lineEdit_i_1.setText(str(idir[0]))
        self.ui.lineEdit_i_2.setText(str(idir[1]))
        self.ui.lineEdit_i_3.setText(str(idir[2]))

        ndir = dict_args['NDir']
        self.ui.lineEdit_n_1.setText(str(ndir[0]))
        self.ui.lineEdit_n_2.setText(str(ndir[1]))
        self.ui.lineEdit_n_3.setText(str(ndir[2]))

        rdir = dict_args['RDir']
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
        # os.system("daf.expt -e {energy} -s {sampleor} -i {idir} -n {ndir} -r {rdir}".format(energy=energy, sampleor=sampleor, idir=idir, ndir=ndir, rdir=rdir))
            



        
