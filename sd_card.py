import os
import board
import busio
import digitalio
import adafruit_sdcard
import storage
import time

# Setup Spi pins
SD_CS = board.GP13
spi = busio.SPI(board.GP10, board.GP11, board.GP12)
cs = digitalio.DigitalInOut(SD_CS)

# Connect to card and mount filesytem
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)

# Define path to write data to on CircuitPython filesystem (Our files are under /sd)
storage.mount(vfs, "/sd")

# Setup internal LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# Helper function to print contents of SD
def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

# Print all files on filesystem
print("Files on filesystem:")
print("====================")
print_directory("/sd")

# Write GPS data
print("Logging GPS data to filesystem")
'''
# Create GPS file
with open("/sd/GPS.txt", "w") as f:
    f.write("Coordinates:\n")

# Append to GPS file
while True:
    # open file for append
    with open("/sd/GPS.txt", "a") as f:
        led.value = True  # turn on LED to indicate we're writing to the file
        gps = #insert gps value
        print("Coordinates: " % gps) #format gps value
        f.write("%" % gps)
        led.value = False  # turn off LED to indicate we're done
    # file is saved
    time.sleep(1)
'''
'''
# Write new data to file (erase and write new data)
with open("/sd/test.txt", "w") as f:
    f.write("Hello world!\r\n")

# Append new data to file (does not erase old data)
with open("/sd/test.txt", "a") as f:
    f.write("This is another line!\r\n")

# Read all lines in file
with open("/sd/test.txt", "r") as f:
    print("Printing lines in file:")
    line = f.readline()
    while line != '':
        print(line)
        line = f.readline()

# Another way to read all lines in file
with open("/sd/test.txt", "r") as f:
    lines = f.readlines()
    print("Printing lines in file:")
    for line in lines:
        print(line)
'''


