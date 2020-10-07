#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:19:01 2020

@author: hugo
"""
# args = list()
with open('Experiment', 'r') as exp:
 
    lines = exp.readlines()
    args = [i.split('=')[1].split('\n')[0] for i in lines if i != '\n']

print(type(args[1]))
 

            
          

