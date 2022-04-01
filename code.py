import busio
import board
import digitalio
import time

uart = busio.UART(board.TX, board.RX)
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
while True:
    data = uart.read()  # read up to 32 bytes
    # print(data)  # this is a bytearray type

    if data is not None:
        led.value = True
        # convert bytearray to string
        data_string = ''.join([chr(b) for b in data])

        #turn back into dictionary
        data_dict = dict(subString.strip("{} '").split(":") for subString in data_string.split(","))

        #format everything in the dictionary properly
        for key in data_dict.keys():
            new_key = key.strip("{} '")
            data_dict[new_key] = float(data_dict.pop(key))
        print(data_dict)
        led.value = False
    else:
        led.value = True
        time.sleep(0.1)
        led.value = False
        time.sleep(0.1)
