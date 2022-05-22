# -*- coding:utf-8 -*-

import time
import l76x
import time
import math

TRACKER_ID = 1
POLLING_PERIOD = int(60 * 0.25)  # TODO: Change me to something reasonable

x = l76x.L76X()
x.L76X_Set_Baudrate(9600)

x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
time.sleep(2)
x.L76X_Set_Baudrate(115200)

x.L76X_Send_Command(x.SET_POS_FIX_400MS)

# Set output message
x.L76X_Send_Command(x.SET_NMEA_OUTPUT)

time.sleep(2)
x.L76X_Exit_BackupMode()
x.L76X_Send_Command(x.SET_SYNC_PPS_NMEA_ON)

# x.L76X_Send_Command(x.SET_STANDBY_MODE)
# time.sleep(10)
# x.L76X_Send_Command(x.SET_NORMAL_MODE)
# x.config.StandBy.value(1)
read = 0
prev_sent = 0
while(1):

    # check if there is something to be read
    read = x.config.read_from_nano()
    print(read)
    time.sleep(3)
    # see if nano is saying stop
    if (read) and (read.decode('utf-8') == 'STOP'):
        print("Nano said stop")
        x.config.send_to_nano("STOPPING")

        while not 'START' in read.decode('utf-8'):
            if x.config.check_if_anything():
                read = x.config.read_from_nano()
            else:
                print("not starting")
                time.sleep(0.5)

    #send data to nano
    if (time.time() - prev_sent >= POLLING_PERIOD):
        x.L76X_Gat_GNRMC()

        data = {
            "id": TRACKER_ID,
            "status": x.Status,
            "lon": x.Lon,
            "lat": x.Lat,
        }

        if(x.Status == 1):
            print('Already positioned')
        else:
            print('No positioning')

        # TODO: Adil: add button handler to post this entire thing
        x.config.send_to_nano(data)
        prev_sent = time.time()
