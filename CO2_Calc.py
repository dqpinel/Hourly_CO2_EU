# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:04:37 2019

@author: dqpinel
"""

import Load_Data as load
import pandas as pd
#%%

year=2015

#%%

Z=load.load_data(year)

#%%

Emissions_Factors=pd.read_excel('Emission_Factors.xlsx',header=None)
