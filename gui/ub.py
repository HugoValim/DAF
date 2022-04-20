from os import path
from pydm import Display
import os
import subprocess
import dafutilities as du
import xrayutilities as xu
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QCheckBox, QHBoxLayout, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from qtpy.QtWidgets import QApplication
import qdarkstyle

class MyDisplay(Display):


    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)

        self.app = QApplication.instance()
        self.loop()
        self.update_reflections()
        self.ui.pushButton_refs_save.clicked.connect(self.get_reflection)
        
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
        self.center()

    def ui_filename(self):
        return 'ub.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def loop(self):
        """Loop to check if a curve is selected or not"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(2000) #trigger every .25 seconds.

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def set_tab_order(self):

        # Calc UB
        self.setTabOrder(self.ui.tab_calcUB, self.ui.pushButton_refs_save)
        self.setTabOrder(self.ui.pushButton_refs_save, self.ui.pushButton_2_ref_calc)
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

    def update(self):
        data = self.get_experiment_file()
        refs = data['reflections']
        if self.refs != refs:
            self.update_reflections()

    def update_reflections(self):

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        lb = lambda x: "{:.5f}".format(float(x))
        data = self.get_experiment_file()
        refs = data['reflections']
        self.refs = refs
        row = 0
        self.table_checkboxes = {} 
        for i in range(len(refs)):

            idx = str(i+1)
            idx_for_table = QTableWidgetItem(idx)
            idx_for_table.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) 
            h = QTableWidgetItem(str(refs[i][0]))
            h.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) 
            k = QTableWidgetItem(str(refs[i][1]))
            k.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) 
            l = QTableWidgetItem(str(refs[i][2]))
            l.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            mu = QTableWidgetItem(str(refs[i][3]))
            mu.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            eta = QTableWidgetItem(str(refs[i][4]))
            eta.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            chi = QTableWidgetItem(str(refs[i][5]))
            chi.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            phi = QTableWidgetItem(str(refs[i][6]))
            phi.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            nu = QTableWidgetItem(str(refs[i][7]))
            nu.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            delta = QTableWidgetItem(str(refs[i][8]))
            delta.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            en = QTableWidgetItem(lb(refs[i][9]))
            en.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, idx_for_table)
            self.tableWidget.setItem(row, 1, h)
            self.tableWidget.setItem(row, 2, k)
            self.tableWidget.setItem(row, 3, l)
            self.tableWidget.setItem(row, 4, mu)
            self.tableWidget.setItem(row, 5, eta)
            self.tableWidget.setItem(row, 6, chi)
            self.tableWidget.setItem(row, 7, phi)
            self.tableWidget.setItem(row, 8, nu)
            self.tableWidget.setItem(row, 9, delta)
            self.tableWidget.setItem(row, 10, en)
            widget = QWidget(parent=self.tableWidget)
            self.table_checkboxes[idx] = QCheckBox()
            self.table_checkboxes[idx].setCheckState(QtCore.Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(self.table_checkboxes[idx])
            layoutH.setAlignment(QtCore.Qt.AlignCenter)
            layoutH.setContentsMargins(10, 0, 0, 0)           
            self.tableWidget.setCellWidget(row, 11, widget)
            self.tableWidget.setCellWidget(row, 11, self.table_checkboxes[idx])
            row += 1

        for i in range(self.tableWidget.columnCount()):
            header = self.tableWidget.horizontalHeader()
            header.setResizeMode(i, QHeaderView.Stretch)


    def get_reflection(self):
        # os.system("daf.ub -rn")
        subprocess.Popen("daf.ub -rn", shell = True)
        self.update_reflections()

    def calc_from_2_ref(self):

        inp = []
        for key, value in self.table_checkboxes.items():
            if value.isChecked():
                inp.append(key)

        if len(inp) != 2:
            msgbox = QtWidgets.QMessageBox()
            msgbox_text = 'The number of checked items \nmust be 2 for this calculation'
            ret = msgbox.question(self, 'Warning', msgbox_text, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            # os.system("daf.ub -c2 {} {}".format(inp[0], inp[1]))
            subprocess.Popen("daf.ub -c2 {} {}".format(inp[0], inp[1]), shell = True)

    def calc_from_3_ref(self):

        inp = []
        for key, value in self.table_checkboxes.items():
            if value.isChecked():
                inp.append(key)

        if len(inp) != 3:
            msgbox = QtWidgets.QMessageBox()
            msgbox_text = 'The number of checked items \nmust be 2 for this calculation'
            ret = msgbox.question(self, 'Warning', msgbox_text, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            # os.system("daf.ub -c3 {} {} {}".format(inp[0], inp[1], inp[2]))
            subprocess.Popen("daf.ub -c3 {} {} {}".format(inp[0], inp[1], inp[2]), shell = True)

        self.update_samp_parameters()

    def update_samp_parameters(self):
        data = self.get_experiment_file()
        self.label_a.setText(self.format_decimals(data['lparam_a']))
        self.label_b.setText(self.format_decimals(data['lparam_b']))
        self.label_c.setText(self.format_decimals(data['lparam_c']))
        self.label_alpha.setText(self.format_decimals(data['lparam_alpha']))
        self.label_beta.setText(self.format_decimals(data['lparam_beta']))
        self.label_gamma.setText(self.format_decimals(data['lparam_gama']))

    def set_new_sample(self):
        dict_args = du.read()
        samples = dict_args['user_samples']
        text, result = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'New sample name')
        a = dict_args['lparam_a']
        b = dict_args['lparam_b']
        c = dict_args['lparam_c']
        alpha = dict_args['lparam_alpha']
        beta = dict_args['lparam_beta']
        gamma = dict_args['lparam_gama']
        if result:
            if text in samples.keys():
                msgbox = QtWidgets.QMessageBox()
                msgbox_text = 'This samples name {} already exists, \ndo you want to overwrite it?'.format(text)
                ret = msgbox.question(self, 'Warning', msgbox_text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)

                if ret == QtWidgets.QMessageBox.Ok:
                    # os.system("daf.expt -m {} -p {} {} {} {} {} {}".format(text, a, b, c, alpha, beta, gamma))
                    subprocess.Popen("daf.expt -m {} -p {} {} {} {} {} {}".format(text, a, b, c, alpha, beta, gamma), shell = True)


            else:
                # os.system("daf.expt -m {} -p {} {} {} {} {} {}".format(text, a, b, c, alpha, beta, gamma))
                subprocess.Popen("daf.expt -m {} -p {} {} {} {} {} {}".format(text, a, b, c, alpha, beta, gamma), shell = True)

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
        subprocess.Popen("daf.ub -U {} {} {} {} {} {} {} {} {}".format(u_00, u_01, u_02, u_10, u_11, u_12, u_20, u_21, u_22), shell = True)
        # os.system("daf.ub -U {} {} {} {} {} {} {} {} {}".format(u_00, u_01, u_02, u_10, u_11, u_12, u_20, u_21, u_22))
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
        # os.system("daf.ub -UB {} {} {} {} {} {} {} {} {}".format(ub_00, ub_01, ub_02, ub_10, ub_11, ub_12, ub_20, ub_21, ub_22))
        subprocess.Popen("daf.ub -UB {} {} {} {} {} {} {} {} {}".format(ub_00, ub_01, ub_02, ub_10, ub_11, ub_12, ub_20, ub_21, ub_22), shell = True)




        






        
        
            



        
