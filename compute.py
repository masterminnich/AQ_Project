#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 21:03:16 2020

Computational stuff for the Nested Dataframe Structure
"""

import pandas as pd
import numpy as np
import math
import os
import datetime
import matplotlib.pyplot as plt2
import better_file_reading

#Sensors = [["Echo Park P1","Echo Park P1 (undefined) (34.073635 -118.268681) Primary 30_minute_average 01_01_2017 05_07_2020.csv"],["CCA Pepper","CCA Pepper (outside) (34.089558 -118.226068) Primary 30_minute_average 01_01_2017 05_07_2020.csv"]]
#SensorYearly_dfs = better_file_reading.readSensors([["Echo Park P1","Echo Park P1 (undefined) (34.073635 -118.268681) Primary 30_minute_average 01_01_2017 05_07_2020.csv"],["CCA Pepper","CCA Pepper (outside) (34.089558 -118.226068) Primary 30_minute_average 01_01_2017 05_07_2020.csv"],["CCA Pepper","CCA Pepper (outside) (34.089558 -118.226068) Primary 30_minute_average 01_01_2017 05_07_2020.csv"]],True)
col_names = ['created_at','PM1.0_CF1_ug/m3','PM2.5_CF1_ug/m3','PM10.0_CF1_ug/m3','UptimeMinutes','RSSI_dbm','Temperature_F','Humidity_%','PM2.5_ATM_ug/m3','Unnamed: 9'] #

def findYearlyDevFrom2020(SensorYearly_df):
    list_of_yr_diffs = []
    first_date_got_trimmed = False
    for y in range(SensorYearly_df.shape[0]-1):
        trimmed = False
        y2020 = SensorYearly_df.iloc[-1,0]
        y_i = SensorYearly_df.iloc[y,0]
        
        #Is 2020 range the same as y_i? If not. trim y_i
        y_i_trim  = y_i[:int(y2020.shape[0])]
        
        if y_i_trim.shape[0] < y2020.shape[0]: #y_i smaller than y2020. add nans to y_i
            y_i_frst_d = y_i_trim.iloc[0,0][5:]
            y_i_frst_dt = datetime.datetime.strptime(y_i_frst_d, '%m-%d %H:%M:%S %Z')
            y_i_lst_d = y_i_trim.iloc[-1,0][5:]
            y_i_lst_dt = datetime.datetime.strptime(y_i_lst_d, '%m-%d %H:%M:%S %Z')
            y_2020_frst_d = y2020.iloc[0,0][5:]
            y_2020_frst_dt = datetime.datetime.strptime(y_2020_frst_d, '%m-%d %H:%M:%S %Z')
            y_2020_lst_d = y2020.iloc[-1,0][5:]
            y_2020_lst_dt = datetime.datetime.strptime(y_2020_lst_d, '%m-%d %H:%M:%S %Z')
            
            if y_i_frst_dt > y_2020_lst_dt: #Y_i_first_date older than last date in y_2020
                print("out of range",y)
                first_date_got_trimmed = True
                trimmed = True
            else:
                print("y_i_trim",y_i_trim.shape,'y2020',y2020.shape)
                print("resize")
                [DF_l,yy,oo] = resizeDFs([y_i_trim,y2020])
                [y_i_trim,y2020] = DF_l
                print("y_i_trim",y_i_trim.shape,'y2020',y2020.shape)
        
        if trimmed == False:
        
            print("y2020 shape"+str(y2020.shape))
            print("y_i shape"+str(y_i.shape))
            print("y_i_trim shape"+str(y_i_trim.shape))
            
            PM1_diff = pd.DataFrame.to_numpy(y2020['PM1.0_CF1_ug/m3'])-pd.DataFrame.to_numpy(y_i_trim['PM1.0_CF1_ug/m3'])
            
            PM25_diff = pd.DataFrame.to_numpy(y2020['PM2.5_CF1_ug/m3'])-pd.DataFrame.to_numpy(y_i_trim['PM1.0_CF1_ug/m3'])
            PM10_diff = pd.DataFrame.to_numpy(y2020['PM10.0_CF1_ug/m3'])-pd.DataFrame.to_numpy(y_i_trim['PM1.0_CF1_ug/m3'])
            Temp_diff = pd.DataFrame.to_numpy(y2020['Temperature_F'])-pd.DataFrame.to_numpy(y_i_trim['Temperature_F'])
    
            #Construct a new dataframe and insert the diffs.
            y_i_trim_invs = pd.DataFrame.to_numpy(y_i[int(y2020.shape[0]):])
            y_i_PM1_diff = np.append(PM1_diff,y_i_trim_invs[:,1])
            y_i['PM1.0_CF1_ug/m3'] = y_i_PM1_diff
            
            y_i_PM25_diff = np.append(PM25_diff,y_i_trim_invs[:,2])
            y_i['PM2.5_CF1_ug/m3'] = y_i_PM25_diff
            
            y_i_PM10_diff = np.append(PM10_diff,y_i_trim_invs[:,2+1])
            y_i['PM10.0_CF1_ug/m3'] = y_i_PM10_diff
            
            y_i_Temp_diff = np.append(Temp_diff,y_i_trim_invs[:,6])
            y_i['Temperature_F'] = y_i_Temp_diff
            
            #Trim the dataframe for dates with no deviation (because 2020 data not found)
            y_i = y_i.truncate(after=int(y_i.iloc[0].name) + (y_i_trim.shape[0]))
        
            list_of_yr_diffs.append(y_i)
     
    if first_date_got_trimmed == False:    
        SensorYearly_df = pd.DataFrame({"Non_Outliers":list_of_yr_diffs,"Outliers":SensorYearly_df.iloc[:-1,0]})
    else: 
        SensorYearly_df = pd.DataFrame({"Non_Outliers":list_of_yr_diffs,"Outliers":SensorYearly_df.iloc[1:-1,0]})

    return SensorYearly_df

def findYearlyDevsFrom2020(SensorYearly_dfs):
    B = []
    for SensorYearly_df in SensorYearly_dfs:
        A = findYearlyDevFrom2020(SensorYearly_df)
        B.append(A)
    return B


def resizeDFs(DF_list):  #Takes a list of clean Dataframes (DOES NOT WORK FOR YEARLY DFs) and returns back DFs with the same shape (filled w/ np.nan)
    def findOldestAndYoungestDateInDFList(DF_list):
        oldest_date = None  #Saves furthest date from the current date
        youngest_date = None  #Saves fclosest date from the current date
        for df in DF_list:
            o_l = df['created_at'].iloc[0]
            y_l = df['created_at'].iloc[-1]
            print(o_l,y_l)
            if pd.isna(o_l):
                i = 0
                while pd.isna(o_l):
                    o_l = df['created_at'].iloc[i]
                    i += 1
                print("not this one")
                
            o_date = datetime.datetime.strptime(o_l, '%Y-%m-%d %H:%M:%S %Z') #Oldest date in single DF in datetime format
            y_date = datetime.datetime.strptime(y_l, '%Y-%m-%d %H:%M:%S %Z') #Youngest date in single DF in datetime format
            
            if oldest_date == None: #If first DF, save oldest and youngest date for comparison
                oldest_date = o_date
                youngest_date = y_date
            else: #If not first
                if oldest_date > o_date: #if oldest_date younger than o_date, Save o_date
                    oldest_date = o_date
                if youngest_date < y_date: #if youngest_date older than y_date, Save y_date
                    youngest_date = y_date
         
        return [oldest_date,youngest_date]
    
    [oldest_date,youngest_date] = findOldestAndYoungestDateInDFList(DF_list)
    print("oldest,youngest : ",oldest_date,youngest_date)
    
    most_dps = 0 #Stores the amount of datapoints of the largest DF in the list
    most_dp_index = 0
    for ii,df in enumerate(DF_list):
        dps = DF_list[ii].shape[0]
        if dps > most_dps:
            most_dps = dps
            most_dp_index = ii
    
    for ii,df in enumerate(DF_list):
        dps = DF_list[ii].shape[0]
        if dps < most_dps:
            diff_dps = most_dps - dps
            
            df_n = pd.DataFrame.to_numpy(df)
            
            for d in range(diff_dps):
                date_str = DF_list[most_dp_index]['created_at'].iloc[0]
                row = [date_str,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
                df_n = np.vstack((row,df_n))
            
            df2 = pd.DataFrame(df_n, columns = df.columns)
            DF_list[ii] = df2
    
    """
    RETIRED. This used to subtract the current oldest date from the oldest date and add np rows for each datapoint. This failed for some data because if we are only looking at a specific date range, extra nan rows will be added
    
    for ii,df in enumerate(DF_list):
        print("ii = ",ii)
        o_l = df['created_at'].iloc[0]
        print('o_l',o_l)
        y_l = df['created_at'].iloc[-1]
        o_date = datetime.datetime.strptime(o_l, '%Y-%m-%d %H:%M:%S %Z') #Oldest date in single DF in datetime format
        y_date = datetime.datetime.strptime(y_l, '%Y-%m-%d %H:%M:%S %Z') #Youngest date in single DF in datetime format
        row = [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
        
        if o_date > oldest_date: #If oldest date in dataframe is younger than "oldest_date", add nans to fit the shape.
            print("o_date = ",o_date,"  oldest_date = ",oldest_date)
            df_n = pd.DataFrame.to_numpy(df)
            o_diff = o_date - oldest_date#How many days do we need to add np.nans for?
            o_diff_days = o_diff.days + o_diff.seconds / 86400 #86400 seconds/day
            print("o days",o_diff_days)
            o_diff_ind = int((o_diff_days-1)*(24*60/30))  #1800 = Thirty mins to seconds. This should be input_dt
            print("o_diff : ",o_date - oldest_date,'o_diff_ind',o_diff_ind)
            for i in range(o_diff_ind):
                df_n = np.vstack((row,df_n))
            df2 = pd.DataFrame(df_n, columns = df.columns)
            DF_list[ii] = df2
        if o_date < oldest_date:
            print("DF has values older than var \" oldest_date \" ")
            
        if y_date < youngest_date: #If youngest date in dataframe is older than "youngest_date", add nans to fit the shape.
            df_n2 = pd.DataFrame.to_numpy(df)
            y_diff = abs(youngest_date - y_date)#How many days do we need to add np.nans for?
            y_diff_days = y_diff.days + math.floor(y_diff.seconds / 86400) #86400 seconds/day
            print("y days",y_diff_days)
            y_diff_ind = int((y_diff_days-1)*(24*60/30))  #1800 = Thirty mins to seconds. This should be input_dt
            print("y_dff : ",abs(youngest_date - y_date),'y_diff_ind',y_diff_ind)
            for i in range(y_diff_ind):
                df_n2 = np.vstack((row,df_n2))
            df2_ = pd.DataFrame(df_n2, columns = df.columns)
            DF_list[ii] = df2_
        if y_date > youngest_date:
            print("DF has values younger than var \" youngest_date \" ")
    """
    
    return [DF_list,oldest_date,youngest_date]


def unseperateYearly(SensorYearly_df, yrs=777):
    if yrs == 777: #This activates if you are only unseperating one sensor's Dataframe
        yrs = SensorYearly_df['Non_Outliers'].shape[0]
    c_yrs = SensorYearly_df['Non_Outliers'].shape[0]
        
    diff_in_yrs = yrs - c_yrs #Gives the amount of years difference between the largest df and the current df
    print("diff_in_yrs = ",diff_in_yrs)
    
    for y in range(c_yrs):
        if y == 0:
            np_y = pd.DataFrame.to_numpy(SensorYearly_df['Non_Outliers'].iloc[0])
        else:
            np_y = np.vstack((np_y, pd.DataFrame.to_numpy(SensorYearly_df['Non_Outliers'].iloc[y])))
    df = pd.DataFrame(np_y,columns=col_names)
        
    return df
    
def unseperateYearly_dfs(SensorYearly_dfs):
    A = []
    
    #Find largest year size
    max_yrs = 0
    for i in range(len(SensorYearly_dfs)):
        y = SensorYearly_dfs[i].shape[0]
        if y > max_yrs:
            max_yrs = y
    
    for df in SensorYearly_dfs:
        A.append(unseperateYearly(df,max_yrs))
    return A,max_yrs
    

def AvgAllSensors(SensorYearly_dfs, delta = datetime.timedelta(minutes=30)): #Averages yearly data across all sensors 
    youngest_date_str_2020 = SensorYearly_dfs[0]['Non_Outliers'].iloc[-1]['created_at'].iloc[-1]
    oldest_date_str_2020 = SensorYearly_dfs[0]['Non_Outliers'].iloc[-1]['created_at'].iloc[0]    
    datetime.datetime.strptime(youngest_date_str_2020, '%Y-%m-%d %H:%M:%S %Z')


    for i,sensor in enumerate(SensorYearly_dfs):
        youngest_date_str = sensor['Non_Outliers'].iloc[-1]['created_at'].iloc[-1]
        oldest_date_str = sensor['Non_Outliers'].iloc[-1]['created_at'].iloc[0]

    [pl2,max_yrs] = unseperateYearly_dfs(SensorYearly_dfs)    #Non_Outliers

    """
    pl = [p1,p2] = better_file_reading.readSensors(Sensors,False) #List of Sensors w shape [Non_outliers, Outliers]
    pl2 = [] #List of Sensors (just Non_outliers).
    for p in pl:
        pl2.append(p[0]) #Non_outliers
    """

    [DF_list,oldest_date,youngest_date] = resizeDFs(pl2) #DF_list is now a list of sensor DFs with identical shape.
    
    #oldest_date = datetime.datetime.strptime(SensorYearly_dfs[1].iloc[-2]['Non_Outliers']['created_at'].iloc[-1], '%Y-%m-%d %H:%M:%S %Z')
    #youngest_date = datetime.datetime.strptime(SensorYearly_dfs[1].iloc[0]['Non_Outliers']['created_at'].iloc[-1], '%Y-%m-%d %H:%M:%S %Z')
        
    datapoints = DF_list[0]['PM1.0_CF1_ug/m3'].shape[0]
    pm1_tot = np.zeros(datapoints)
    pm25_tot = np.zeros(datapoints)
    pm10_tot = np.zeros(datapoints)
    temp_tot = np.zeros(datapoints)
    print("tot shape "+str(temp_tot.shape))
    bool_tot = np.zeros(datapoints) #Stores the number of (non-NaN) datapoints for each time.
    
    for df in DF_list:
        pm1 = pd.DataFrame.to_numpy(df['PM1.0_CF1_ug/m3'])
        pm25 = pd.DataFrame.to_numpy(df['PM2.5_CF1_ug/m3'])
        pm10 = pd.DataFrame.to_numpy(df['PM10.0_CF1_ug/m3'])
        temp = pd.DataFrame.to_numpy(df['Temperature_F'])
        
        bool_arr = [] #Boolean Array (using 1s and 0s). Allows us to add multiple together to know how many values we have for each time.
        for d in np.isnan(pm1.astype(np.float)):
            if d == True:
                bool_arr.append(0)
            if d == False:
                bool_arr.append(1) #1 == True. Has a value other than NaN
                
        pm1_tot = np.nan_to_num(pm1.astype(np.float)) + pm1_tot.astype(np.float)
        pm25_tot = np.nan_to_num(pm25.astype(np.float)) + pm25_tot.astype(np.float)
        pm10_tot = np.nan_to_num(pm10.astype(np.float)) + pm10_tot.astype(np.float)
        temp_tot = np.nan_to_num(temp.astype(np.float)) + temp_tot.astype(np.float)
        bool_tot = bool_arr + bool_tot

    pm1_avg = np.zeros(datapoints)
    pm25_avg = np.zeros(datapoints)
    pm10_avg = np.zeros(datapoints)
    temp_avg = np.zeros(datapoints)
    print("avg1 shape "+str(temp_avg.shape))
    for time in range(datapoints):
        if bool_tot[time] != 0:
            pm1_avg[time] = pm1_tot[time] / bool_tot[time]
            pm25_avg[time] = pm25_tot[time] / bool_tot[time]
            pm10_avg[time] = pm10_tot[time] / bool_tot[time]
            temp_avg[time] = temp_tot[time] / bool_tot[time]
        if bool_tot[time] == 0:
            pm1_avg[time] = np.nan
            pm25_avg[time] = np.nan
            pm10_avg[time] = np.nan
            temp_avg[time] = np.nan
            
    #d_list = better_file_reading.getDateList(oldest_date,youngest_date)
    if True:
        d_list = better_file_reading.getYearlyDateList(2017,oldest_date_str_2020,youngest_date_str_2020,max_yrs)
    
    NaN_col = []
    for i in range(pm1_avg.shape[0]):
        NaN_col.append(np.nan) #Fill a list with np.nans for each datapoint
    print("len(d_list)",len(d_list))
    print("len(Nan_col) = ",len(NaN_col))
    print("len(pm1_avg.tolist()) = ",len(pm1_avg.tolist()))
    print("pm25_avg.shape = ",pm25_avg.shape)
    print("temp_avg.shape = ",temp_avg.shape)
    
    #Create a new dataframe with the avg values. 
    #avg_df_just_data = pd.DataFrame({'created_at':d_list,'PM1.0_CF1_ug/m3':pm1_avg,'PM2.5_CF1_ug/m3':pm25_avg,'PM10.0_CF1_ug/m3':pm10_avg,'Temperature_F':temp_avg})
    New_avg_df = pd.DataFrame({'created_at':d_list,'PM1.0_CF1_ug/m3':pm1_avg,'PM2.5_CF1_ug/m3':pm25_avg,'PM10.0_CF1_ug/m3':pm10_avg,'UptimeMinutes':NaN_col,'RSSI_dbm':NaN_col,'Temperature_F':temp_avg,'Humidity_%':NaN_col,'PM2.5_ATM_ug/m3':NaN_col,'PM2.5_ATM_ug/m3':NaN_col})
    
    return New_avg_df,bool_tot
    
"""
Retired.

def getAvgYearlyDevDF(Sensors_): 
    #Plot the avg of the Yearly Devs From 2020 for all sensors.
    B = []
    for i in Sensors_:
        SensorYearly_df = better_file_reading.readSensor(i,True)
        A = findYearlyDevFrom2020(SensorYearly_df)
        B.append(A)
        
    #B = findYearlyDevsFrom2020(Sensors_)
    
    AVG_DF,bool_tot = AvgAllSensors(B)
    
    AVG_DF_seperated = better_file_reading.seperateByYear(AVG_DF, None, AVG_DF.iloc[0,0][5:10], AVG_DF.iloc[-1,0][5:10])
    
    #The following should really be in seperateByYear()
    for iii in range(len(AVG_DF_seperated[0])):
        print(iii)
        if iii == 0:
            v = np.array((AVG_DF_seperated[0][0]))
        else:
            v = np.dstack((v,AVG_DF_seperated[0][iii]))
    #v = np.reshape(v,(v.shape[2], v.shape[0], v.shape[1]))
    np_list = np.split(v,v.shape[2],axis=2)
    v_aslist = []
    for vv in range(v.shape[2]): 
        np_list_yr = np.reshape(np_list[vv], (np_list[0].shape[0],np_list[0].shape[1]))
        p = pd.DataFrame(np_list_yr,columns=col_names[:9])
        v_aslist.append(p)
    AVGDF = pd.DataFrame({"Non-Outliers":v_aslist,"Outliers":v_aslist})  #NOTE THAT OUTLIERS ARE FAULTY AND ARE LOST, outliers are repeated to satisfy SensorYearly_df format of Series of DataFrams

    return AVGDF
"""

def MovingAvg(y, movingAvgLength): #Takes a 1-D numpy array and returns the MA.
    MA_mask = []
    MA = []
    for d in range(y.shape[0]):
        d = d+1
        if d < movingAvgLength:
            MA.append(np.nan)
            MA_mask.append(False)
        if d >= movingAvgLength:
            window_vals = y[d-movingAvgLength:d] #Contains the data for everyday of the moving avg
            window_vals = window_vals.astype(float)
            
            #If at least 85% of the last (MovingAvgLength) days have an average calculate the moving avg
            isNan = np.isnan(window_vals)
            n_NaNs = np.sum(isNan)
            if n_NaNs <= .15*movingAvgLength:
                summ = np.nansum(window_vals)
                MA.append(summ / movingAvgLength)
                MA_mask.append(True)
            else:
                MA.append(np.nan)
                MA_mask.append(False)
                
    MA = np.array(MA) 
    MA_mask = np.array(MA_mask)             
    
    return MA,MA_mask


def MovingAvgDF(df, movingAvgLength): #Takes the MovingAvg of a single df
    PM1 = pd.DataFrame.to_numpy(df['PM1.0_CF1_ug/m3'])
    PM25 = pd.DataFrame.to_numpy(df['PM2.5_CF1_ug/m3'])
    PM10 = pd.DataFrame.to_numpy(df['PM10.0_CF1_ug/m3'])
    Temp = pd.DataFrame.to_numpy(df['Temperature_F'])
    
    [PM1_ma,PM1_ma_mask] = MovingAvg(PM1, movingAvgLength)
    [PM25_ma,PM25_ma_mask] = MovingAvg(PM25, movingAvgLength)
    [PM10_ma,PM10_ma_mask] = MovingAvg(PM10, movingAvgLength)
    [Temp_ma,Temp_ma_mask] = MovingAvg(Temp, movingAvgLength)
    
    df['PM1.0_CF1_ug/m3'] = PM1_ma
    df['PM2.5_CF1_ug/m3'] = PM25_ma
    df['PM10.0_CF1_ug/m3'] = PM10_ma
    df['Temperature_F'] = Temp_ma
    
    return df
    

def YearlyMovingAvg(SensorYearly_df, movingAvgLength): #Takes YearlyDF with shape [yrs,2] The 2 represents Non_Outliers and Outliers
    YearlyMA_DF = []
    for y in range(SensorYearly_df.shape[0]):
        df = SensorYearly_df.iloc[y]['Non_Outliers']
        df_ma = MovingAvgDF(df, movingAvgLength)
        YearlyMA_DF.append(df_ma)
    
    return YearlyMA_DF


def getAvgYearlyDevDF(Sensors, doDeviation=True):
    
    def readSensors(Sensors):
        Sensors_Data = []
        for i in Sensors:
            SensorYearly_df = better_file_reading.readSensor(i,True)
            Sensors_Data.append(SensorYearly_df)
        return Sensors_Data
    
    
    def ComputeMA(Sensors_Data):
        New_Sensors_Data = []
        for j in range(len(Sensors_Data)):
            a = YearlyMovingAvg(Sensors_Data[j], 1440)
            b = pd.DataFrame(a,columns=['Non_Outliers'])
            New_Sensors_Data.append(b)
            
        return New_Sensors_Data
        
    
    def TakeDev(Sensors_Data):
        New_Sensors_Data = []
        for k in range(len(Sensors_Data)):
            New_Sensors_Data.append(findYearlyDevFrom2020(Sensors_Data[k]))
        return New_Sensors_Data
        
    
    def unseperateYearlyDFS(Yearly_DFS):
        C = []
        for s in range(len(Yearly_DFS)): #For every sensor
            seperate_df = Yearly_DFS[s]['Non_Outliers']
            
            print("#of yrs = ", len(seperate_df))
            print("Current Sensor: ",Sensors[s][0])
            
            for yr in range(len(seperate_df)): #Stack each year of a single sensor
                yr_np = pd.DataFrame.to_numpy(seperate_df.iloc[yr]) #Single year of a single sensor in np form
                if yr == 0:
                    DF = yr_np
                else:
                    DF = np.vstack((DF,yr_np))
            C.append(DF)
        return C
    
    """After the DFs are unseperated into a list of continuous np arrays we need to add nan values to the front of the array to make them all the same shape."""
    def FindLargestDFsize(C):
        most_dps = 0
        most_dps_index = None
        for i,df in enumerate(C):
            dps = df.shape[0]
            if i == 0 or dps > most_dps:
                most_dps = dps
                most_dps_index = i
        return [most_dps, most_dps_index]
    
    def ResizeByAddingNaNs(C, most_dps, most_dps_index): #This works because we assume the last datapoint is the same for each sensor and files have already been parsed for missing/duplicate data
        for d,df in enumerate(C):
            if df.shape[0] < most_dps:
                NaNsToAdd = most_dps - df.shape[0]
                for n in range(NaNsToAdd):
                    #Find the name of this date
                    date = C[most_dps_index][n,0] #Finds the name of this datapoint by reading the file w most dps
                    row = [date, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                    row = np.array(row)
                    #print("insert row of NaNs at position "+str(n))
                    df = np.insert(df,n,row,0)
            C[d] = df
        return C
    
    def AvgDFList(D):
        def MakeBoolArray(col): #Find number of valid datapoints for each time
            binary_col_tot = np.zeros(D[0].shape[0])
            for s in range(len(D)):
                col_nan = np.isnan(D[s][:,col].astype(np.float))
                col_nan = np.invert(col_nan)
                col_nan_binary = col_nan.astype(int) #If data replace with a 1, if NaN replace with 0
                binary_col_tot += col_nan_binary
                
            return binary_col_tot
        
        PM1_bool = MakeBoolArray(1) #Find number of valid datapoints for each time for PM1 
        PM25_bool = MakeBoolArray(2) #Find number of valid datapoints for each time for PM2.5
        PM10_bool = MakeBoolArray(3) #Find number of valid datapoints for each time for PM10 
        Temp_bool = MakeBoolArray(6) #Find number of valid datapoints for each time for Temp
    
        """Now I need to add along rows, then divide by PM1_bool"""
        def AddArrays(col): #Adds up all similar datapoints across all sensors
            binary_col_tot = np.zeros(D[0].shape[0])
            for s in range(len(D)):
                col_float = np.nan_to_num(D[s][:,col].astype(np.float))
                binary_col_tot += col_float
                
            return binary_col_tot
                
        PM1_tot = AddArrays(1)
        PM25_tot = AddArrays(2)
        PM10_tot = AddArrays(3)
        Temp_tot = AddArrays(6)
        
        def FindAvgs(tot_arr, bool_arr):
            avg_arr = tot_arr
            for e in range(tot_arr.shape[0]):
                if bool_arr[e] != 0:
                    avg_dp = tot_arr[e] / bool_arr[e]
                    avg_arr[e] = avg_dp
                    
            return avg_arr
        
        PM1_avg = FindAvgs(PM1_tot, PM1_bool)
        PM25_avg = FindAvgs(PM25_tot, PM25_bool)
        PM10_avg = FindAvgs(PM10_tot, PM10_bool)
        Temp_avg = FindAvgs(Temp_tot, Temp_bool)
        
        return [PM1_avg,PM25_avg,PM10_avg,Temp_avg]
    
    def reconstructDF(D, most_dps_index, PM1_avg, PM25_avg, PM10_avg, Temp_avg):
        dates = D[most_dps_index][:,0].tolist()
        pm1_avg = PM1_avg.tolist()
        pm25_avg = PM25_avg.tolist()
        pm10_avg = PM10_avg.tolist()
        temp_avg = Temp_avg.tolist()
        
        NaN_col=[]
        for i in range(D[0].shape[0]):
            NaN_col.append(np.nan) #Fill a list with np.nans for each datapoint
        
        New_avg_df = pd.DataFrame({'created_at':dates,'PM1.0_CF1_ug/m3':pm1_avg,'PM2.5_CF1_ug/m3':pm25_avg,'PM10.0_CF1_ug/m3':pm10_avg,'UptimeMinutes':NaN_col,'RSSI_dbm':NaN_col,'Temperature_F':temp_avg,'Humidity_%':NaN_col,'PM2.5_ATM_ug/m3':NaN_col,'PM2.5_ATM_ug/m3':NaN_col})
        
        return New_avg_df
    
    B = Sensors_Data = readSensors(Sensors)
    #Sensors_Data = ComputeMA(Sensors_Data)
    #B = TakeDev(Sensors_Data)
    C = unseperateYearlyDFS(B)
    [most_dps, most_dps_index] = FindLargestDFsize(C) 
    D = ResizeByAddingNaNs(C, most_dps, most_dps_index)
    [PM1_avg,PM25_avg,PM10_avg,Temp_avg] = AvgDFList(D)
    AVGDF = reconstructDF(D, most_dps_index, PM1_avg, PM25_avg, PM10_avg, Temp_avg)
    
    return AVGDF










#A = findYearlyDevsFrom2020(SensorYearly_dfs)
#AVG_DF = AvgAllSensors(A)

"""Plot AVG Yearly"""
#AVG_DF_seperated = better_file_reading.seperateByYear(AVG_DF, None, AVG_DF.iloc[0,0][5:10], AVG_DF.iloc[-1,0][5:10])


