# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 14:07:07 2019

@author: dqpinel
"""

import pandas as pd
import numpy as np
from tqdm import tqdm

def load_data(year):
    """ Load the data to use to calculate the Hourly Emission Factors of CO2. """
    
#    pd.options.mode.chained_assignment = None
    monthly_gen={'January':pd.read_csv('Data\%s_1_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'February':pd.read_csv('Data\%s_2_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'March':pd.read_csv('Data\%s_3_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'April':pd.read_csv('Data\%s_4_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'May':pd.read_csv('Data\%s_5_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'June':pd.read_csv('Data\%s_6_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'July':pd.read_csv('Data\%s_7_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'August':pd.read_csv('Data\%s_8_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'September':pd.read_csv('Data\%s_9_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'October':pd.read_csv('Data\%s_10_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'November':pd.read_csv('Data\%s_11_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t"),'December':pd.read_csv('Data\%s_12_AggregatedGenerationPerType.csv'%year,encoding = "utf-16", sep="\t")}
    monthly_flow={'January':pd.read_csv('Data\%s_1_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'February':pd.read_csv('Data\%s_2_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'March':pd.read_csv('Data\%s_3_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'April':pd.read_csv('Data\%s_4_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'May':pd.read_csv('Data\%s_5_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'June':pd.read_csv('Data\%s_6_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'July':pd.read_csv('Data\%s_7_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'August':pd.read_csv('Data\%s_8_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'September':pd.read_csv('Data\%s_9_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'October':pd.read_csv('Data\%s_10_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'November':pd.read_csv('Data\%s_11_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t"),'December':pd.read_csv('Data\%s_12_CrossBorderPhysicalFlow.csv'%year,encoding = "utf-16", sep="\t")}

    for key in monthly_gen.keys():
        monthly_gen[key]=monthly_gen[key][monthly_gen[key]['AreaTypeCode']=='BZN'] # Removing data that is not for bidding zone, ie data for country or for control area
        monthly_gen[key].index=pd.to_datetime(monthly_gen[key].DateTime)
        monthly_gen[key]=monthly_gen[key].drop(['Year','Month','Day','DateTime'])
    for key in monthly_flow.keys():
        monthly_flow[key]=monthly_flow[key][monthly_flow[key]['OutAreaTypeCode']=='BZN']
        monthly_flow[key].index=pd.to_datetime(monthly_flow[key].DateTime)
        monthly_flow[key]=monthly_flow[key].drop(['Year','Month','Day','DateTime'])
    
    Z={}
    for bid_zone in monthly_gen['January'].sort_values(by=['MapCode'],axis=0).MapCode.unique(): #for each unique bidding zone in alphabetical order
        Z.update({bid_zone:pd.DataFrame(index=pd.date_range('1/1/%s'%year, end='31/12/%s 23:00'%year, freq='H'),columns=['Biomass_Gen','Biomass_Cons','Fossil Brown coal/Lignite_Gen','Fossil Brown coal/Lignite_Cons','Fossil Coal-derived gas_Gen','Fossil Coal-derived gas_Cons','Fossil Gas_Gen','Fossil Gas_Cons','Fossil Hard coal_Gen','Fossil Hard coal_Cons','Fossil Oil_Gen','Fossil Oil_Cons','Fossil Oil shale_Gen','Fossil Oil shale_Cons','Fossil Peat_Gen','Fossil Peat_Cons','Geothermal_Gen','Geothermal_Cons','Hydro Pumped Storage_Gen','Hydro Pumped Storage_Cons','Hydro Run-of-river and poundage_Gen','Hydro Run-of-river and poundage_Cons','Hydro Water Reservoir_Gen','Hydro Water Reservoir_Cons','Marine_Gen','Marine_Cons','Nuclear_Gen','Nuclear_Cons','Other_Gen','Other_Cons','Other renewable_Gen','Other renewable_Cons','Solar_Gen','Solar_Cons','Waste_Gen','Waste_Cons','Wind Offshore_Gen','Wind Offshore_Cons','Wind Onshore_Gen','Wind Onshore_Cons'])}) # Create keys for the dictionary
    
    length={}
    for month in monthly_flow.keys():
        length.update({month:len(monthly_flow[month].sort_values(by=['OutMapCode'],axis=0).OutMapCode.unique())})
        
    for bid_zone1 in monthly_gen['January'].sort_values(by=['MapCode'],axis=0).MapCode.unique():
        for bid_zone2 in monthly_flow[max(length, key=length.get)].sort_values(by=['OutMapCode'],axis=0).OutMapCode.unique(): #use the month that has the most zones
            Z[bid_zone1]['Imports_from_%s'%bid_zone2]=np.nan

#Method 2 by blocks
    for bid_zone in tqdm(Z.keys()):# for each bidding zone
        for month in tqdm(monthly_gen.keys()): # for each month
            for prod_tech in monthly_gen[month][monthly_gen[month]['MapCode']==bid_zone].ProductionType.unique(): # for each unique technology type in the bidding zone
                ind=monthly_gen[month][(monthly_gen[month]['ProductionType']==prod_tech)&(monthly_gen[month]['MapCode']==bid_zone)]['ActualGenerationOutput'].resample('H').mean().index #get the index of the hours of the month
                Z[bid_zone]['%s_Gen'%prod_tech][ind[0]:ind[-1]]=monthly_gen[month][(monthly_gen[month]['ProductionType']==prod_tech)&(monthly_gen[month]['MapCode']==bid_zone)]['ActualGenerationOutput'].resample('H').mean() # resample to hourly data if necessary and copy the value to Z
                Z[bid_zone]['%s_Cons'%prod_tech][ind[0]:ind[-1]]=monthly_gen[month][(monthly_gen[month]['ProductionType']==prod_tech)&(monthly_gen[month]['MapCode']==bid_zone)]['ActualConsumption'].resample('H').mean()

    for bid_zone_to in tqdm(Z.keys()):# for each bidding zone
        for month in tqdm(monthly_flow.keys()):
            for bid_zone_from in monthly_flow[month][monthly_flow[month]['InMapCode']==bid_zone_to].OutMapCode.unique():
                ind=monthly_flow[month][(monthly_flow[month]['InMapCode']==bid_zone_to)&(monthly_flow[month]['OutMapCode']==bid_zone_from)]['FlowValue'].resample('H').mean().index
                Z[bid_zone_to]['Imports_from_%s'%bid_zone_from][ind[0]:ind[-1]]=monthly_flow[month][(monthly_flow[month]['InMapCode']==bid_zone_to)&(monthly_flow[month]['OutMapCode']==bid_zone_from)]['FlowValue'].resample('H').mean()

    for bid_zone in Z.keys():
        Z[bid_zone]=Z[bid_zone].fillna(0)
        
    SE_Prod=pd.read_excel('Data\statistik-per-elomrade-och-timme-%s.xlsx'%year)
    SE_tech={'Ospec.':'Other_Gen','Vattenkraft':'Hydro Water Reservoir_Gen','Vindkraft':'Wind Onshore_Gen','Kärnkraft':'Nuclear_Gen','Värmekraft':'Waste_Gen','Gast./diesel':'Fossil Gas_Gen','Solkraft':'Solar_Gen'}
    
    for tech in SE_tech.keys():
        if tech in SE_Prod.columns:
            for area in [tech,'%s.1'%tech,'%s.2'%tech,'%s.3'%tech]:
                if area in SE_Prod.columns:
                    for bid_zone in ['SE1','SE2','SE3','SE4']:
                        if SE_Prod[area][1]==bid_zone:
                            if SE_Prod[area][0]=='produktion':
                                Z[bid_zone][SE_tech[tech]][0:len(Z[bid_zone][SE_tech[tech]])]=SE_Prod[area][4:]
                    
    return Z


#year=2015 # or 2016, 2017, 2018
#Z=load_data(year)