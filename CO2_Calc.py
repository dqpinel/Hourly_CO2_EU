# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:04:37 2019

@author: dqpinel
"""

import Load_Data as load
import CO2_intensity as CO2
import pandas as pd
#%%

for year in [2017,2018]:
        
    #%%
    
    Z=load.load_data(year)
    
    Z = load.remove_extra_zones(Z)
    
    #%%
    
    Emissions_Factors=pd.read_excel('Emission_Factors.xlsx',header=None,index_col=0)
    
    #%%
    Results = CO2.CO2_intensity(Z,Emissions_Factors,year)