# -*- coding:utf-8 -*-

import time
import l76x
import time
import math

x=l76x.L76X()
x.L76X_Set_Baudrate(9600)

x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
time.sleep(2)
x.L76X_Set_Baudrate(115200)

x.L76X_Send_Command(x.SET_POS_FIX_400MS);

#Set output message
x.L76X_Send_Command(x.SET_NMEA_OUTPUT);

time.sleep(2)
x.L76X_Exit_BackupMode();
x.L76X_Send_Command(x.SET_SYNC_PPS_NMEA_ON)

#x.L76X_Send_Command(x.SET_STANDBY_MODE)
#time.sleep(10)
#x.L76X_Send_Command(x.SET_NORMAL_MODE)
#x.config.StandBy.value(1)
read = 0
prev_sent = 0
while(1):
    
    #check if there is something to be read
    read = x.config.read_from_nano()
    print(read)
    time.sleep(3)
    #see if nano is saying stop
    if (read) and (read.decode('utf-8') =='STOP'):
        print("Nano said stop")
        x.config.send_to_nano("STOPPING")
        
        while not 'START' in read.decode('utf-8'):
            if x.config.check_if_anything():
                read = x.config.read_from_nano()
            else:
                print("not starting")
                time.sleep(0.5)
            
    
    if (time.time() - prev_sent >= 20):
        x.L76X_Gat_GNRMC()

        data = {
            "Status" : x.Status,
            "Time_H" : x.Time_H,
            "Time_M" : x.Time_M,
            "Time_S" : x.Time_S,
            "Lon" : x.Lon,
            "Lat" : x.Lat,
            "Lon Baidu" : x.Lon_Baidu,
            "Lat Baidu" : x.Lat_Baidu,
            "Lon Google" : x.Lon_Google,
            "Lat Google" : x.Lat_Google
            }
        
        if(x.Status == 1):
            print ('Already positioned')
        else:
            print ('No positioning')
        
        x.config.send_to_nano(data)
        prev_sent = time.time()

