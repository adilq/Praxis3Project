
import busio
import board
import digitalio
import time
import mqtt_publish
import DataPacket

#establish UART btwn Pico/GPS and Nano
uart = busio.UART(board.TX, board.RX)

#set up LEDs
onboard_led = digitalio.DigitalInOut(board.LED)
onboard_led.direction = digitalio.Direction.OUTPUT
green_led = digitalio.DigitalInOut(board.D2)
green_led.direction = digitalio.Direction.OUTPUT

#set up button
button = digitalio.DigitalInOut(board.D3)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

#establish connection with mqtt broker
connection = mqtt_publish.Connection() #this is an object (see mqtt_publish.py)

#list of data packet objects
push = []
lastState = True

def check_button_state(state, lastState):
    '''check the state of the button'''
    was_pressed = False
    if (state != lastState) and (state == False):
        #the button has been pressed
        while button.value == False:
            pass
        was_pressed = True
    lastState = state
    return was_pressed

#main loop
while True:
    data = uart.read()  # read up to 32 bytes
    button_state = button.value
    was_pressed = check_button_state(button_state, lastState)
    # print(data)  # this is a bytearray type

    if data is not None:
        onboard_led.value = True
        #make a new DataPacket object; append it to list
        pack = DataPacket.Packet(data)
        pack.convert()
        push.append(pack)
        print(pack.data)
        onboard_led.value = False
    else:
        green_led.value = True

    #sending data over wifi
    if was_pressed:
        green_led.value = False
        for packet in push:
            if not packet.sent:
                onboard_led.value = not onboard_led.value #flash the led
                msg = str(packet.data)
                connection.mqtt_client.publish(connection.mqtt_topic, msg)
                packet.update_sent()
        onboard_led.value = False
