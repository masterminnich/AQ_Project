#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Better PurpleAir Reading Strategy (v4)

Slight modifications for AU HPC.

readData(sensor) Will read in data from PurpleAir file and save as a Nested Data Frame (or list of nested dfs) called SensorYearly_df
"""

import pandas as pd
import numpy as np
import os
import re
import datetime
from hampel_filter_pandas import hampel_filter_pandas
#import matplotlib.pyplot as plt2
import math



inputData_dt = 1440 #30
ws = 10 #window_size
n_sig = 3 #N-sigmas



d_range1 = "01-01"
d_range2 = "12-31"
d_range1_date = datetime.datetime.strptime(d_range1, '%m-%d')
d_range2_date = datetime.datetime.strptime(d_range2, '%m-%d')
d_range = d_range2_date - d_range1_date 
d_range_days = (d_range.days+1+math.ceil(d_range.seconds/86400)) #Rounds up days in range (yearly)
delta = datetime.timedelta(minutes=inputData_dt) #Defines dt step size

DataPerDay = 24*60/inputData_dt

#master_path = "/home/jm2511a/AQProject/15mi_radius"
#primary_data_dir = "/PurpleAirData_daily"
master_path = "/Users/josephminnich/Downloads/AQProject/ReadYearlyData(Covid_V3)" #/Files for HPC May24"
primary_data_dir = "/LA_5mi_r_daily_all"     #/PurpleAirData" 
list_of_dir = os.listdir(master_path+primary_data_dir)
try:
	list_of_dir.remove('.DS_Store')
except:
	"No .DS_Store file found."
string_of_dir = '|'.join(list_of_dir) #converts the list into a single string seperated by "|"
#path_A_primary = re.findall(r'([^@|]+Primary[^@|]+(?:.csv))',string_of_dir) #Returns the a list of arrays. Arrays contain data for all A (Primary) Sensors
sensor_names = re.findall(r'((\w+\s*\w*\s*\w*\s*\w*\s*\w*\s*)\s\(\w+\) \(\d+\.\d+ \-?\d+\.\d+\) Primary \d+_\w+ \d{2}_\d{2}_\d{4} \d{2}_\d{2}_\d{4}.csv)',string_of_dir)

sensorNames = []
sensorFullFileNames = []
Sensors=[sensorNames,sensorFullFileNames]
for s in range(len(sensor_names)):
    sensorFullFileNames.append(sensor_names[s][0])
    sensorNames.append(sensor_names[s][1])

def set_date_ranges(d_range1,d_range2):
    d_range1_date = datetime.datetime.strptime(d_range1, '%m-%d')
    d_range2_date = datetime.datetime.strptime(d_range2, '%m-%d')
    d_range = d_range2_date - d_range1_date 
    d_range_days = (d_range.days+1+math.ceil(d_range.seconds/86400)) #Rounds up days in range (yearly)
    return [d_range1,d_range2,d_range1_date,d_range2_date,d_range,d_range_days]
    
def get_date_ranges():
    return [d_range1,d_range2,d_range_days,DataPerDay]


"""Depreciated"""
def getDateList(START, END):
    RANGE = END - START
    Dlist = []
    for i in range(int(RANGE/delta)):
        d = START + i*delta
        d1 = datetime.datetime.strftime(d,'%Y-%m-%d %H:%M:%S %Z')
        d1 = d1 + "UTC"
        Dlist.append(d1)
        
    return Dlist



def getYearlyDateList(start_yr, range_1, range_2, yrs):
    START = datetime.datetime.strptime(range_1[5:], '%m-%d %H:%M:%S %Z')  #start_d[5:], '%m-%d %H:%M:%S %Z')
    END = datetime.datetime.strptime(range_2[5:], '%m-%d %H:%M:%S %Z')
    
    """get Yearly Date for 2020 range! when doing yearly dev"""
    
    RANGE = END - START
    END_RANGE = datetime.timedelta(days=365) - RANGE
    one_yr = datetime.timedelta(days=365)
    Dlist = []
    for yy in range(yrs):
        for i in range(int(RANGE/delta)+1):
            d = START + i*delta + (yy*one_yr)
            d1 = datetime.datetime.strftime(d,'%Y-%m-%d %H:%M:%S %Z')
            d1 = str(start_yr + yy) +"-"+ d1[5:] + "UTC"
            #print("i",i,"d1",d1)
            Dlist.append(d1)
        
    return Dlist

def getDateListForYearlyDataFrame(dataframe):
    start_d = dataframe[0]['created_at'].iloc[0]
    end_d = dataframe[-1]['created_at'].iloc[-1]
    START = datetime.datetime.strptime(start_d, '%Y-%m-%d %H:%M:%S %Z')
    END = datetime.datetime.strptime(end_d, '%Y-%m-%d %H:%M:%S %Z')
    RANGE = END - START
    Dlist = []
    for i in range(int(RANGE/delta)):
        d = START + i*delta
        d1 = datetime.datetime.strftime(d,'%Y-%m-%d %H:%M:%S %Z')
        d1 = d1 + "UTC"
        Dlist.append(d1)
        
    return Dlist

def filterNDs(Data): #Removes gaps (when the sensor fails to write a datapoint) and redundancies (duplicates)
    Data_np = Data.to_numpy()
    print(Data.shape)
    start_date_str = Data['created_at'][0]
    end_date_str = Data['created_at'].iloc[-1]
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S %Z')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S %Z')
    
    #df = pd.DataFrame(columns = ['created_at', 'PM1.0_CF1_ug/m3', 'PM2.5_CF1_ug/m3', 'PM10.0_CF1_ug/m3', 'UptimeMinutes', 'RSSI_dbm', 'Temperature_F', 'Humidity_%', 'PM2.5_ATM_ug/m3', 'Unnamed: 9'])
    Data_N = np.empty(10)
    
    dates_list = []
        
    date_length = end_date - start_date
    for i in range(int( (int(date_length.days) * DataPerDay) + int(date_length.seconds/1800))):  #Number of days in range * datapoints per day
        date = start_date + delta*i
        date_str = datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S %Z')
        date_str = date_str + "UTC"
        dates_list.append(date_str)
        
        try:
            row = Data['created_at'].values.tolist().index(date_str)
            Data_N = np.vstack((Data_N,Data_np[row]))
            #Append to calendar
        except:
            if i == 0:
                print("insert")
            else:
                print(".",end="")
            #print("insert! row " +str(i))
            ND = [date_str, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
            Data_N = np.vstack((Data_N,ND))
        
    print(".")
            
    Data_N = np.delete(Data_N, 0, 0) #Delete the first row because it is junk
    return Data_N


def removeGapsAndDupes(contData,sensorname): #Read then Save the Filtered Data. This only needs to be done once!
    print("removeGapsAndDupes("+str(sensorname)+")")
    Data1 = filterNDs(contData)
    a = pd.DataFrame(Data1)
    a.columns = contData.columns
    a.to_csv(master_path+primary_data_dir+"/"+sensorname+"_parsed.csv") #saves the file
    print("")
    
    return

#Create dataframe from file Remove leap days
def removeLeapDays(Data__):
    Yearly_Data = Data__
    U = [] #This is the new Yearly_Data list of dataframes
    for year in range(len(Yearly_Data)):
        a2 = [e[5:10] for e in Yearly_Data[year]['created_at'].tolist()] #list of all dates in mm/dd form
        list1 = []
        for i,d in enumerate(a2):
            if d == "02-29":
                list1.append(i)
        if len(list1) == 0:
            U.append(Yearly_Data[year])
        else:
            p = pd.concat([Yearly_Data[year][0:list1[0]],Yearly_Data[year][list1[-1]+1:]])
            U.append(p)
    return U


def seperateByYear(filteredData, outliers, range1, range2="02-08"): #Filtered Data should have no redundancies, gaps or outliars.
    
    start_date_str = filteredData["created_at"][0] #Gives first date
    print("start_date_str "+str(start_date_str))
    end_date_str = filteredData['created_at'].iloc[-1]
    print("end_date_str "+str(end_date_str))
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S %Z')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S %Z')
    delta = datetime.timedelta(minutes=inputData_dt) #Defines dt step size
    
    e_yrs = int(end_date_str[:4]) - int(start_date_str[:4]) + 1
    print("yrs of data = "+str(e_yrs))
    
    range_len = d_range2_date - d_range1_date
    
    A = [] #Stores a dataframe of each years data (in range)
    B = [] #Stores a dataframe of each years outliers (in range)
    C = [] #Stores the clipped index
    #D = [] #Stores a dataframe of all data
    #E = [] #Stores a dataframe of all outliers
    for e_year in range(e_yrs):
        print("seperating year "+str(e_year+int(start_date_str[:4])))
        
        """find first date index
        find last date index
        stack it 
        """
        
        s1 = str(int(start_date_str[:4])+e_year)+"-"+d_range1 +" 00:00:00 UTC"
        s2 = str(int(start_date_str[:4])+e_year)+"-"+d_range2 +" 23:30:00 UTC"
        
        try:
            s1_ = datetime.datetime.strptime(s1, '%Y-%m-%d %H:%M:%S %Z')
        except:
            print("error 1")
        try:
            s2_ = datetime.datetime.strptime(s2, '%Y-%m-%d %H:%M:%S %Z')
        except:
            print("error 1")
        
        def findClosest(e_year):
            print("first date of yr",end=" ")
            found = False
            j=0
            
            while found == False and j< d_range.days * DataPerDay:
                date = d_range1_date.replace(year = int(start_date.year)+e_year) + delta*j
                date_str = datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S %Z')
                date_str = date_str + "UTC"
                s1 = date_str
                #print(s1)
                try:
                    s1_ = filteredData.index[filteredData['created_at'] == s1].tolist()[0]
                    found = True
                    print("found : "+str(s1)+" j="+str(j))
                    C.append(j)
                    break
                except:
                    #print("tesing index "+str(s1))
                    dummy="dumb"
                j+=1
            
            return s1,found
        
        def findClosestBack(e_year):
            print("last date of yr ",end=" ")
            found = False
            change=False
            j=0
            
            while found == False and j< d_range.days * DataPerDay:
                date = d_range2_date.replace(year = int(start_date.year)+e_year) - delta*j
                date_str = datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S %Z')
                date_str = date_str + "UTC"
                s1 = date_str
                #print(s1)
                try:
                    s1_ = filteredData.index[filteredData['created_at'] == s1].tolist()[0]
                    found = True
                    print("found : "+str(s1)+" j="+str(j))
                    
                    if j > 0:
                        change=True
                    break
                except:
                    j+=1
            
            return s1,found,change

        if e_year >= 0:
            try:
                s1_i = filteredData.index[filteredData['created_at'] == findClosest(e_year)[0]].tolist()[0]
            except:
                print("Can't find an starting date in range. Skipped.")
            try:
                s2_i = filteredData.index[filteredData['created_at'] == findClosestBack(e_year)[0]].tolist()[0]

                Year_D = filteredData.iloc[s1_i:s2_i+1]
                A.append(Year_D)
                
                try:
                    Year_O = outliers.iloc[s1_i:s2_i+1]
                    B.append(Year_O)
                except Exception as exc:
                    print("fatal error appending to B (Yearly Outliers list)... e follows: ",exc)
                    print("Year_O = Year_D to prevent further errors.")
                    Year_O = Year_D
                    
                #print("Year_D"+str(Year_D.shape))
                #print("filteredData"+str(filteredData.shape))
            except Exception as e:
                print("EXCEPTION : "+str(e))
                #print("s2_i",filteredData.index[filteredData['created_at'] == findClosestBack(e_year)[0]].tolist()[0])
                #print("Can't find end date in range. Skipped. This might need to be changed to findClosetfromback() in the future")
    print("years of data = "+str(len(A)))
    return A,B,C,filteredData,outliers

def filterAndSeperateSensor(sensor_file,doSeperateByYear): #Load a single sensors Filtered Data. This needs to be run each time  
    def filterVars(Data_):
        print("filtering outliers...")
        Outliers_ = pd.DataFrame.copy(Data_)
        
        #Returns 2 dataframe similar to the original. One with outliers removed and one with outliers.
        [Data_['PM1.0_CF1_ug/m3'],Outliers_['PM1.0_CF1_ug/m3']] = hampel_filter_pandas(Data_['PM1.0_CF1_ug/m3'], ws, n_sig) 
        [Data_['PM2.5_CF1_ug/m3'],Outliers_['PM2.5_CF1_ug/m3']] = hampel_filter_pandas(Data_['PM2.5_CF1_ug/m3'], ws, n_sig) 
        [Data_['PM10.0_CF1_ug/m3'],Outliers_['PM10.0_CF1_ug/m3']] = hampel_filter_pandas(Data_['PM10.0_CF1_ug/m3'], ws, n_sig) 
        [Data_['Temperature_F'],Outliers_['Temperature_F']] = hampel_filter_pandas(Data_['Temperature_F'], ws, n_sig) 
        
        return [Data_,Outliers_]
    
    Data1 = pd.read_csv(master_path+primary_data_dir+"/"+sensor_file,index_col=0)#, index_col=0) #Create dataframe from file
    [Data2,Outliers] = filterVars(Data1) #Filter outliars
    print("Outliers filterAndSeperateSensor ",Outliers.shape)
    
    if doSeperateByYear == True:
        [Yearly_Data,Yearly_Outliers,index_skew,All_Data,All_Outliers] = seperateByYear(Data2,Outliers,d_range1,d_range2) #Seperate by Year
    else:
        [Yearly_Data,Yearly_Outliers,index_skew,All_Data,All_Outliers] = [Data2,Outliers,0,Data2,Outliers]

    return[Yearly_Data,Yearly_Outliers,index_skew,All_Data,All_Outliers]


def readSensor(Sensor_,doSeperateByYear=True): 
    sensorName_ = Sensor_[0]
    fullFileName_ = Sensor_[1]
    parsedFileName = sensorName_+"_parsed.csv" #This is the original data with gaps filled and duplicates removed
    #SensorData = []
    if os.path.exists(master_path+primary_data_dir+"/"+str(sensorName_)+"_Non_Outliers_clean.csv"):
        path1 = master_path+primary_data_dir+"/"+str(sensorName_)+"_Non_Outliers_clean.csv"
        path2 = master_path+primary_data_dir+"/"+str(sensorName_)+"_Outliers_clean.csv"
        
        [Non_Out,Out] = [pd.read_csv(path1,index_col=0),pd.read_csv(path2,index_col=0)]
        if doSeperateByYear == True:
            [Yearly_Data,Yearly_Outliers,index_skew, All_data, All_Outliers] = seperateByYear(Non_Out,Out,d_range1,d_range2)
            if len(Yearly_Outliers) == 0:
                SensorYearly_df = pd.DataFrame({'Non_Outliers':Yearly_Data})
            else:
                SensorYearly_df = pd.DataFrame({'Non_Outliers':Yearly_Data,'Outliers':Yearly_Outliers})
        else:
            SensorYearly_df = [Non_Out,Out]
    else:
        if parsedFileName not in list_of_dir: #False #if Dupe and Gaps haven't been filtered+saved then do so.
            print("Parsing file for the first time.")
            Data = pd.read_csv(master_path+primary_data_dir+"/"+fullFileName_)    
            removeGapsAndDupes(Data,sensorName_) #Read raw data and SAVES w/o dupes and gaps
            SensorYearly_df = None #to avoid an error. Delete me later.
        if parsedFileName in list_of_dir: #True #if gaps and dupes taken out load the file and remove outliars.
            print("Loading Parsed File")  
            [Yearly_Data,Yearly_Outliers,index_skew, All_data, All_Outliers] = filterAndSeperateSensor(parsedFileName,doSeperateByYear) #Read file + Remove outliers
            
            Yearly_Data = removeLeapDays(Yearly_Data)
            Yearly_Outliers = removeLeapDays(Yearly_Outliers)
            
            #print("Yearly_Data 2shape = ",len(Yearly_Data))
            #print("Yearly_Outliers 2shape = ",len(Yearly_Outliers))
            
            print("type!",type(Yearly_Data))
            print("Yearly_Data[0].shape ",Yearly_Data[0].shape)
            #SensorData = [Yearly_Data,Yearly_Outliers,index_skew]
            #SensorData.append([Yearly_Data,Yearly_Outliers,index_skew]) 
            
            #SensorData format is currently nested list of dfs. SensorData[[Non_outlier,outlier,skew],year].
            #Convert to a nested dataframe.
            SensorYearly_df = pd.DataFrame({'Non_Outliers':Yearly_Data,'Outliers':Yearly_Outliers})
            
            #os.mkdir(master_path+"/PurpleAirData/"+sensorName_+"_clean")
            for n,out_or_non in enumerate(["Non_Outliers","Outliers"]):
                fileN = str(sensorName_)+"_"+str(out_or_non)+"_clean.csv"
                All_data.to_csv(master_path+primary_data_dir+"/"+fileN)
            
            """
            for n,out_or_non in enumerate(["Non_Outlier_","Outlier_"]):
                for year in range(len(SensorYearly_df)):
                    fileN = str(str(out_or_non)+str(year)+".csv")
                    SensorYearly_df.iloc[year,n][0:].to_csv(master_path+"/PurpleAirData/"+str(sensorName_)+"_clean/"+fileN)
            """
            print("saved SensorYearly_df "+str(s))
    
    return SensorYearly_df #SensorData

def readSensors(Sensors,doSeperateByYear):
    Sensors_list = []
    for s in range(len(Sensors)):
        Sensors_list.append(readSensor(Sensors[s],doSeperateByYear))
    return Sensors_list