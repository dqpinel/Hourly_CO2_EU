# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 12:24:22 2019
@author: kasperet
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
import sys

def CO2_intensity(Data,E_factors,year):
    #%%

    
    """
    This function takes in a huge list of power production for the european power system
    Based on the power production per bidding zone, the generation source in each zone and exchange between the zones
    The function will calculate the mix of electricity consumption for each bidding zone based on technology
    This is based on local production, and interaction around
    Then, the model goes one step further and calculates the corresponding emission value for the bidding zone
    This is based on the electricity mix and their corresponding emission factors [given in gram/kWh]
    
    The following information is imported to the function:    
        
    Data contains the following (in the given order, aka [1][2][3]):
        Each bidding zone that has been acquired by input data
        Generation amount from each generation type (including import from other bidding zones)
        Time step of the year (from first to last hour of the year)
    
    Data is thus in the following dimension: [BZN x Tech x hours]
    
    E_factors contain the emission factor for the technology types [gram/kWh]
    Note: Bidding zones not included but importing to an existing bidding zone, is given as a generating unit for that node.
    These generating units also have an emission factor corresponding to their "expected" values
    
    year is the year we are calculating from. This is only used for storing the data in an excel-file.
    
    We distuingish between the following:
        BZN - This contains information regarding the bidding zones we have in our system
        IMPO- This contains information regarding bidding zones simplified to be a generator for certain bidding zones
        IMP - This contains information regarding power exchange between bidding zones
        TEC - This contains information regarding technologies that produces electricity in the system
    
    """
    
    #We need to find the actual bidding zones that is being considered
    Zones = []
    for zone in Data:
        Zones.append(zone)

    #We need a list of all technologies that are generating power for a bidding zone, including import.
    #Thus, this list contains all technologies, and all import possibilities
    #We use 
    List_TEC_IMP_IMPO = []
    for zone in Data:
        for col in Data[zone]:
            List_TEC_IMP_IMPO.append(col)
        break
    
    #Here, we divide the lists from List_TEC_IMP_GEN into imports, imports from bidding zones, and imports for simplified "bidding zones"
    List_IMP_IMPO = []  #Dimension: [IMP+IMPO x 1]
    List_IMP = []       #Dimension: [IMP x 1]
    List_IMPO = []      #Dimension: [IMPO x 1]
    
    #In this for loop, we extract all imports that exist into the corresponding lists.
    #We loop for each bidding zone, despite only analyzing for 1
    for bzn in Data:
        #We loop for each column data, which contains information on generation and imports
        for col in Data[bzn]:
            
            #If the column value starts with Imports, then it is import data
            if col[0:7] == "Imports":
                List_IMP_IMPO.append(col)
                
                #If the import is found in bidding zones, then we store it in the corresponding list
                for zone in Zones:
                    if col[13:] == zone:
                        List_IMP.append(col)
        #Break after 1 bidding zone, all is the same so it is not necessary
        break
    
    #For each import including generation nodes
    for col in List_IMP_IMPO:
        #If the import is not from an existing bidding zone, we store it in this list
        if col[13:] not in Zones:
            List_IMPO.append(col)
        

    #Get list of technologies
    List_TEC = [] #Dimension: [TEC x 1]
    
    #For each bidding zone
    for bzn in Data:
        #For each column
        for col in Data[bzn]:
            #If the column name ends with Gen, it is a technology
            if col[-3:] == "Gen":
                #We store the technology name
                List_TEC.append(col)
        break
    
    #Get list of all the time steps
    Time_steps = [] #Dimension: [Hours x 1]
    
    for bzn in Data:
        #We do for each row of the data, so for each hour of the year
        for row in Data[bzn].index:
            Time_steps.append(row)
        break
    
    #We create an Emission pandas dictionary with initial value equal to 0
    Emission = pd.DataFrame(0,index = Time_steps,columns = Zones, dtype = float) #Dimension: [Hours x BZN]

    #Create dictionary containing information on the generation mix of each bidding zone
    mix_country = {}
        
    #In the calculation, it is necessary to create an identity matrix
    #THis is done manually in this case.
    
    zone_identity = np.zeros((len(Zones),len(Zones))) #Dimension: [BZN x BZN]
    for i in range(len(Zones)):
        zone_identity[i,i] = 1
        
    #We also need to create a matrix that is [BZN x 1], which only contain information on what BZN we look at
    #This is done by creating these [1 0 0 0 ... 0], [0 1 0 0 0 ... 0] stored for each zone
    #The 1 value is indicating the position in the BZN matrix
    
    #Create dictionary for each BZN
    y_zone = {}
    for i in range(len(Zones)):
        #For each bidding zone, we store the identity matrix of that corresponding BZN
        zone = Zones[i]
        y_zone[zone] = zone_identity[i,:]
        
    
    #Create a dataframe containing information of emission value for both TEC and IMPO
    Emission_factor = pd.DataFrame(columns = List_TEC+List_IMPO) #Dimension: [1 x TEC+IMPO]
    
    #Store values from technologies
    for col in List_TEC:
        Emission_factor.at[0,col] = E_factors[2][col]
    
    #Store values from IMPO
    for col in List_IMPO:
        Emission_factor.at[0,col] = E_factors[2][col[13:]]
    
    """
    Then, we start with analyzing for each time step existing
    """
    
    #For each hour in the year
    for h in tqdm(Time_steps):
        
        #Create an empty dataframe for mix of countries for this specific time step
        mix_country[h] = pd.DataFrame(index = List_TEC + List_IMPO, columns = Zones, dtype = float)
        
        #Create empty dataframe containing information from input data. Contains generation and import info from each BZN
        Generation_info = pd.DataFrame(index = List_TEC_IMP_IMPO, columns = Zones) #Dimension: [TEC+IMP+IMPO x BZN]
        
        #Insert relevant data for each tech, and for each zone
        for row in List_TEC_IMP_IMPO:
            for col in Zones:
                Generation_info.at[row,col]  = Data[col][row][h]
        
        #Sum up the generation from each tech for each zone
        Gen_summed = Generation_info.sum(axis = 0) #Dimension: [1 x BZN] Contains summed generation quantity for each BZN
        
        #Sets up a diagonal matrix with the sum of generation [zones X zones]
        Gen_diagonal = pd.DataFrame(0,index = Gen_summed.index, columns = Gen_summed.index) #Dimension: [BZN x BZN]
        for zone2 in Zones:
            Gen_diagonal.at[zone2,zone2] = Gen_summed[zone2]
    
        #Inverse of the diagonal matrix [zones X zones]
        #Gives us the per unit production of each node based on total production
        Gen_pu = pd.DataFrame(np.linalg.pinv(Gen_diagonal.values), index = Gen_diagonal.columns, columns = Gen_diagonal.index) #Dimension: [BZN x BZN]
        
        #Finds the weighted generation from each source for each zone [tech X zones]
        Gen_info_weighted = Generation_info.dot(Gen_pu) #Dimension: [TEC+IMP+IMPO x BZN]
        
        #Get the data based on imports
        IMP_from_BZN = pd.DataFrame(index = List_IMP, columns = Zones, dtype = float) #Dimension: [IMP x BZN]
        #It should be import from nodes that we have in the system!
              
        #Store the data from import
        for row2 in List_IMP:
            for col2 in Zones:
                IMP_from_BZN.at[row2,col2]  = Gen_info_weighted[col2][row2]
        
        #Generate dataframe containing production from technologies + IMPO
        Gen_TEC_IMPO = pd.DataFrame(index = List_TEC+List_IMPO, columns = Zones,dtype = float) #Dimension: [TEC+IMPO x BZN]
        
        #Store the relevant info for technologies and IMPO        
        for row2 in List_TEC+List_IMPO:
            for col2 in Zones:
                Gen_TEC_IMPO.at[row2,col2]  = Gen_info_weighted[col2][row2]
        
        #Now, we create a matrix telling us the connection between each BZN in terms of self-consumption and power exchange
        #We therefore have 1 for each bidding zone telling: We import 1 unit to ourselves. The imports from others will be given as negative
        BZN_power_exchange = zone_identity-IMP_from_BZN #Dimension: [IMP x BZN]
        
        #We then invert it, which will give us information on how each BZN affects the others. This shows how each BZN affects each BZN consumption
        BZN_power_exchange_total = pd.DataFrame(np.linalg.pinv(BZN_power_exchange.values), index = BZN_power_exchange.columns, columns = BZN_power_exchange.index) #Dimension: [BZN x IMP]
        
        #We then combine this with the technologies, to find what technology origin each country consumes of power
        BZN_consumption_tec = Gen_TEC_IMPO.dot(BZN_power_exchange_total) #Dimension: [TEC x BZN]
        #Set up identity matrix for the current zone
        
        #We then store this information for each bidding zone
        for zone in Zones:
            
            #We store the mix of power from each country
            mix_country[h][zone] = BZN_consumption_tec.dot(y_zone[zone])
            
            #We store the emission that each country then would have based on their electricity consumption based on technologies
            Emission.at[h,zone] = Emission_factor.dot(mix_country[h][zone])
        #for row in Generation+Imports_only
        
    #Change layout for tech per BZN to make it easier to store in Excel files
    tech_BZN = {}
    #Store for each zone the consumption for each bidding zone for each technology
    for zone in Zones:
        
        tech_BZN[zone] = pd.DataFrame(index = Time_steps,columns = List_TEC+List_IMPO)
        
        #For each time step
        for row in Time_steps:
            for col in List_TEC+List_IMPO:
                tech_BZN[zone].at[row,col] = mix_country[row][zone][col]
        
    #Finished calculating
    """
    Start storing the code
    """
    #Store the information of emissions into a separate excel file
    with pd.ExcelWriter("CO2_intensity_"+str(year)+ ".xlsx") as writer:
         
        Emission.to_excel(writer,sheet_name = "Intensity")

    #Store the information of technology mix to an excel file. Each sheet is for a bidding zone
    with pd.ExcelWriter("Cons_technology_"+str(year)+".xlsx") as writer:
        for zone in tqdm(tech_BZN):
            tech_BZN[zone].to_excel(writer,sheet_name = zone)
    
    return(Data)
