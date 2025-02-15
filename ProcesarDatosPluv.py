# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 18:17:45 2023

@author: sanba


EM20694 <- IEI
EM43835 <- Hidraulica

"""

#Import required libraries
import os
import sys
import glob
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

#determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

#change working directory
os.chdir(application_path)

#Create empty data frame to store the time series
EM20694 = pd.DataFrame(columns = ["Date", "P1", "P2"])
EM43835 = pd.DataFrame(columns = ["Date", "P3", "P4"])

#Calibration curves
def CalP1(P1):
    P1 = round(P1/0.2, 0)
    P1 = P1 * 0.187
    P1 = P1 / (1/60)
    
    if(P1 <= 72.94):
        P1 = P1 * (1 + 0.1389)    
    elif(P1 > 72.94):
        P1 = P1 * ((P1 * 0.0125 - 0.7729) + 1)
    
    P1 = P1 * (1/60)
    return round(P1,4)

def CalP2(P2):
    P2 = round(P2/0.2, 0)
    P2 = P2 * 0.187
    P2 = P2 / (1/60)
    
    if(P2 <= 62.33):
        P2 = P2 * (1 + 0.1310)    
    elif(P2 > 62.33):
        P2 = P2 * ((P2 * 0.0108 - 0.5422) + 1)
    
    P2 = P2 * (1/60)
    return round(P2,4)

def CalP3(P3):
    P3 = round(P3/0.2, 0)
    P3 = P3 * 0.187
    P3 = P3 / (1/60)
    
    if(P3 <= 46.89):
        P3 = P3 * (1 + 0.1604)    
    elif(P3 > 46.89):
        P3 = P3 * ((P3 * 0.0037 - 0.0131) + 1)
    
    P3 = P3 * (1/60)
    return round(P3,4)

def CalP4(P4):
    P4 = round(P4/0.2, 0)
    P4 = P4 * 0.187
    P4 = P4 / (1/60)
    
    if(P4 <= 45.13):
        P4 = P4 * (1 + 0.0610)    
    elif(P4 > 45.13):
        P4 = P4 * ((P4 * 0.002837 - 0.067054) + 1)
    
    P4 = P4 * (1/60)
    return round(P4,4)

for i in glob.glob("*.xls"):
    
    #Read the excel file with precipitation records
    df = pd.read_excel(i)
    df = df.drop([0,1])
    
    #Concatenate data in a single data frame per pluviograph
    if(df.columns[0] == 'EM20694'):
        df.drop(['Port 3', 'Port 4', 'Port 5'], axis=1, inplace=True)
        df.rename(columns = {'EM20694':'Date', 'Port 1':'P1', 'Port 2':'P2'}, inplace = True)
        EM20694 = pd.concat([EM20694,df])
    elif(df.columns[0] == 'EM43835'):
        df.drop(['Port 1', 'Port 2', 'Port 5'], axis=1, inplace=True)
        df.rename(columns = {'EM43835':'Date', 'Port 3':'P3', 'Port 4':'P4'}, inplace = True)
        EM43835 = pd.concat([EM43835,df])
    
    del df
    
#Correct precipitation with calibration curves
EM20694['P1'] = EM20694['P1'].apply(CalP1)
EM20694['P2'] = EM20694['P2'].apply(CalP2)
EM43835['P3'] = EM43835['P3'].apply(CalP3)
EM43835['P4'] = EM43835['P4'].apply(CalP4)

#convert to dates datetime object
EM20694['Date'] = pd.to_datetime(EM20694['Date'])
EM43835['Date'] = pd.to_datetime(EM43835['Date'])

#Sort dataframes by date
EM20694.sort_values(by='Date', inplace=True)
EM43835.sort_values(by='Date', inplace=True)

#Reset index values of final data frames
EM20694.reset_index(drop = True, inplace = True)
EM43835.reset_index(drop = True, inplace = True)

#introduce NA rows in missing dates
for i in range(1, int((EM20694.iloc[len(EM20694)-1,0]-EM20694.iloc[0,0]).days*1440 + (EM20694.iloc[len(EM20694)-1,0]-EM20694.iloc[0,0]).seconds/60) + 1):
    if((EM20694.iloc[i,0] - EM20694.iloc[i-1,0]) != timedelta(minutes=1)):
        newLine = pd.DataFrame({"Date": pd.date_range(EM20694.iloc[i-1,0] + timedelta(minutes=1), periods=int((EM20694.iloc[i,0] - EM20694.iloc[i-1,0]).days * 1440 + (EM20694.iloc[i,0] - EM20694.iloc[i-1,0]).seconds/60 - 1), freq='T').tolist()})
        EM20694 = pd.concat([EM20694.iloc[:i], newLine, EM20694.iloc[i:]]).reset_index(drop=True)

for i in range(1, int((EM43835.iloc[len(EM43835)-1,0]-EM43835.iloc[0,0]).days*1440 + (EM43835.iloc[len(EM43835)-1,0]-EM43835.iloc[0,0]).seconds/60) + 1):
    if((EM43835.iloc[i,0] - EM43835.iloc[i-1,0]) != timedelta(minutes=1)):
        newLine = pd.DataFrame({"Date": pd.date_range(EM43835.iloc[i-1,0] + timedelta(minutes=1), periods=int((EM43835.iloc[i,0] - EM43835.iloc[i-1,0]).days * 1440 + (EM43835.iloc[i,0] - EM43835.iloc[i-1,0]).seconds/60 - 1), freq='T').tolist()})
        EM43835 = pd.concat([EM43835.iloc[:i], newLine, EM43835.iloc[i:]]).reset_index(drop=True)

#Generate csv files with outputs
EM20694.to_csv('EM20694_IEI.csv', index = False)
EM43835.to_csv('EM43835_Hidraulica.csv', index = False)

#Generate graphs
plt.rcParams.update({'font.size': 8})

plt.plot(EM20694.iloc[:,0], EM20694.iloc[:,2], label= "P2", color='red', linewidth = 1)
plt.plot(EM20694.iloc[:,0], EM20694.iloc[:,1], label= "P1", color='black', linestyle='dashed', linewidth = 1, alpha=0.6)
plt.ylabel('Precipitación (mm)')
plt.title('EM20694_IEI')
plt.legend()
plt.savefig('EM20694_IEI.png', dpi = 900, bbox_inches='tight')
plt.close()

plt.plot(EM43835.iloc[:,0], EM43835.iloc[:,2], label= "P4", color='red', linewidth = 1)
plt.plot(EM43835.iloc[:,0], EM43835.iloc[:,1], label= "P3", color='black', linestyle='dashed', linewidth = 1, alpha=0.6)
plt.ylabel('Precipitación (mm)')
plt.title('EM43835_Hidraulica')
plt.legend()
plt.savefig('EM43835_Hidraulica.png', dpi = 900, bbox_inches='tight')
plt.close()


















   