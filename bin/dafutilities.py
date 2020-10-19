#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 12:51:42 2020

@author: hugo
"""
import os
import sys


def dict_conv():
    os.system("head -63 .Experiment > Experiment1")
    os.system("rm .Experiment; mv Experiment1 \.Experiment")
    
    with open('.Experiment', 'r') as exp:
        
        lines = exp.readlines()
        dict_args = {i.split('=')[0]:i.split('=')[1].split('\n')[0] for i in lines if i != '\n'}
    return dict_args
