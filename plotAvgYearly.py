#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prints a plot of the yearly average amongst all sensors in a localized area.
"""

import better_file_reading
import compute
import plotting

[d_range1,d_range2,d_range_days,DataPerDay] = better_file_reading.get_date_ranges()
col_names = ['created_at','PM1.0_CF1_ug/m3','PM2.5_CF1_ug/m3','PM10.0_CF1_ug/m3','UptimeMinutes','RSSI_dbm','Temperature_F','Humidity_%','PM2.5_ATM_ug/m3']



#Thirty Min
#AVGDF = compute.getAvgYearlyDevDF([['661 Dimmick Dr. Outside','661 Dimmick Dr. Outside (outside) (34.105414 -118.211069) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['2857 W. 7th Street','2857 W. 7th Street (outside) (34.059919 -118.287979) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['AQMD_CELA','AQMD_CELA (outside) (34.066423 -118.226591) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['AQMD_NASA_29','AQMD_NASA_29 (outside) (34.076629 -118.222371) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['AQMD_NASA_34','AQMD_NASA_34 (outside) (34.111188 -118.21065) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['Bancroft Near Hidalgo','Bancroft Near Hidalgo (outside) (34.097363 -118.257627) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA 27th & Brighton','CCA 27th & Brighton (outside) (34.030904 -118.301509) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA Alma and 1st','CCA Alma and 1st (outside) (34.035696 -118.191404) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA Jeffries','CCA Jeffries (outside) (34.085236 -118.223757) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA Loma Vista & Alessandro ','CCA Loma Vista & Alessandro  (outside) (34.09488 -118.254657) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA Oros','CCA Oros (undefined) (34.085791 -118.229687) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA Pepper','CCA Pepper (outside) (34.089558 -118.226068) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA Rowena & Auburn','CCA Rowena & Auburn (outside) (34.107859 -118.265826) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['CCA_36th&Normandie','CCA_36th&Normandie (outside) (34.02279 -118.300264) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['Echo Park P1','Echo Park P1 (undefined) (34.073635 -118.268681) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['Edendale','Edendale (outside) (34.110663 -118.271735) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['Huntington','Huntington (outside) (34.082874 -118.189514) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['Mt. Washington School','Mt. Washington School (outside) (34.105557 -118.215239) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['SCAP_53','SCAP_53 (outside) (34.057421 -118.173696) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['USCEHC El Paso Dr. ','USCEHC El Paso Dr.  (outside) (34.11759 -118.21734) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['USCEHC Lincoln Heights','USCEHC Lincoln Heights (undefined) (34.068458 -118.206389) Primary 30_minute_average 08_01_2016 05_20_2020.csv']])

#Debug
#AVGDF = compute.getAvgYearlyDevDF([['Echo Park P1','Echo Park P1 (undefined) (34.073635 -118.268681) Primary 30_minute_average 08_01_2016 05_20_2020.csv'],['USCEHC Lincoln Heights','USCEHC Lincoln Heights (undefined) (34.068458 -118.206389) Primary 30_minute_average 08_01_2016 05_20_2020.csv']])

#Daily Avg
AVGDF = compute.getAvgYearlyDevDF([['661 Dimmick Dr. Outside','661 Dimmick Dr. Outside (outside) (34.105414 -118.211069) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['2857 W. 7th Street','2857 W. 7th Street (outside) (34.059919 -118.287979) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['AQMD_CELA','AQMD_CELA (outside) (34.066423 -118.226591) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['AQMD_NASA_29','AQMD_NASA_29 (outside) (34.076629 -118.222371) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['AQMD_NASA_34','AQMD_NASA_34 (outside) (34.111188 -118.21065) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['Bancroft Near Hidalgo','Bancroft Near Hidalgo (outside) (34.097363 -118.257627) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['CCA 27th & Brighton','CCA 27th & Brighton (outside) (34.030904 -118.301509) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['CCA Alma and 1st','CCA Alma and 1st (outside) (34.035696 -118.191404) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['CCA Loma Vista & Alessandro ','CCA Loma Vista & Alessandro  (outside) (34.09488 -118.254657) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['CCA Oros','CCA Oros (undefined) (34.085791 -118.229687) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['CCA Pepper','CCA Pepper (outside) (34.089558 -118.226068) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['CCA Rowena & Auburn','CCA Rowena & Auburn (outside) (34.107859 -118.265826) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['CCA_36th&Normandie','CCA_36th&Normandie (outside) (34.02279 -118.300264) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['Echo Park P1','Echo Park P1 (undefined) (34.073635 -118.268681) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['Edendale','Edendale (outside) (34.110663 -118.271735) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['Huntington','Huntington (outside) (34.082874 -118.189514) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['Mt. Washington School','Mt. Washington School (outside) (34.105557 -118.215239) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['SCAP_53','SCAP_53 (outside) (34.057421 -118.173696) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['USCEHC El Paso Dr. ','USCEHC El Paso Dr.  (outside) (34.11759 -118.21734) Primary 1440_minute_average 08_01_2016 05_28_2020.csv'],['USCEHC Lincoln Heights','USCEHC Lincoln Heights (undefined) (34.068458 -118.206389) Primary 1440_minute_average 08_01_2016 05_28_2020.csv']],False)




#AVGDF needs to be seperated into yearly DF
AVGDF_sep = better_file_reading.seperateByYear(AVGDF, AVGDF, "01-01", "05-21")
AVGDF = AVGDF_sep[0]


for data_type in ['PM1.0_CF1_ug/m3','PM2.5_CF1_ug/m3','PM10.0_CF1_ug/m3','Temperature_F']:
	if data_type == 'PM1.0_CF1_ug/m3':
		data_type_name = 'PM1.0'
	if data_type == 'PM2.5_CF1_ug/m3':
		data_type_name = 'PM2.5'
	if data_type == 'PM10.0_CF1_ug/m3':
		data_type_name = 'PM10'
	if data_type == 'Temperature_F':
		data_type_name = 'Temp (F)'
	plotting.yearlyAvgPlot(AVGDF, "Average Yearly Dev From 2020 "+data_type_name, data_type)
