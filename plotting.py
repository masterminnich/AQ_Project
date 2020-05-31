#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 20:58:12 2020

@author: josephminnich
"""
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt2
import better_file_reading
#import compute
import math
#from hampel_filter_pandas import hampel_filter_pandas


#SensorYearly_df = better_file_reading.readSensor(["Echo Park P1","Echo Park P1 (undefined) (34.073635 -118.268681) Primary 30_minute_average 01_01_2017 05_07_2020.csv"],True)
#SensorYearly_df = better_file_reading.readSensor(["CCA Pepper","CCA Pepper (outside) (34.089558 -118.226068) Primary 30_minute_average 01_01_2017 05_07_2020.csv"],True)

[d_range1,d_range2,d_range_days,DataPerDay] = better_file_reading.get_date_ranges()
col_names = ['created_at','PM1.0_CF1_ug/m3','PM2.5_CF1_ug/m3','PM10.0_CF1_ug/m3','UptimeMinutes','RSSI_dbm','Temperature_F','Humidity_%','PM2.5_ATM_ug/m3']

#Plot yearly plots
def yearlyPlot(SensorYearly_df, sensorname, data_type='PM1.0_CF1_ug/m3'):
    
    def genXticks(x,dp_range,ticks): #x = array of datapoints by year, ticks = desired num of xtick labels
        
        def get_date_range(d1,d2,d_len):
            start = datetime.datetime.strptime(d1, '%m-%d')
            end = datetime.datetime.strptime(d2, '%m-%d')
            step = datetime.timedelta(days=d_len)
            date_range = []
            while start <= end:
                d1 = str(start.date())
                d = d1.replace("-", "/")
                d = d[5:] #Drop the year because it is arbitrary for the yearlyPlot
                date_range.append(d)
                start += step
            return date_range
    
        tick_len = math.floor(x.shape[0]/ticks)
        tick_len2 = x.shape[0]/ticks
        tick_inds = []
        """
        if int(x.shape[0])%ticks == 0: #If datapoints dividisble by ticks
            #ticks +=1
            print("xticks1")
        else: #Gets rounded
            #ticks -= 1
            print("xticks2")
        """
        for j in range(ticks):
            # Find Indicies
            ind = j*tick_len2
            #print(ind)
            tick_inds.append(ind/DataPerDay)
        
        num_days = dp_range.days+math.ceil(dp_range.seconds/86400) #num of days in the range rounded up
        day_len = num_days/(ticks) #how many days does each tick represent
        tick_names = get_date_range(d_range1,d_range2,day_len)
            
        #print(tick_inds)
        #print(tick_names)
            
        return tick_inds,tick_names,day_len
        
    fig, ax = plt2.subplots()
    fig.set_size_inches(7,5)
    
    first_date = SensorYearly_df.iloc[0][0]['created_at'].iloc[0]
    last_date = SensorYearly_df.iloc[0][0]['created_at'].iloc[-1]
    dp_range = datetime.datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S %Z') - datetime.datetime.strptime(first_date, '%Y-%m-%d %H:%M:%S %Z')
    
    for year in range(len(SensorYearly_df.iloc[:])):
        first_date = SensorYearly_df.iloc[year][0]['created_at'].iloc[0]
        last_date = SensorYearly_df.iloc[year][0]['created_at'].iloc[-1]
        dp_range1 = datetime.datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S %Z') - datetime.datetime.strptime(first_date, '%Y-%m-%d %H:%M:%S %Z')
        
        dp_range1 = (dp_range1.days+math.ceil(dp_range1.seconds/86400)) #Rounds up days in range (yearly)
        print("dp_range1="+str(dp_range1))
        
        year_f = SensorYearly_df.iloc[year][0]['created_at'].iloc[0][:4]
        print(year_f)
        data_points = SensorYearly_df.iloc[year][0].shape[0]
        data_points2 = d_range_days*DataPerDay
        #start_day = SensorData[2][0]/48 #If first year doesn't read the entire range
        days = SensorYearly_df.iloc[year][0].shape[0]/DataPerDay # - 1) + (SensorData[0][-1][/48)
        print("days="+str(days))
        
        """
        #if last datapoint of the year doesn't match the range
        if d_range2_date>datetime.datetime.strptime(SensorYearly_df.iloc[year][0]['created_at'].iloc[-1][5:10], '%m-%d'):
            dp = len(SensorYearly_df.iloc[year][0]['created_at'])
            x = np.linspace(dp/48, int(d_range_days), int(data_points2))"""
        
        x = np.linspace(0, int(d_range_days), int(data_points2)) #SensorData[2][year]/48
        print("len(x) = "+str(len(x)))
        [tick_inds,tick_names,day_len] = genXticks(x,dp_range,10)
        if year_f == "2020": #Make 2020 Thicker
            if int(days) != d_range_days:
                for i in range(int(int(d_range_days-days)*DataPerDay)):
                    if i == 0:
                        blank = pd.DataFrame([np.nan])
                        a = pd.concat([SensorYearly_df.iloc[year][0][data_type],blank[0]])
                    else:
                        a = pd.concat([a,blank[0]])
            else:
            	a = SensorYearly_df.iloc[year][0][data_type]
            	if x.shape[0] < a.shape[0]:
            		x = np.linspace(0, int(d_range_days), int(data_points2))
            		print("data_points2 (x = np.linespace) is 1 value to small. Modify line 86 in plotting.py")
            	print("full year")
            ax.plot(x, a, label=sensorname+" "+str(year_f), linewidth=1.8)
        else:
            x = np.linspace(0, int(d_range_days), int(data_points)) #SensorData[2][year]/48
            ax.plot(x, SensorYearly_df.iloc[year][0][data_type], label=sensorname+" "+str(year_f), linewidth=1.2)
            
    print(x.shape)
    print(SensorYearly_df.iloc[-1][0].shape[0])
    ax.legend()
    ax.set_ylim(ymax=75,ymin=-125)
    c= (dp_range.days+math.ceil(dp_range.seconds/86400))
    #plt2.xlim(0,c)
    #print('tick_inds'+str(tick_inds)+" : len="+str(len(tick_inds)))
    #print('tick_names'+str(tick_names)+" : len="+str(len(tick_names)))
    plt2.xticks(ticks=tick_inds, labels=tick_names)
    plt2.xlabel("Date")
    plt2.title(str(sensorname) + str(data_type))
    plt2.savefig(str(sensorname)+'diff.png',dpi=300)
    plt2.show()
    plt2.close()
    
    return

def yearlyPlots(Sensors):
    for s in Sensors:
        yearlyPlot(s[0],s[1])#(Sensors[0,1][s]) #This should be Sensor[s]
        
    return

        
        
def yearlyAvgPlot(AVGDF, sensorname, data_type='PM1.0_CF1_ug/m3'):
    
    def genXticks(x,dp_range,ticks): #x = array of datapoints by year, ticks = desired num of xtick labels
        
        def get_date_range(d1,d2,d_len):
            start = datetime.datetime.strptime(d1, '%m-%d')
            end = datetime.datetime.strptime(d2, '%m-%d')
            step = datetime.timedelta(days=d_len)
            date_range = []
            while start <= end:
                d1 = str(start.date())
                d = d1.replace("-", "/")
                d = d[5:] #Drop the year because it is arbitrary for the yearlyPlot
                date_range.append(d)
                start += step
            return date_range
    
        tick_len = math.floor(x.shape[0]/ticks)
        tick_len2 = x.shape[0]/ticks
        tick_inds = []
        """
        if int(x.shape[0])%ticks == 0: #If datapoints dividisble by ticks
            #ticks +=1
            print("xticks1")
        else: #Gets rounded
            #ticks -= 1
            print("xticks2")
        """
        for j in range(ticks):
            # Find Indicies
            ind = j*tick_len2
            #print(ind)
            tick_inds.append(ind/DataPerDay)
        
        num_days = dp_range.days+math.ceil(dp_range.seconds/86400) #num of days in the range rounded up
        day_len = num_days/(ticks) #how many days does each tick represent
        tick_names = get_date_range(d_range1,d_range2,day_len)
            
        #print(tick_inds)
        #print(tick_names)
            
        return tick_inds,tick_names,day_len
        
    fig, ax = plt2.subplots()
    fig.set_size_inches(7,5)
    
    first_date = AVGDF[0]['created_at'].iloc[0]
    last_date = AVGDF[0]['created_at'].iloc[-1]
    dp_range = datetime.datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S %Z') - datetime.datetime.strptime(first_date, '%Y-%m-%d %H:%M:%S %Z')
    
    for year in range(len(AVGDF)):
        first_date = AVGDF[year]['created_at'].iloc[0]
        last_date = AVGDF[year]['created_at'].iloc[-1]

        
        year_f = AVGDF[year]['created_at'].iloc[0][:4]
        print(year_f)
        data_points = AVGDF[year].shape[0]
        data_points2 = d_range_days*DataPerDay	#I believe this -1 is unnecessary. This should probably be changed in the future (See line 110)
        #start_day = SensorData[2][0]/48 #If first year doesn't read the entire range
        days = AVGDF[year].shape[0]/DataPerDay # - 1) + (SensorData[0][-1][/48)
        print("days = "+str(days), end=" ")
        
        """
        #if last datapoint of the year doesn't match the range
        if d_range2_date>datetime.datetime.strptime(AVGDF[year][0]['created_at'].iloc[-1][5:10], '%m-%d'):
            dp = len(AVGDF[year][0]['created_at'])
            x = np.linspace(dp/48, int(d_range_days), int(data_points2))"""
        
        x = np.linspace(0, int(d_range_days), int(data_points2)) #SensorData[2][year]/48
        print("len(x) = "+str(len(x)))
        [tick_inds,tick_names,day_len] = genXticks(x,dp_range,10)
        if year_f == "2020": #Make 2020 Thicker
            if int(days) != d_range_days:
                for i in range(int(int(d_range_days-days)*DataPerDay)):
                    if i == 0:
                        blank = pd.DataFrame([np.nan])
                        a = pd.concat([AVGDF[year][data_type],blank[0]])
                    else:
                        a = pd.concat([a,blank[0]])
            else:
            	a = AVGDF[year][data_type]
            	if x.shape[0] < a.shape[0]:
            		x = np.linspace(0, int(d_range_days), int(data_points2)+1)
            		print("data_points2 (x = np.linespace) is 1 value to small. Modify line 86 in plotting.py")
            	print("full year")
            ax.plot(x, a, label=sensorname+" "+str(year_f), linewidth=1.8)
        else:
            x = np.linspace(0, int(d_range_days), int(data_points)) #SensorData[2][year]/48
            ax.plot(x, AVGDF[year][data_type], label=sensorname+" "+str(year_f), linewidth=1.2)
            
    #print("year",AVGDF[-1].shape[0])
    ax.legend()
    ax.set_ylim(ymax=100,ymin=0)
    c= (dp_range.days+math.ceil(dp_range.seconds/86400))
    #plt2.xlim(0,c)
    #print('tick_inds'+str(tick_inds)+" : len="+str(len(tick_inds)))
    #print('tick_names'+str(tick_names)+" : len="+str(len(tick_names)))
    plt2.xticks(ticks=tick_inds, labels=tick_names)
    plt2.xlabel("Date")
    plt2.title(str(sensorname))
    plt2.savefig(str(sensorname)+'.png',dpi=300)
    plt2.show()
    plt2.close()  
    
    return
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
"""Plot Yearly Devs From 2020 for ONE sensor."""
#A = compute.findYearlyDevFrom2020(SensorYearly_df)    
#yearlyPlot(A,"Echo Park P1")


"""Plot Avg Yearly Devs From 2020 for ALL sensor."""
#AVGDF = compute.getAvgYearlyDevDF()
#yearlyPlot(AVGDF,"Yearly Dev From 2020")


#yearlyPlot(AVG_DF_seperated[0],"2020 devs")

#yearlyPlot(SensorYearly_df,0)