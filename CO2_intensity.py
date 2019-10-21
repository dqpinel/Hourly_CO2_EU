# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 12:24:22 2019

@author: kasperet
"""

import pandas as pd
import numpy as np
from tqdm import tqdm


def CO2_intensity(Data,E_factors,year):
    #%%
    
    #Assume data is matrix as Z in the original script
    
    """
    Need to find:
    - Zones list (or place to find the range of it)
    - 
    """
    

    
    #Get list of zones that are included
    Zones = []
    for zone in Data:
        Zones.append(zone)
    
    #Get list of columns in total
    Columns = []
    for col in Data["NO1"]:
        Columns.append(col)
    
    #Get list of columns that are import based
    Imports = []
    Imports_zones = []
    Imports_only = []
    
    for col in Data["NO1"]:
        if col[0:7] == "Imports":
            Imports.append(col)
            for zone in Zones:
                if col[13:] == zone:
                    Imports_zones.append(col)
    for col in Imports:
        if col[13:] not in Zones:
            Imports_only.append(col)
        

    #Get list of columns that are generation based
    Generation = []
    for col in Data["NO1"]:
        if col[-3:] == "Gen":
            Generation.append(col)
    
    #Get list of all the time steps
    Time_steps = []
    for row in Data["NO1"].index:
        Time_steps.append(row)
    
    #Emission = {}
    Emission = pd.DataFrame(0,index = Time_steps,columns = Zones)
    mix_country = {}
    Tech_emission = {}
    
    zone_identity = np.zeros((len(Zones),len(Zones)))
    for i in range(len(Zones)):
        zone_identity[i,i] = 1
        
    
    y_zone = {}
    for i in range(len(Zones)):
        zone = Zones[i]
        y_zone[zone] = zone_identity[i,:]
        
    
    
    E_fact = pd.DataFrame(columns = Generation+Imports_only)
    for col in Generation:
        E_fact.at[0,col] = E_factors[2][col]
    
    for col in Imports_only:
        E_fact.at[0,col] = E_factors[2][col[13:]]
    
    
    
    
    
        
    #For each hour in the year
    for h in tqdm(Time_steps):
    
        mix_country[h] = pd.DataFrame(index = Generation+Imports_only, columns = Zones)
        
        
        
        #Create empty dataframe
        Z_tot = pd.DataFrame(index = Columns, columns = Zones) #94x43
        
        #Insert relevant data for each tech, and for each zone
        for row in Columns:
            for col in Zones:
                Z_tot.at[row,col]  = Data[col][row][h]
        
        #Sum up the generation from each tech for each zone [1 X zones]
        Z_sum = Z_tot.sum(axis = 0)
        
        #Sets up a diagonal matrix with the sum of generation [zones X zones]
        Z_diag = pd.DataFrame(0,index = Z_sum.index, columns = Z_sum.index)
        for zone2 in Zones:
            Z_diag.at[zone2,zone2] = Z_sum[zone2]
        
        #Inverse of the diagonal matrix [zones X zones]
        Z_trans = pd.DataFrame(np.linalg.pinv(Z_diag.values), index = Z_diag.columns, columns = Z_diag.index)
        
        #Finds the weighted generation from each source for each zone [tech X zones]
        A1 = Z_tot.dot(Z_trans)
        
        #Get the data based on imports
        A = pd.DataFrame(index = Imports_zones, columns = Zones, dtype = float) #WRONG! NOOB!
        #It should be import from nodes that we have in the system!
        
        for row2 in Imports_zones:
            for col2 in Zones:
                A.at[row2,col2]  = A1[col2][row2]
        
        A_gen = pd.DataFrame(index = Generation+Imports_only, columns = Zones,dtype = float)
        for row2 in Generation+Imports_only:
            for col2 in Zones:
                A_gen.at[row2,col2]  = A1[col2][row2]
        
        IA = zone_identity-A
        IA_inv = pd.DataFrame(np.linalg.pinv(IA.values), index = IA.columns, columns = IA.index)
        t_IA = A_gen.dot(IA_inv)
        
        #Set up identity matrix for the current zone
        
        for zone in Zones:
            mix_country[h][zone] = t_IA.dot(y_zone[zone])
            
            Emission.at[h,zone] = E_fact.dot(mix_country[h][zone])
        #for row in Generation+Imports_only
    
    #Change layout for tech per country
    tech_country = {}
    for zone in Zones:
        tech_country[zone] = pd.DataFrame(index = Time_steps,columns = Generation+Imports_only)
        
        for row in Time_steps:
            for col in Generation+Imports_only:
                tech_country[zone].at[row,col] = mix_country[row][zone][col]
        
    
    #Finished calculating
    """
    Start storing the code
    """
    
    with pd.ExcelWriter("CO2_intensity_"+str(year)+ ".xlsx") as writer:
         
        Emission.to_excel(writer,sheet_name = "Intensity")

    with pd.ExcelWriter("CO2_technology_"+str(year)+".xlsx") as writer:
        for zone in tqdm(tech_country):
            tech_country[zone].to_excel(writer,sheet_name = zone)
    return()

      #%%      
    """
            Tech_emission[zone][h] = {}
            
            Z_tot = 1337
            
            Z_tot = 1337 #Z_tot = AxB -> A = number of sources for generation, B = number of zones
            A1 = Z_tot*diag(sum(Z_tot[zone]))^(-1) # AxB, same as Z_tot, but now is "percentage" (sum of columns == 1)
            A = A1[42:55,:] #BxB -> The data regarding import of electricity, the values from each of the zones imported from
            t = A1[rows2remove,:] # CxB -> C = number of import sources from own generation 
            t_mix = t*[I-A]^(-1)*y[zone] # Cx1, y[zone] is a matrix having the 1 value for the corresponding zone
            e[zone][h] = Emission_factors*t_mix # 1x8760 -> CO2 intensity in hour h
            tech_per_time[zone][h][source] = t_mix
    
    """
    return(Data)