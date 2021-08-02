#!/usr/bin/env python3

import numpy as np
import yaml


data = {'Mode': '2052',
		'Material' : 'Si',
		'IDir' : [0,1,0],
		'NDir' : [0,0,1],
		'RDir' : [0,0,1],
		'Sampleor' : 'z+',
		'Energy' : 8000,
		'bound_Mu' : [-20.0, 160.0],
		'bound_Eta' : [-20.0, 160.0],
		'bound_Chi' : [-5.0, 95.0],
		'bound_Phi' : [-400.0, 400.0],
		'bound_Nu': [-20.0, 160.0],
		'bound_Del': [-20.0, 160.0],
		'hklnow' : [0, 0, 0],
		'hkl1' : '',
		'hkl2' : '',
		'hkl3' : '',
		'angs1' : '',
		'angs2' : '',
		'angs3' : '',
		'Print_marker' : '',
		'Print_cmarker' : '',
		'Print_space' : '',
		'hkl' : '',
		'cons_Mu' : 0.0,
		'cons_Eta' : 0.0,
		'cons_Chi' : 0.0,
		'cons_Phi' : 0.0,
		'cons_Nu' : 0.0,
		'cons_Del' : 0.0,
		'cons_alpha' : 0.0,
		'cons_beta' : 0.0,
		'cons_psi' : 0.0,
		'cons_omega' : 0.0,
		'cons_qaz' : 0.0,
		'cons_naz' : 0.0,
		'Mu': 0.0,
		'Eta' : 0.0,
		'Chi' : 0.0,
		'Phi' : 0.0,
		'Nu' : 0.0,
		'Del' : 0.0,
		'tt' : 0.0,
		'theta' : 0.0,
		'alpha' : 0.0,
		'qaz' : 90.0,
		'naz' : 0.0,
		'tau' : 0.0,
		'psi' : 0.0,
		'beta' : 0.0,
		'omega' : 0.0,
		'U_mat' : [[1., 0., 0.],[0., 1., 0.],[0., 0., 1.]],
		'UB_mat' : [[1.15690279e+00, 0., 0.],[0., 1.15690279e+00, 0.],[0., 0., 1.15690279e+00]],
		'lparam_a' : 0.0,
		'lparam_b' : 0.0,
		'lparam_c' : 0.0,
		'lparam_alpha' : 0.0,
		'lparam_beta' : 0.0,
		'lparam_gama' : 0.0,
		'Max_diff' : 0.1,
		'scan_name' : 'scan_test',
		'separator' : ',',
		'macro_flag' : False,
		'macro_file' : 'macro',
		'setup' : 'default',
		'user_samples' : {},
		'setup_desc' : ''





}

with open('default', 'w') as stream:
	yaml.dump(data, stream, allow_unicode=False)

