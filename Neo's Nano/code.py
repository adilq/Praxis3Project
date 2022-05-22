import busio
import board
import digitalio
import time
import mqtt_publish
import DataPacket

#establish UART btwn Pico/GPS and Nano
uart = busio.UART(board.TX, board.RX)

connection = mqtt_publish.Connection() #this is an object (see mqtt_publish.py)

#set up LEDs
onboard_led = digitalio.DigitalInOut(board.LED)
onboard_led.direction = digitalio.Direction.OUTPUT
green_led = digitalio.DigitalInOut(board.D2)
green_led.direction = digitalio.Direction.OUTPUT

#set up button
button = digitalio.DigitalInOut(board.D3)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

#list of data packet objects
push = []

def check_button_state(state):
    '''#check the state of the button
    '''

    was_pressed = False
    if (state == False):
        #the button has been pressed
        for i in range(0, 10):
            green_led.value = not green_led.value
            time.sleep(0.15)

        while button.value == False:
            print('I am pressed')
            time.sleep(0.5)
        print('no longer pressed')
        was_pressed = True
    return was_pressed

#flash both rapidly unitl button is pressed
def flash_leds():
    while check_button_state(button.value) == False:
        green_led.value = not green_led.value
        onboard_led.value = not onboard_led.value
        time.sleep(0.05)
    return

#main loop
while True:
    data = uart.read()  #read data from Pico
    button_state = button.value
    was_pressed = check_button_state(button_state)

    if data != b'\x00' and data is not None:
        onboard_led.value = True
        #make a new DataPacket object and convert back to dictionary
        pack = DataPacket.Packet(data)
        pack.convert()

        #if there is a position, append data to list. If its the first time, flash both LEDs so that we can see
        if (pack.data["Status"] == 1) and (len(push) == 0):
            #flash_leds()
            push.append(pack)
        elif (pack.data["Status"] == 1):
            push.append(pack)

        print(pack.data)
        onboard_led.value = False
    else:
        green_led.value = not green_led.value

    #sending data over wifi
    if was_pressed:
        #establish connection with mqtt broker
        #connection = mqtt_publish.Connection() #this is an object (see mqtt_publish.py)
        onboard_led.value = True
        green_led.value = False
        time.sleep(0.05)
        onboard_led.value = False
        green_led.value = True
        time.sleep(0.05)
        green_led.value = False
        for packet in push:
            if not packet.sent:
                onboard_led.value = not onboard_led.value #flash the led
                msg = str(packet.data)
                packet.update_sent()
        onboard_led.value = False
