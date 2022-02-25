from os import path
from pydm import Display

import sys
import os
import subprocess
import daf
import numpy as np
import dafutilities as du
import yaml
import time
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QCoreApplication, Qt
from qtpy.QtWidgets import QApplication, QTreeWidgetItem, QMenu, QAction, QHeaderView, QTableWidgetItem, QMenu, QComboBox, QListWidget
from pydm.widgets import PyDMEmbeddedDisplay
import json
import qdarkstyle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

DEFAULT = ".Experiment"

# global data_to_update # This variable holds the data processed in another Qthread and then the labels are updated in MyDisplay class

class Worker(QObject):
    finished = pyqtSignal()
    update_labels = pyqtSignal()

    
    def get_experiment_data(self, filepath=DEFAULT):
        with open(filepath) as file:
            data = yaml.safe_load(file)
        
        return data

    def format_decimals(self, x):
            
            if type(x) == float:
                return "{:.5f}".format(float(x)) # format float with 5 decimals

            else:
                result = []
                for i in x:
                    result.append("{:.5f}".format(float(i)))

                return result


    def call_update(self):

        data = self.get_experiment_data()
        if data != self.data:
            self.update()
            self.data = data


    def update(self):


        dict_args = du.read()

        U = np.array(dict_args['U_mat'])
        U_print = np.array([self.format_decimals(U[0]), self.format_decimals(U[1]), self.format_decimals(U[2])])

        UB = np.array(dict_args['UB_mat'])
        UB_print = np.array([self.format_decimals(UB[0]), self.format_decimals(UB[1]), self.format_decimals(UB[2])])


        mode = [int(i) for i in dict_args['Mode']]
        idir = dict_args['IDir_print']
        ndir = dict_args['NDir_print']
        rdir = dict_args['RDir']

        exp = daf.Control(*mode)
        exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])

        if dict_args['Material'] in dict_args['user_samples'].keys():
            exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

        else: 
            exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
    
        # exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])
        exp.set_U(U)
        exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                    Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                    psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])
        
        hklnow = exp.calc_from_angs(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])

        pseudo = exp.calc_pseudo(dict_args["Mu"], dict_args["Eta"], dict_args["Chi"], dict_args["Phi"], dict_args["Nu"], dict_args["Del"])
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
                            'U' : U_print, 'UB' : UB_print, 'bounds' : bounds , 'pseudo_dict' : pseudo_dict, 'dargs' : dict_args}

        

    def run(self):
        """Long-running task."""
        while True:
            self.update()
            self.update_labels.emit()
            time.sleep(1)

class RMap(FigureCanvasQTAgg):
    """Class to handle the RMap plot in the GUI"""

    def __init__(self, parent=None, dict_args=None, move=False, samples=None, idirp=None, ndirp=None):
        U = np.array(dict_args['U_mat'])
        mode = [int(i) for i in dict_args['Mode']]
        idir = dict_args['IDir']
        ndir = dict_args['NDir']
        rdir = dict_args['RDir']
        paradir = idirp
        normdir = ndirp
        Mu_bound = dict_args['bound_Mu']
        Eta_bound = dict_args['bound_Eta']
        Chi_bound = dict_args['bound_Chi']
        Phi_bound = dict_args['bound_Phi']
        Nu_bound = dict_args['bound_Nu']
        Del_bound = dict_args['bound_Del']

        exp = daf.Control(*mode)
        if dict_args['Material'] in dict_args['user_samples'].keys():
            exp.set_material(dict_args['Material'], *dict_args['user_samples'][dict_args['Material']])

        else: 
            exp.set_material(dict_args['Material'], dict_args["lparam_a"], dict_args["lparam_b"], dict_args["lparam_c"], 
                             dict_args["lparam_alpha"], dict_args["lparam_beta"], dict_args["lparam_gama"])

        exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])
        exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
        exp.set_U(U)
        exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                            Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                            psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])

        exp(calc=False)
        ttmax, ttmin = exp.two_theta_max()
        self.ax, h = exp.show_reciprocal_space_plane(ttmax = ttmax, ttmin=ttmin, idir=paradir, ndir=normdir, scalef=100, move=move)
        for i in samples:
            exp = daf.Control(*mode)
            exp.set_material(str(i))
            exp.set_exp_conditions(idir = idir, ndir = ndir, rdir = rdir, en = dict_args['PV_energy'] - dict_args['energy_offset'], sampleor = dict_args['Sampleor'])
            exp.set_circle_constrain(Mu=Mu_bound, Eta=Eta_bound, Chi=Chi_bound, Phi=Phi_bound, Nu=Nu_bound, Del=Del_bound)
            exp.set_U(U)
            exp.set_constraints(Mu = dict_args['cons_Mu'], Eta = dict_args['cons_Eta'], Chi = dict_args['cons_Chi'], Phi = dict_args['cons_Phi'],
                                Nu = dict_args['cons_Nu'], Del = dict_args['cons_Del'], alpha = dict_args['cons_alpha'], beta = dict_args['cons_beta'],
                                psi = dict_args['cons_psi'], omega = dict_args['cons_omega'], qaz = dict_args['cons_qaz'], naz = dict_args['cons_naz'])
            exp(calc=False)
            ttmax, ttmin = exp.two_theta_max()
            ax, h2 = exp.show_reciprocal_space_plane(ttmax = ttmax, ttmin=ttmin, idir=paradir, ndir=normdir, scalef=100, ax = self.ax, move=move)
        
        super(RMap, self).__init__(self.ax.figure)


class MyDisplay(Display):

    def __init__(self, parent=None, args=None, macros=None):
        super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)

        self.app = QApplication.instance()
        self.set_main_screen_title()
        self._createMenuBar()
        self.default_theme()
        self.set_scan_prop()
        self.setup_scroll_area()
        self.ui.progressBar.hide()
        self.ui.label_generating_points.hide()
        self.scan = False
        self.make_connections()
        self.set_tab_order()
        self.runLongTask()
        self.current_rmap_samples = []
        self.idir = [0,1,0]
        self.ndir = [0,0,1]
        self.rmap_widget(du.read(), samples = self.current_rmap_samples, idir=self.idir, ndir=self.ndir)
        self.delay = 5 # Some thing in GUI dont need to be updated every update call
        self.delay_counter = self.delay # Cooldown to delay, it start with the same value so it runs in the first loop
        

    def set_tab_order(self):

        # Scan
        self.setTabOrder(self.ui.tab_scan, self.ui.lineEdit)
        self.setTabOrder(self.ui.lineEdit, self.ui.lineEdit_2)
        self.setTabOrder(self.ui.lineEdit_2, self.ui.listWidget_counters)
        self.setTabOrder(self.ui.listWidget_counters, self.ui.treeWidget_counters)
        self.setTabOrder(self.ui.treeWidget_counters, self.ui.pushButton_new_counter_file)
        self.setTabOrder(self.ui.pushButton_new_counter_file, self.ui.pushButton_remove_counter_file)
        self.setTabOrder(self.ui.pushButton_remove_counter_file, self.ui.pushButton_set_config_counter)
        self.setTabOrder(self.ui.pushButton_set_config_counter, self.ui.comboBox_counters)
        self.setTabOrder(self.ui.comboBox_counters, self.ui.pushButton_add_counter)
        self.setTabOrder(self.ui.pushButton_add_counter, self.ui.pushButton_remove_counter)
        self.setTabOrder(self.ui.pushButton_remove_counter, self.ui.lineEdit_hi)
        self.setTabOrder(self.ui.lineEdit_hi, self.ui.lineEdit_hf)
        self.setTabOrder(self.ui.lineEdit_hf, self.ui.lineEdit_ki)
        self.setTabOrder(self.ui.lineEdit_ki, self.ui.lineEdit_kf)
        self.setTabOrder(self.ui.lineEdit_kf, self.ui.lineEdit_li)
        self.setTabOrder(self.ui.lineEdit_li, self.ui.lineEdit_lf)
        self.setTabOrder(self.ui.lineEdit_lf, self.ui.lineEdit_step)
        self.setTabOrder(self.ui.lineEdit_step, self.ui.lineEdit_time)
        self.setTabOrder(self.ui.lineEdit_time, self.ui.comboBox_xlabel)
        self.setTabOrder(self.ui.comboBox_xlabel, self.ui.lineEdit_csv_filename)
        self.setTabOrder(self.ui.lineEdit_csv_filename, self.ui.checkBox_only_csv)
        self.setTabOrder(self.ui.checkBox_only_csv, self.ui.pushButton_start_scan)
        self.setTabOrder(self.ui.pushButton_start_scan, self.ui.tab_scan)

        # Setup
        self.setTabOrder(self.ui.tab_setup, self.ui.listWidget_setup)
        self.setTabOrder(self.ui.listWidget_setup, self.ui.pushButton_new_setup)
        self.setTabOrder(self.ui.pushButton_new_setup, self.ui.pushButton_save_setup)
        self.setTabOrder(self.ui.pushButton_save_setup, self.ui.pushButton_copy_setup)
        self.setTabOrder(self.ui.pushButton_copy_setup, self.ui.pushButton_remove_setup)
        self.setTabOrder(self.ui.pushButton_remove_setup, self.ui.pushButton_change_setup)
        self.setTabOrder(self.ui.pushButton_change_setup, self.ui.pushButton_update_desc)
        self.setTabOrder(self.ui.pushButton_update_desc, self.ui.tab_setup)

    def make_connections(self):

        self.ui.listWidget_setup.itemSelectionChanged.connect(self.on_list_widget_change)
        self.ui.listWidget_counters.itemSelectionChanged.connect(self.on_counters_list_widget_change)

        # Scan buttons
        self.ui.pushButton_set_config_counter.clicked.connect(self.set_counter)
        self.ui.pushButton_new_counter_file.clicked.connect(self.new_counter_file)
        self.ui.pushButton_remove_counter_file.clicked.connect(self.remove_counter_file)
        self.ui.pushButton_add_counter.clicked.connect(self.add_counter)
        self.ui.pushButton_remove_counter.clicked.connect(self.remove_counter)
        self.ui.pushButton_start_scan.clicked.connect(self.start_scan)

        # Setup buttons
        self.ui.pushButton_new_setup.clicked.connect(self.new_setup_dialog)
        self.ui.pushButton_save_setup.clicked.connect(self.save_setup)
        self.ui.pushButton_copy_setup.clicked.connect(self.copy_setup)
        self.ui.pushButton_change_setup.clicked.connect(self.change_setup)
        self.ui.pushButton_update_desc.clicked.connect(self.update_setup_description)
        self.ui.pushButton_remove_setup.clicked.connect(self.remove_setup)
        
        # Menu connections
        self.menu_bar.triggered.connect(self.style_sheet_handler)

        # RMap tab connections
        self.checkBox_rmap.stateChanged.connect(lambda: self.rmap_widget(data_to_update['dargs'], samples=self.current_rmap_samples, idir=self.idir, ndir=self.ndir))
        self.pushButton_refresh.clicked.connect(lambda: self.rmap_widget(data_to_update['dargs'], samples=self.current_rmap_samples, idir=self.idir, ndir=self.ndir))

    def _createMenuBar(self):
        """Create the menu bar and shortcuts"""
        self.menu_bar = self.app.main_window.menuBar()
        self.menu_bar.clear()
        # Creating menus using a QMenu object
        self.file_menu = QMenu("&File", self)
        self.option_menu = QMenu("&Options", self)

        self.menu_bar.addMenu(self.file_menu)
        open_action = self.file_menu.addAction('&Open File')
        open_action.setShortcut("Ctrl+o")

        self.menu_bar.addMenu(self.option_menu)
        style_action = self.option_menu.addAction(QAction('Dark Theme', self.menu_bar, checkable=True))
    
    def default_theme(self):
        dict_args = du.read()
        if dict_args['dark_mode']:
            style = qdarkstyle.load_stylesheet_pyqt5()
            self.tableWidget_U.setMaximumHeight(97)
            self.tableWidget_UB.setMaximumHeight(97)
            self.app.setStyleSheet(style)
            for action in self.option_menu.actions():
                if action.text() == 'Dark Theme':
                    action.setChecked(True)
        else:
            self.tableWidget_U.setMaximumHeight(92)
            self.tableWidget_UB.setMaximumHeight(92)
            self.app.setStyleSheet('')
            for action in self.option_menu.actions():
                if action.text() == 'Dark Theme':
                    action.setChecked(False)

    def style_sheet_handler(self):
        dict_args = du.read()
        for action in self.option_menu.actions():
            if action.text() == 'Dark Theme':
                if action.isChecked():
                    style = qdarkstyle.load_stylesheet_pyqt5()
                    self.tableWidget_U.setMaximumHeight(97)
                    self.tableWidget_UB.setMaximumHeight(97)
                    self.app.setStyleSheet(style)
                    dict_args['dark_mode'] = 1
                    du.write(dict_args)
                else:
                    self.tableWidget_U.setMaximumHeight(92)
                    self.tableWidget_UB.setMaximumHeight(92)
                    self.app.setStyleSheet('')
                    dict_args['dark_mode'] = 0
                    du.write(dict_args)

    def load_data(self):
        # Extract the directory of this file...
        base_dir = os.path.dirname(os.path.realpath(__file__))
        # Concatenate the directory with the file name...
        data_file = os.path.join(base_dir, "motor_fields_default.yml")
        # Open the file so we can read the data...
        with open(data_file, 'r') as file:
            data = yaml.safe_load(file)
            return data

    def set_main_screen_title(self):
        dict_ = du.read()
        # self.app.main_window.setWindowTitle('teste')
        self.ui.setWindowTitle('DAF GUI ({})'.format(dict_['setup']))

    def update_main_screen_title(self):
        dict_ = du.read()
        self.app.main_window.setWindowTitle('DAF GUI ({}) - PyDM'.format(dict_['setup']))

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

    def refresh_pydm_motors(self):

        data = du.PVS

        

        translate = QCoreApplication.translate
        
        # set del motor labels

        del_channel = 'ca://' + data['Del']
        self.ui.PyDMLabel_del_desc.setProperty("channel", translate("Form", del_channel + '.DESC'))
        self.ui.PyDMLabel_del_val.setProperty("channel", translate("Form", del_channel + '.VAL'))
        self.ui.PyDMLabel_del_rbv.setProperty("channel", translate("Form", del_channel + '.RBV'))
        self.ui.PyDMByteIndicator_del.setProperty("channel", translate("Form", del_channel + '.MOVN'))
        self.ui.PyDMPushButton_del.setProperty("channel", translate("Form", del_channel + '.STOP'))

        # set eta motor labels

        del_channel = 'ca://' + data['Eta']
        self.ui.PyDMLabel_eta_desc.setProperty("channel", translate("Form", del_channel + '.DESC'))
        self.ui.PyDMLabel_eta_val.setProperty("channel", translate("Form", del_channel + '.VAL'))
        self.ui.PyDMLabel_eta_rbv.setProperty("channel", translate("Form", del_channel + '.RBV'))
        self.ui.PyDMByteIndicator_eta.setProperty("channel", translate("Form", del_channel + '.MOVN'))
        self.ui.PyDMPushButton_eta.setProperty("channel", translate("Form", del_channel + '.STOP'))

        # set chi motor labels

        del_channel = 'ca://' + data['Chi']
        self.ui.PyDMLabel_chi_desc.setProperty("channel", translate("Form", del_channel + '.DESC'))
        self.ui.PyDMLabel_chi_val.setProperty("channel", translate("Form", del_channel + '.VAL'))
        self.ui.PyDMLabel_chi_rbv.setProperty("channel", translate("Form", del_channel + '.RBV'))
        self.ui.PyDMByteIndicator_chi.setProperty("channel", translate("Form", del_channel + '.MOVN'))
        self.ui.PyDMPushButton_chi.setProperty("channel", translate("Form", del_channel + '.STOP'))

        # set phi motor labels

        del_channel = 'ca://' + data['Phi']
        self.ui.PyDMLabel_phi_desc.setProperty("channel", translate("Form", del_channel + '.DESC'))
        self.ui.PyDMLabel_phi_val.setProperty("channel", translate("Form", del_channel + '.VAL'))
        self.ui.PyDMLabel_phi_rbv.setProperty("channel", translate("Form", del_channel + '.RBV'))
        self.ui.PyDMByteIndicator_phi.setProperty("channel", translate("Form", del_channel + '.MOVN'))
        self.ui.PyDMPushButton_phi.setProperty("channel", translate("Form", del_channel + '.STOP'))

        # set nu motor labels

        del_channel = 'ca://' + data['Nu']
        self.ui.PyDMLabel_nu_desc.setProperty("channel", translate("Form", del_channel + '.DESC'))
        self.ui.PyDMLabel_nu_val.setProperty("channel", translate("Form", del_channel + '.VAL'))
        self.ui.PyDMLabel_nu_rbv.setProperty("channel", translate("Form", del_channel + '.RBV'))
        self.ui.PyDMByteIndicator_nu.setProperty("channel", translate("Form", del_channel + '.MOVN'))
        self.ui.PyDMPushButton_nu.setProperty("channel", translate("Form", del_channel + '.STOP'))

        # set mu motor labels

        del_channel = 'ca://' + data['Mu']
        self.ui.PyDMLabel_mu_desc.setProperty("channel", translate("Form", del_channel + '.DESC'))
        self.ui.PyDMLabel_mu_val.setProperty("channel", translate("Form", del_channel + '.VAL'))
        self.ui.PyDMLabel_mu_rbv.setProperty("channel", translate("Form", del_channel + '.RBV'))
        self.ui.PyDMByteIndicator_mu.setProperty("channel", translate("Form", del_channel + '.MOVN'))
        self.ui.PyDMPushButton_mu.setProperty("channel", translate("Form", del_channel + '.STOP'))

    def rmap_widget(self, data, samples, idir, ndir):
        # Build the RMap graph
        self.rmap_plot = RMap(dict_args=data, move=self.checkBox_rmap.isChecked(), samples = samples, idirp=idir, ndirp=ndir)
        plt.close(self.rmap_plot.ax.figure) #Must have that, otherwise it will consume all the RAM opening figures
        for i in reversed(range(self.verticalLayout_rmap.count())): 
            self.verticalLayout_rmap.itemAt(i).widget().setParent(None)
        toolbar = NavigationToolbar(self.rmap_plot, self)
        self.verticalLayout_rmap.addWidget(toolbar)
        self.verticalLayout_rmap.addWidget(self.rmap_plot)
        # self.rmap_menu()
        self.rmap_plot.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rmap_plot.customContextMenuRequested[QtCore.QPoint].connect(self.rmap_menu_builder)

    def rmap_menu_builder(self):
        """Build the menu that will pop when with right clicks in the graph"""
        self.rmap_menu = QMenu(self.rmap_plot)
        # Refresh plot
        refresh_plot = self.rmap_menu.addAction('Refresh')
        refresh_plot.triggered.connect(lambda: self.rmap_widget(data_to_update['dargs'], samples=self.current_rmap_samples, idir=self.idir, ndir=self.ndir))
        # Clear other samples in graph
        idir = self.rmap_menu.addAction('IDir ({})'.format(self.idir))
        idir.triggered.connect(self.idir_manager)
        # Clear other samples in graph
        ndir = self.rmap_menu.addAction('Ndir ({})'.format(self.ndir))
        ndir.triggered.connect(self.ndir_manager)
        # Add more samples to the graph
        add_samples = self.rmap_menu.addAction('Add Samples')
        add_samples.triggered.connect(self.rmap_add_samples)
        # Clear other samples in graph
        clear_plot = self.rmap_menu.addAction('Clear')
        clear_plot.triggered.connect(self.clear_plot_samples)


        self.rmap_menu.exec_(QtGui.QCursor.pos())

    def idir_manager(self):
        text, result = QtWidgets.QInputDialog.getText(self, 'Set IDir', 'Enter with the new IDir with the format a,b,c')
        if result:
            self.idir = [float(i) for i in text.split(",")]
        self.rmap_widget(data_to_update['dargs'], samples=self.current_rmap_samples, idir=self.idir, ndir=self.ndir)

    def ndir_manager(self):
        text, result = QtWidgets.QInputDialog.getText(self, 'Set NDir', 'Enter with the new NDir with the format a,b,c')
        if result:
            self.ndir = [float(i) for i in text.split(",")]
        self.rmap_widget(data_to_update['dargs'], samples=self.current_rmap_samples, idir=self.idir, ndir=self.ndir)

    def rmap_add_samples(self):
        self.combo_box = QComboBox()
        items = ['Si', 'Al', 'Co',
                     'Cu', 'Cr', 'Fe',
                     'Ge', 'Sn',
                     'LaB6', 'Al2O3', 'C',
                     'C_HOPG', 'InAs', 'InP',
                     'InSb', 'GaP', 'GaAs',
                     'AlAs', 'GaSb', 'GaAsWZ',
                     'GaAs4H', 'GaPWZ', 'InPWZ',
                     'InAs4H', 'InSbWZ', 'InSb4H',
                     'PbTe', 'PbSe', 'CdTe',
                     'CdSe', 'CdSe_ZB', 'HgSe',
                     'NaCl', 'MgO', 'GaN',
                     'BaF2', 'SrF2', 'CaF2',
                     'MnO', 'MnTe', 'GeTe',
                     'SnTe', 'Au', 'Ti',
                     'Mo', 'Ru', 'Rh',
                     'V', 'Ta', 'Nb',
                     'Pt', 'Ag2Se', 'TiO2',
                     'MnO2', 'VO2_Rutile', 'VO2_Baddeleyite',
                     'SiO2', 'In', 'Sb', 
                     'Ag', 'SnAlpha', 'CaTiO3',
                     'SrTiO3', 'BaTiO3', 'FeO',
                     'CoO', 'Fe3O4', 'Co3O4',
                     'FeRh', 'Ir20Mn80', 'CoFe',
                     'CoGa', 'CuMnAs', 'Mn3Ge_cub',
                     'Mn3Ge', 'Pt3Cr', 'TiN']

        user_samples = du.read()['user_samples']
        for sample in user_samples.keys():
            items.append(sample)
        items.sort()
        # adding list of items to combo box
        self.combo_box.addItems(items)
        self.combo_box.move(QtGui.QCursor.pos())
        self.combo_box.currentTextChanged.connect(self.current_rmap_samples_manager)
        self.combo_box.showPopup()

    def clear_plot_samples(self):
        self.current_rmap_samples = []
        self.rmap_widget(data_to_update['dargs'], samples=self.current_rmap_samples, idir=self.idir, ndir=self.ndir)

    def current_rmap_samples_manager(self, choice):
        if choice in self.current_rmap_samples:
            self.current_rmap_samples.remove(choice)
        else:
            self.current_rmap_samples.append(choice)
        self.rmap_widget(data_to_update['dargs'], samples=self.current_rmap_samples, idir=self.idir, ndir=self.ndir)


    def extract(self, q_list_widget):
        lst = q_list_widget
        items = []
        for x in range(lst.count()):
            items.append(lst.item(x).text())
        return items 

    def setup_scroll_area(self):

        setups = os.listdir(du.HOME + '/.daf')
        setups = [i for i in setups if not i.endswith('.py')]
        setups.sort()       

        # itemsTextList =  [str(self.ui.listWidget_setup.item(i).text()) for i in range(self.ui.listWidget_setup.count())]
        

        self.ui.listWidget_setup.clear()

        self.ui.listWidget_setup.addItems(setups)

    def on_list_widget_change(self):

        setups = os.listdir(du.HOME + '/.daf')
        setups = [i for i in setups if not i.endswith('.py')]

        item = self.ui.listWidget_setup.currentItem()
        value = item.text()
        
        if value in setups:
            dict_ = du.read(du.HOME + '/.daf/' + value)
            # self.ui.textEdit_setup.setText(bytes(dict_['setup_desc'], "uft-8").decode("unicode_escape"))
            self.ui.textEdit_setup.setText(dict_['setup_desc'])


    def change_setup(self):

        item = self.ui.listWidget_setup.currentItem()
        value = item.text()

        os.system("daf.setup -c {}".format(value))
        self.update_main_screen_title()

    def update_setup_description(self):

        item = self.ui.listWidget_setup.currentItem()
        value = item.text()
        mytext = self.textEdit_setup.toPlainText()
        # raw_s = repr(mytext)

        os.system('daf.setup -d {} "{}"'.format(value, mytext))


    def new_setup_dialog(self):
        setups = os.listdir(du.HOME + '/.daf')
        setups = [i for i in setups if not i.endswith('.py')]

        text, result = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'New setup name')
        
        if result:
            if text in setups:
                msgbox = QtWidgets.QMessageBox()
                msgbox_text = 'Setup {} already exists, \ndo you want to overwrite it?'.format(text)
                ret = msgbox.question(self, 'Warning', msgbox_text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)

                if ret == QtWidgets.QMessageBox.Ok:
                    os.system('daf.setup -n {}'.format(text))

            else:
                os.system('daf.setup -n {}'.format(text))

        self.setup_scroll_area()
    
    def save_setup(self):

        os.system('daf.setup -s')

    def copy_setup(self):

        setups = os.listdir(du.HOME + '/.daf')
        setups = [i for i in setups if not i.endswith('.py')]

        text, result = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Copy setup name')
        
        if result:
            if text in setups:
                msgbox = QtWidgets.QMessageBox()
                msgbox_text = 'Setup {} already exists, \ndo you want to overwrite it?'.format(text)
                ret = msgbox.question(self, 'Warning', msgbox_text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)

                if ret == QtWidgets.QMessageBox.Ok:
                    os.system('daf.setup -s {}'.format(text))

            else:
                os.system('daf.setup -s {}'.format(text))

        self.setup_scroll_area()

    def remove_setup(self):
        item = self.ui.listWidget_setup.currentItem()
        value = item.text()
        os.system("daf.setup -r {}".format(value))
        self.setup_scroll_area()

    def set_scan_prop(self):
        """ Set properties showed in scan tab in daf.gui """
        dict_ = du.read()
        self.ui.label_current_config.setText(dict_['default_counters'].split('.')[1])
        self.counters_scroll_area()
        self.set_counter_combobox_options()
        self.set_xlabel_combobox_options()

    def fill_item(self, item, value):
        item.setExpanded(False)
        if type(value) is dict:
            for key, val in sorted(value.items()):
                child = QTreeWidgetItem()
                child.setText(0, str(key))
                item.addChild(child)
                self.fill_item(child, val)
        elif type(value) is list:
            for val in value:
                child = QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:      
                    child.setText(0, '[dict]')
                    self.fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    self.fill_item(child, val)
                else:
                    child.setText(0, str(val))              
                    child.setExpanded(True)
        else:
            child = QTreeWidgetItem()
            child.setText(0, str(value))
            item.addChild(child)

    def fill_widget(self, widget, value):
        widget.clear()
        self.fill_item(widget.invisibleRootItem(), value)

    def print_tree(self, file):
        """Print counters of a setup as a tree"""
        with open('/etc/xdg/scan-utils/config.yml') as conf:
            config_data = yaml.safe_load(conf)
        with open(file) as file:
            data = yaml.safe_load(file)
        if data != None:
            full_output = {}
            for counter in data:
                if isinstance(counter, dict):
                    counter = list(counter.keys())[0]
                full_output[counter] = config_data['counters'][counter]
        else:
            full_output = 'Add counters to this file'
        self.fill_widget(self.ui.treeWidget_counters, full_output)

    def counters_scroll_area(self):
        """List all possible counter configs"""
        user_configs = os.listdir(du.HOME + '/.config/scan-utils')
        sys_configs = os.listdir('/etc/xdg/scan-utils')
        all_configs = user_configs + sys_configs
        configs = [i.split('.')[1] for i in all_configs if len(i.split('.')) == 3 and i.endswith('.yml')]
        configs.sort()
        self.ui.listWidget_counters.clear()
        self.ui.listWidget_counters.addItems(configs)

    def on_counters_list_widget_change(self):
        """Print the counters on a setup when selected"""       
        prefix = 'config.'
        sufix = '.yml'
        user_configs = os.listdir(du.HOME + '/.config/scan-utils')
        sys_configs = os.listdir('/etc/xdg/scan-utils')
        all_configs = user_configs + sys_configs
        configs = [i.split('.')[1] for i in all_configs if len(i.split('.')) == 3 and i.endswith('.yml')]
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        if value in configs:
            try:
                self.print_tree('/etc/xdg/scan-utils/' + prefix + value + sufix)
            except:
                self.print_tree(du.HOME + '/.config/scan-utils/' + prefix + value + sufix)

    def set_counter(self):
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        os.system("daf.mc -s {}".format(value))
        dict_ = du.read()
        self.ui.label_current_config.setText(dict_['default_counters'].split('.')[1])
        self.set_xlabel_combobox_options()

    def new_counter_file(self):
        configs = os.listdir(du.HOME + '/.config/scan-utils')
        configs = [i.split('.')[1] for i in configs if len(i.split('.')) == 3 and i.endswith('.yml')]
        text, result = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'New config file name')
        
        if result:
            if text in configs:
                msgbox = QtWidgets.QMessageBox()
                msgbox_text = 'Config file {} already exists, \ndo you want to overwrite it?'.format(text)
                ret = msgbox.question(self, 'Warning', msgbox_text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)

                if ret == QtWidgets.QMessageBox.Ok:
                    os.system('daf.mc -n {}'.format(text))

            else:
                os.system('daf.mc -n {}'.format(text))
        self.counters_scroll_area()

    def add_counter(self):
        """Add a counter to a setup"""
        counter = self.ui.comboBox_counters.currentText()
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        os.system("daf.mc -a {} {}".format(value, counter))
        list_ = self.extract(self.ui.listWidget_counters)
        if list_.index(value) == 0 and len(list_) > 1:
            self.ui.listWidget_counters.setCurrentRow(1)
        else:
            self.ui.listWidget_counters.setCurrentRow(0)
        self.ui.listWidget_counters.setCurrentRow(list_.index(value))
        self.set_xlabel_combobox_options()

    def remove_counter_file(self):
        item = self.ui.listWidget_counters.currentItem()
        value = item.text()
        os.system("daf.mc -r {}".format(value))
        self.counters_scroll_area()
        self.set_xlabel_combobox_options()

    def set_counter_combobox_options(self):
        with open('/etc/xdg/scan-utils/config.yml') as conf:
            config_data = yaml.safe_load(conf)
        counters = config_data['counters'].keys()
        self.ui.comboBox_counters.addItems(counters)
        self.ui.comboBox_counters.setEditable(True)
        self.ui.comboBox_counters.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

    def set_xlabel_combobox_options(self):
        motors_now = ['points', 'huber_mu', 'huber_eta', 'huber_chi', 'huber_phi', 'huber_nu', 'huber_del']
        self.ui.comboBox_xlabel.clear()
        self.ui.comboBox_xlabel.addItems(motors_now)
        self.ui.comboBox_xlabel.setEditable(True)
        self.ui.comboBox_xlabel.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

    def remove_counter(self):
        getSelected = self.ui.treeWidget_counters.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            counter = baseNode.text(0)
            item = self.ui.listWidget_counters.currentItem()
            value = item.text()
            os.system("daf.mc -rc {} {}".format(value, counter))
            list_ = self.extract(self.ui.listWidget_counters)
            if list_.index(value) == 0 and len(list_) > 1:
                self.ui.listWidget_counters.setCurrentRow(1)
            else:
                self.ui.listWidget_counters.setCurrentRow(0)
            self.ui.listWidget_counters.setCurrentRow(list_.index(value))
        self.set_xlabel_combobox_options()

    def start_scan(self):
        if not self.scan:
            self.scan = True
            prefix = self.ui.lineEdit.text()
            file = self.ui.lineEdit_2.text()
            output = prefix + '/' + file
            hi = self.ui.lineEdit_hi.text()
            hf = self.ui.lineEdit_hf.text()
            ki = self.ui.lineEdit_ki.text()
            kf = self.ui.lineEdit_kf.text()
            li = self.ui.lineEdit_li.text()
            lf = self.ui.lineEdit_lf.text()
            hi = self.ui.lineEdit_hi.text()
            self.step = self.ui.lineEdit_step.text()
            time = self.ui.lineEdit_time.text()
            xlabel = self.ui.comboBox_xlabel.currentText()
            csv_fn = self.ui.lineEdit_csv_filename.text()
            
            os.system('echo "" > .my_scan_counter.csv')
            if self.ui.checkBox_only_csv.isChecked():
                subprocess.Popen('daf.scan {} {} {} {} {} {} {} -t {} -n {} -x {} -o {} -c -g'.format(hi, ki, li, hf, kf, lf, self.step, time, csv_fn, xlabel, output), 
                    shell = True)
            else:
                subprocess.Popen('daf.scan {} {} {} {} {} {} {} -t {} -n {} -x {} -o {} -g'.format(hi, ki, li, hf, kf, lf, self.step, time, csv_fn, xlabel, output), 
                    shell=True)

    def progress_bar(self, fname = '.my_scan_counter.csv'):
        if self.scan:
            self.ui.progressBar.show()
            self.ui.label_generating_points.show()
            with open(fname) as f:
                lines = 0
                for i in f:
                    lines += 1
            percentage =  ((lines-1) / (int(self.step) + 1))*100
            self.ui.progressBar.setValue(int(percentage))
            if (percentage) >= 100:
                self.ui.progressBar.hide()
                self.ui.label_generating_points.hide()
                self.scan = False
                self.ui.progressBar.setValue(0)


    def update(self):        
        # if self.delay_counter == self.delay:
        #     self.rmap_widget(data_to_update['dargs'])
        #     self.delay_counter = 0

        self.refresh_pydm_motors()
        self.progress_bar()


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
        self.ui.label_samp_a.setText(lb(str(data_to_update['samp_info'][1])))
        self.ui.label_samp_b.setText(lb(str(data_to_update['samp_info'][2])))
        self.ui.label_samp_c.setText(lb(str(data_to_update['samp_info'][3])))
        self.ui.label_samp_alpha.setText(lb(str(data_to_update['samp_info'][4])))
        self.ui.label_samp_beta.setText(lb(str(data_to_update['samp_info'][5])))
        self.ui.label_samp_gamma.setText(lb(str(data_to_update['samp_info'][6])))
        

        #Update status Matrixes
        #U
        header_U = self.tableWidget_U.horizontalHeader()
        for row in range(self.tableWidget_U.rowCount()):
            for column in range(self.tableWidget_U.columnCount()):
                item = QTableWidgetItem(str(data_to_update['U'][row][column]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  
                self.tableWidget_U.setItem(row, column, item)
            header_U.setResizeMode(row, QHeaderView.Stretch)

        #UB
        header_UB = self.tableWidget_UB.horizontalHeader()
        for row in range(self.tableWidget_UB.rowCount()):
            for column in range(self.tableWidget_UB.columnCount()):
                item = QTableWidgetItem(str(data_to_update['UB'][row][column]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget_UB.setItem(row, column, item)
            header_UB.setResizeMode(row, QHeaderView.Stretch)
        
        #Update motor bounds
        self.ui.label_mu_bounds_ll.setText(str(data_to_update['bounds']["mu"][0]))
        self.ui.label_mu_bounds_hl.setText(str(data_to_update['bounds']["mu"][1]))

        self.ui.label_eta_bounds_ll.setText(str(data_to_update['bounds']["eta"][0]))
        self.ui.label_eta_bounds_hl.setText(str(data_to_update['bounds']["eta"][1]))

        self.ui.label_chi_bounds_ll.setText(str(data_to_update['bounds']["chi"][0]))
        self.ui.label_chi_bounds_hl.setText(str(data_to_update['bounds']["chi"][1]))

        self.ui.label_phi_bounds_ll.setText(str(data_to_update['bounds']["phi"][0]))
        self.ui.label_phi_bounds_hl.setText(str(data_to_update['bounds']["phi"][1]))

        self.ui.label_nu_bounds_ll.setText(str(data_to_update['bounds']["nu"][0]))
        self.ui.label_nu_bounds_hl.setText(str(data_to_update['bounds']["nu"][1]))

        self.ui.label_del_bounds_ll.setText(str(data_to_update['bounds']["del"][0]))
        self.ui.label_del_bounds_hl.setText(str(data_to_update['bounds']["del"][1]))

        self.delay_counter += 1
